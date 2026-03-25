# 📬 College Complaint Box

Full-stack complaint management system for colleges.
Stack: Python Flask · PostgreSQL (Supabase) · Vanilla JS · Deployed on Vercel

---

## 📁 Project Structure

```
college-complaint-box/
│
├── app.py                ← Main Flask app + database connection (START HERE)
├── requirements.txt      ← Python dependencies
├── vercel.json           ← Vercel routing config
├── .env.example          ← Template for your secrets
├── .gitignore
│
├── templates/
│   ├── index.html        ← Student complaint form
│   └── admin.html        ← Admin dashboard
│
└── static/
    ├── css/
    │   ├── style.css
    │   └── admin.css
    └── js/
        ├── main.js
        └── admin.js
```

---

## Step 1 — Set Up Supabase (Free Database)

1. Go to https://supabase.com → Sign up → New Project
2. Set a strong database password (save it!), pick a region, wait ~2 min
3. Go to: Settings → Database → Connection string → URI tab
4. Copy the URI:
   postgresql://postgres:[YOUR-PASSWORD]@db.abcdefgh.supabase.co:5432/postgres
5. Replace [YOUR-PASSWORD] with your actual password

That is your DATABASE_URL. Use it in the steps below.
The app creates the complaints table automatically on first run.

---

## Step 2 — Run Locally

  python -m venv venv
  source venv/bin/activate        # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  cp .env.example .env
  # Edit .env and paste your DATABASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD
  python app.py

  Student form:  http://localhost:5000
  Admin panel:   http://localhost:5000/admin

---

## Step 3 — Deploy to Vercel

OPTION A — Dashboard (easiest)

1. Push project to GitHub
2. Go to https://vercel.com → Add New Project → Import your repo
3. Before deploying, add Environment Variables:
     DATABASE_URL    = postgresql://postgres:... (your Supabase URI)
     ADMIN_USERNAME  = admin
     ADMIN_PASSWORD  = your_strong_password
4. Click Deploy

OPTION B — CLI

  npm install -g vercel
  vercel login
  vercel                          # follow prompts
  vercel env add DATABASE_URL
  vercel env add ADMIN_USERNAME
  vercel env add ADMIN_PASSWORD
  vercel --prod

---

## API Endpoints

  POST   /submit_complaint      public   Submit a complaint
  POST   /complaints            admin    List/filter complaints
  PUT    /resolve/<id>          admin    Toggle resolved/pending
  DELETE /delete/<id>           admin    Delete a complaint
  POST   /admin/login           public   Verify admin credentials

Admin routes require { "username": "...", "password": "..." } in JSON body.
