# utils/log_utils.py

import psycopg2
from datetime import datetime

DB_NAME     = "ml_api_db"
DB_USER     = "postgres"
DB_PASSWORD = "0611"
DB_HOST     = "localhost"
DB_PORT     = "5432"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def log_event(level: str, event: str):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO logs (level, event, created_at) VALUES (%s, %s, NOW())",
                (level, event)
            )
            conn.commit()
    except Exception as e:
        print(f"Не удалось записать в логи: {e}")
    finally:
        if conn:
            conn.close()
