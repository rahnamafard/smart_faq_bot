from bot.database import insert_log

def log_question_and_feedback(user_id: int, question: str, answer: str, feedback: int = None) -> None:
    insert_log(user_id, question, answer, feedback)

def log_feedback(user_id: int, question: str, rating: int) -> None:
    # Logic to log feedback in the database
    insert_log(user_id, question, rating)
