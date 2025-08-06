# utils/db_utils.py

import psycopg2
from psycopg2.extras import RealDictCursor
from .log_utils import log_event

DB_NAME     = "ml_api_db"
DB_USER     = "postgres"
DB_PASSWORD = "0611"
DB_HOST     = "localhost"
DB_PORT     = "5432"

def get_db_connection():
    """Возвращает соединение с БД."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def set_task_status(task_id: str, status_str: str, info: str = None, error_code: str = None):
    """
    Создаёт или обновляет запись в таблице tasks:
      - task_id       TEXT PRIMARY KEY
      - status        TEXT          (processing/completed/error)
      - info          TEXT          (CSV‐строка меток или текст ошибки)
      - error_code    TEXT          (NULL или "404"/"500"/"503" и т. д.)
      - updated_at    TIMESTAMP     (NOW())
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (task_id, status, info, error_code, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (task_id)
                DO UPDATE SET
                  status     = EXCLUDED.status,
                  info       = EXCLUDED.info,
                  error_code = EXCLUDED.error_code,
                  updated_at = NOW()
                """,
                (task_id, status_str, info, error_code)
            )
            conn.commit()
    except Exception as e:
        log_event("ERROR", f"set_task_status({task_id}) failed: {e}")
    finally:
        if conn:
            conn.close()

def get_task_status(task_id: str) -> dict:
    """
    Возвращает:
      {
        "task_id": ..., 
        "status": "processing"|"completed"|"error"|"not_found",
        "error_code": <строка или None>
      }
    Если не найдено — status="not_found", error_code=None.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT status, error_code FROM tasks WHERE task_id = %s",
                (task_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "task_id": task_id,
                    "status": row["status"],
                    "error_code": row.get("error_code")
                }
            else:
                return {
                    "task_id": task_id,
                    "status": "not_found",
                    "error_code": None
                }
    except Exception as e:
        log_event("ERROR", f"get_task_status({task_id}) failed: {e}")
        return {
            "task_id": task_id,
            "status": "error",
            "error_code": "500"
        }
    finally:
        if conn:
            conn.close()

def get_task_record(task_id: str) -> dict | None:
    """
    Возвращает всю запись из tasks:
      {
        "status": ...,
        "info": ...,
        "error_code": ...
      }
    Если не найдено — возвращает None.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT status, info, error_code FROM tasks WHERE task_id = %s",
                (task_id,)
            )
            # print(cur.fetchone())
            return cur.fetchone()  # None, если не найдено
    except Exception as e:
        log_event("ERROR", f"get_task_record({task_id}) failed: {e}")
        return None
    finally:
        if conn:
            conn.close()

def any_task_processing() -> bool:
    """
    Возвращает True, если хотя бы одна запись в tasks имеет status='processing'.
    Если при проверке произошла ошибка, тоже возвращаем True, чтобы отказать клиенту.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'processing'")
            count = cur.fetchone()[0]
            return count > 0
    except Exception as e:
        log_event("ERROR", f"any_task_processing failed: {e}")
        return True
    finally:
        if conn:
            conn.close()
