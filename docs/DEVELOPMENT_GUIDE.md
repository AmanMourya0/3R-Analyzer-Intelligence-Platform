# Local Development Guide

## Prerequisites
* Python 3.11+
* Node.js 18+
* PostgreSQL 14+

## Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # (Windows)
# source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
```

Set up your `.env` file referencing `.env.example`.

Run Migrations:
```bash
alembic upgrade head
```

Start Server:
```bash
uvicorn app.main:app --reload
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
