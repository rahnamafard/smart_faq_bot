import psycopg2
import config
import logging

logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

def insert_log(user_id: int, question: str, answer: str, feedback: int = None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (user_id, question, answer, feedback) VALUES (%s, %s, %s, %s)",
        (user_id, question, answer, feedback)
    )
    conn.commit()
    cursor.close()
    conn.close()

def insert_knowledge(question: str, answer: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO knowledge_base (question, answer) VALUES (%s, %s)",
        (question, answer)
    )
    conn.commit()
    cursor.close()
    conn.close()

def remove_knowledge(question: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM knowledge_base WHERE question = %s",
        (question,)
    )
    conn.commit()
    rows_deleted = cursor.rowcount
    cursor.close()
    conn.close()
    return rows_deleted > 0

def get_all_knowledge() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM knowledge_base")
    rows = cursor.fetchall()
    logger.info("Fetched knowledge base entries: %s", rows)
    cursor.close()
    conn.close()
    return rows
