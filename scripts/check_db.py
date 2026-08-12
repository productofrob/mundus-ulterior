"""Verify Postgres is reachable and the pgvector extension is installed."""
import os
import psycopg

url = os.environ.get("APP_DATABASE_URL", "postgresql://mundus:mundus@localhost:5432/mundus")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        row = cur.fetchone()
        print("pgvector installed:" , bool(row))
        cur.execute("SELECT version();")
        print(cur.fetchone()[0])
