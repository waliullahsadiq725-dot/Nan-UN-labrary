# NUDL Backend — Fresh Repository

FastAPI backend for Nangarhar University Digital Library.

## Included
- Student and teacher registration (accounts require administrator approval)
- Login with signed bearer tokens
- Admin approval/disable for users
- PDF upload with file-signature validation
- Admin approval/rejection of uploaded documents
- Public approved-document listing, search and PDF download
- Categories, favorites and dashboard statistics
- First administrator can be bootstrapped from environment variables

## Run locally
1. Install Python 3.12.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and change `SECRET_KEY` and admin password.
5. Run: `uvicorn app.main:app --reload`
6. Open `/docs`.

The app reads environment variables directly; `.env` is an example file and is not automatically loaded. Set variables in your shell or hosting dashboard.

## Deploy to Render
1. Create a new **Web Service** from this repository.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set `SECRET_KEY`, `ADMIN_NAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `DATABASE_URL`, and `UPLOAD_DIR`.
5. Included `render.yaml` uses temporary `/tmp` storage so it can deploy on the free web-service plan. On the free plan, the database and uploaded PDFs are temporary and can be lost when the service restarts or redeploys. For permanent storage, use a paid persistent disk or managed database/object storage.

## Important
- This repository deliberately avoids PostgreSQL drivers and optional extras to reduce build failures. It uses SQLite by default.
- For a production multi-instance deployment, migrate to managed PostgreSQL and object storage.
- Never commit `.env` or real passwords to GitHub.
- The default administrator is created only when `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set and no account with that email exists. Change the sample credentials immediately.
