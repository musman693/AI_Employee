# AI CRM & Sales Management Backend

## Quick start

From the repository root:

```bash
cd AI_Employee/module2-crm-sales
copy .env.example .env
python -m pip install -r requirements.txt
python run.py
```

Then open http://127.0.0.1:8000/docs

## Notes
- The module uses a local SQLite database by default so it runs without Docker/Postgres initially.
- If you want Docker later, install Docker Desktop and use `docker compose up --build`.
