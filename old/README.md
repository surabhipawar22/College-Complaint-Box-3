# 📬 College Complaint Box

A full-stack web application for anonymous college complaint management.  
**Stack:** Flask · PostgreSQL (Supabase) · Vanilla JS · Vercel

---

## 📁 File Structure

```
college-complaint-box/
├── api/
│   └── index.py          ← Flask app (Vercel serverless entry point)
├── static/
│   ├── css/
│   │   ├── style.css     ← Shared styles
│   │   └── admin.css     ← Admin panel styles
│   └── js/
│       ├── main.js       ← Student form logic
│       └── admin.js      ← Admin panel logic
├── templates/
│   ├── index.html        ← Student complaint form
│   └── admin.html        ← Admin dashboard
├── .env.example          ← Environment variable template
├── .gitignore
├── requirements.txt
├── vercel.json           ← Vercel deployment config
└── README.md
```

---

## 🗄️ Database Schema

```sql
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
```

The app runs `CREATE TABLE IF NOT EXISTS` on startup — you don't need to run this manually.

---

## 🔧 Supabase Setup

### 1 — Create a Supabase project
1. Go to [https://supabase.com](https://supabase.com) → **New Project**
2. Choose a name, set a strong database password, pick a region near your users
3. Wait ~2 minutes for the project to provision

### 2 — Get the connection string
1. In your project dashboard, go to **Settings → Database**
2. Scroll to **Connection string** → select **URI** tab
3. Copy the string — it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
4. Replace `[YOUR-PASSWORD]` with the password you set

### 3 — Set environment variable
Paste this string as `DATABASE_URL` in your `.env` file (local) and Vercel dashboard (production).

---

## 💻 Local Development

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/college-complaint-box.git
cd college-complaint-box

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and fill in your DATABASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD

# 5. Run the app
python api/index.py
```

Visit:
- Student form: http://localhost:5000
- Admin panel:  http://localhost:5000/admin  (default: admin / admin123)

> For local dev, make sure to load the `.env` file. Add this to the top of `api/index.py` during development:
> ```python
> from dotenv import load_dotenv
> load_dotenv()
> ```

---

## 🚀 Deployment on Vercel

### Prerequisites
- [Vercel CLI](https://vercel.com/docs/cli): `npm install -g vercel`
- A GitHub account (optional but recommended)

### Steps

#### Option A — CLI deploy

```bash
# 1. Log in to Vercel
vercel login

# 2. From the project root, run:
vercel

# 3. Answer the prompts:
#    - Set up and deploy: Y
#    - Which scope: (your account)
#    - Link to existing project: N
#    - Project name: college-complaint-box
#    - Directory: ./
#    - Override settings: N

# 4. Set environment variables on Vercel:
vercel env add DATABASE_URL
vercel env add ADMIN_USERNAME
vercel env add ADMIN_PASSWORD

# 5. Redeploy with env vars:
vercel --prod
```

#### Option B — GitHub + Vercel dashboard

1. Push your code to GitHub
2. Go to [https://vercel.com/new](https://vercel.com/new)
3. Import your GitHub repository
4. In **Environment Variables**, add:
   - `DATABASE_URL` → your Supabase connection string
   - `ADMIN_USERNAME` → e.g. `admin`
   - `ADMIN_PASSWORD` → a strong password
5. Click **Deploy**

### How it works on Vercel
- `vercel.json` routes all API paths to `api/index.py` (Python serverless function)
- Static files are served directly from `static/`
- HTML templates are served by Flask from `templates/`

---

## 🔐 API Reference

| Method | Endpoint               | Auth Required | Description                        |
|--------|------------------------|---------------|------------------------------------|
| POST   | `/submit_complaint`    | No            | Submit a new complaint             |
| POST   | `/complaints`          | Yes (body)    | Get all / filtered complaints      |
| PUT    | `/resolve/<id>`        | Yes (body)    | Toggle complaint status            |
| DELETE | `/delete/<id>`         | Yes (body)    | Delete a complaint                 |
| POST   | `/admin/login`         | No            | Verify admin credentials           |

**Auth format** (JSON body for protected routes):
```json
{ "username": "admin", "password": "your_password" }
```

---

## 🛡️ Security Notes

- All database queries use parameterised `%s` placeholders (psycopg2) — SQL injection is prevented
- Admin credentials are stored in environment variables, never hardcoded
- Passwords are never stored in localStorage or sent to the frontend
- Form inputs are sanitised with HTML escaping on the frontend
- CORS is enabled for development; restrict `origins` in production if needed

---

## 🎨 Customisation

- **Add departments** → edit the `<select>` in `templates/index.html`
- **Change admin credentials** → update `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars
- **Change theme colours** → edit the CSS variables at the top of `static/css/style.css`
- **Add email notifications** → hook into `submit_complaint` route in `api/index.py`
