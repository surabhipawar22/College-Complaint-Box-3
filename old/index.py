import os
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import hashlib

app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app)

# ── Database connection ────────────────────────────────────────────────────────

def get_db():
    """Return a new psycopg2 connection using DATABASE_URL from env."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


def init_db():
    """Create the complaints table if it doesn't exist."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id          SERIAL PRIMARY KEY,
            name        VARCHAR(120),
            email       VARCHAR(254),
            department  VARCHAR(100) NOT NULL,
            title       VARCHAR(200) NOT NULL,
            description TEXT        NOT NULL,
            status      VARCHAR(20)  NOT NULL DEFAULT 'pending',
            created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


# Initialise on cold start (safe to call repeatedly – CREATE TABLE IF NOT EXISTS)
try:
    init_db()
except Exception as e:
    print(f"[WARN] DB init skipped: {e}")

# ── Auth helpers ───────────────────────────────────────────────────────────────

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


def check_admin(data: dict) -> bool:
    return (
        data.get("username") == ADMIN_USERNAME
        and data.get("password") == ADMIN_PASSWORD
    )

# ── Static page routes ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("../templates", "index.html")


@app.route("/admin")
def admin():
    return send_from_directory("../templates", "admin.html")

# ── API: submit complaint ──────────────────────────────────────────────────────

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    data = request.get_json(silent=True) or {}

    department   = (data.get("department")   or "").strip()
    title        = (data.get("title")        or "").strip()
    description  = (data.get("description")  or "").strip()
    is_anonymous = data.get("anonymous", False)
    name         = None if is_anonymous else (data.get("name")  or "").strip() or None
    email        = None if is_anonymous else (data.get("email") or "").strip() or None

    # Validation
    if not department:
        return jsonify({"error": "Department is required."}), 400
    if not title:
        return jsonify({"error": "Complaint title is required."}), 400
    if not description:
        return jsonify({"error": "Description is required."}), 400
    if len(title) > 200:
        return jsonify({"error": "Title must be 200 characters or fewer."}), 400
    if len(description) > 5000:
        return jsonify({"error": "Description must be 5 000 characters or fewer."}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO complaints (name, email, department, title, description, status, created_at)
        VALUES (%s, %s, %s, %s, %s, 'pending', NOW())
        RETURNING id, created_at;
        """,
        (name, email, department, title, description),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Complaint submitted successfully.",
        "id": row["id"],
        "created_at": row["created_at"].isoformat(),
    }), 201

# ── API: get complaints (admin only) ──────────────────────────────────────────

@app.route("/complaints", methods=["POST"])
def get_complaints():
    data = request.get_json(silent=True) or {}
    if not check_admin(data):
        return jsonify({"error": "Unauthorized."}), 401

    department = (data.get("department") or "").strip()
    status     = (data.get("status")     or "").strip()

    conn = get_db()
    cur = conn.cursor()

    query  = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if department:
        query += " AND department = %s"
        params.append(department)
    if status:
        query += " AND status = %s"
        params.append(status)

    query += " ORDER BY created_at DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    complaints = []
    for r in rows:
        c = dict(r)
        if c.get("created_at"):
            c["created_at"] = c["created_at"].isoformat()
        complaints.append(c)

    return jsonify({"complaints": complaints}), 200

# ── API: resolve / unresolve ───────────────────────────────────────────────────

@app.route("/resolve/<int:complaint_id>", methods=["PUT"])
def resolve_complaint(complaint_id):
    data = request.get_json(silent=True) or {}
    if not check_admin(data):
        return jsonify({"error": "Unauthorized."}), 401

    new_status = data.get("status", "resolved")
    if new_status not in ("pending", "resolved"):
        return jsonify({"error": "Status must be 'pending' or 'resolved'."}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE complaints SET status = %s WHERE id = %s RETURNING id;",
        (new_status, complaint_id),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "Complaint not found."}), 404

    return jsonify({"message": f"Complaint #{complaint_id} marked as {new_status}."}), 200

# ── API: delete complaint ──────────────────────────────────────────────────────

@app.route("/delete/<int:complaint_id>", methods=["DELETE"])
def delete_complaint(complaint_id):
    data = request.get_json(silent=True) or {}
    if not check_admin(data):
        return jsonify({"error": "Unauthorized."}), 401

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM complaints WHERE id = %s RETURNING id;", (complaint_id,))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "Complaint not found."}), 404

    return jsonify({"message": f"Complaint #{complaint_id} deleted."}), 200

# ── API: admin login check ─────────────────────────────────────────────────────

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    if check_admin(data):
        return jsonify({"message": "Login successful."}), 200
    return jsonify({"error": "Invalid credentials."}), 401

# ── Entry point for local dev ──────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
