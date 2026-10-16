# Deployment and integration notes

1) Overview
- app_prod.py is a production-oriented Flask app using SQLAlchemy.
- It supports DATABASE_URL environment variable (Postgres or SQLite). For quick start the default uses SQLite at data/library.db.
- Nonce/challenge endpoints: /api/nonce to request nonce, /api/nonce/verify to mark used. /api/scan expects a server-side nonce and a descriptor payload so the server can verify.
- Dev-only endpoints are protected by X-Dev-Key header or dev_key param.

2) Quick local test with Docker
- Build: docker-compose build
- Run: docker-compose up
- Open: http://localhost:5000

3) Deploy to Railway / Render / Fly
- Create a new project and connect to your GitHub repo.
- Set environment variables (DEV_KEY, DATABASE_URL for Postgres if you prefer, API_ORIGINS to your GitHub Pages domain)
- For Railway/Render: use Dockerfile or the standard Python deployment; Gunicorn will be used in Dockerfile/Procfile.

4) Integrate frontend (docs/index.html)
- In the client (docs/index.html) set the API base URL e.g. const API = 'https://your-backend.example.com';
- Frontend should request a nonce before starting a liveness-challenge and include the nonce in the /api/scan payload.

5) Security notes
- Always change DEV_KEY before going live. Store secret as environment variable on the host (Railway/Render/Fly/DO App Platform).
- Prefer PostgreSQL for multi-instance reliability. If using SQLite, mount a persistent volume.
- Ensure API_ORIGINS is set to the exact origin(s) of your frontend to limit CORS.
- Server-side descriptor matching uses euclidean distance threshold (0.6) — tune based on your dataset.

6) Backup
- If using SQLite you can call /api/backup-db to download database copy. For Postgres, use pg_dump.

