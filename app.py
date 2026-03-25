import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor



app = Flask(__name__)
app.secret_key = "super_secret_key_change_this" # Important for sessions


# Load .env locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
CORS(app)

# Config
DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

def get_db_connection():
    url = DATABASE_URL
    if "sslmode" not in url:
        url += "&sslmode=require" if "?" in url else "?sslmode=require"
    return psycopg2.connect(url)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id SERIAL PRIMARY KEY,
                name VARCHAR(120),
                email VARCHAR(254),
                department VARCHAR(100) NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

with app.app_context():
    init_db()

# ─── PAGE ROUTES ───────────────────────────────────

@app.route("/")
def landing():
    return render_template("index.html") # The Reception/Landing Page

@app.route("/submit")
def submit_page():
    return render_template("submit.html") # The actual Form

@app.route("/track")
def track_page():
    return render_template("track.html") # Status Check Page

@app.route("/admin")
def admin_page():
    if not session.get("is_admin"):
        return redirect(url_for("login_page")) # Redirect to login if not authenticated
    return render_template("admin.html")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if data.get("username") == ADMIN_USERNAME and data.get("password") == ADMIN_PASSWORD:
        session["is_admin"] = True # Set session variable
        return jsonify({"message": "OK"}), 200
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


# ─── API ROUTES ────────────────────────────────────

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    try:
        data = request.get_json()
        is_anon = data.get("anonymous", False)
        name = None if is_anon else data.get("name")
        email = None if is_anon else data.get("email")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "INSERT INTO complaints (name, email, department, title, description) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (name, email, data.get("department"), data.get("title"), data.get("description"))
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Success", "id": result['id']}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/track/<int:complaint_id>", methods=["GET"])
def track_complaint(complaint_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, title, status, created_at FROM complaints WHERE id = %s", (complaint_id,))
        result = cur.fetchone()
        conn.close()
        return jsonify(result) if result else (jsonify({"error": "Not found"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── ADMIN API ROUTES ──────────────────────────────

def check_admin(data):
    return data.get("username") == ADMIN_USERNAME and data.get("password") == ADMIN_PASSWORD

@app.route("/complaints", methods=["POST"])
def get_complaints():
    data = request.get_json() or {}
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM complaints ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"complaints": rows})

@app.route("/resolve/<int:complaint_id>", methods=["PUT"])
def resolve_complaint(complaint_id):
    data = request.get_json() or {}
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE complaints SET status = %s WHERE id = %s", (data.get("status", "resolved"), complaint_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

@app.route("/delete/<int:complaint_id>", methods=["DELETE"])
def delete_complaint(complaint_id):
    data = request.get_json() or {}
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

if __name__ == "__main__":
    app.run(debug=True)