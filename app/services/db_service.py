import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

def insert_resume(resume_json: dict):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO resumes(data) VALUES (%s) RETURNING id",
            (str(resume_json),)
        )
        conn.commit()
        return cur.fetchone()[0]