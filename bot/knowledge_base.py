import requests
import logging
import numpy as np
from transformers import AutoTokenizer, AutoModel
from bot.database import insert_knowledge, remove_knowledge, get_all_knowledge, get_connection
from sklearn.metrics.pairwise import cosine_similarity
from bot.utils import get_embedding

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the BERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("HooshvareLab/bert-fa-base-uncased")
model = AutoModel.from_pretrained("HooshvareLab/bert-fa-base-uncased")

# Initialize the LLM with your Gemini API key
GEMINI_API_KEY = "AIzaSyDlgKVTN5d_ks_9-Hl-sMwcXsLHsntBUR4"

def add_knowledge(question: str, answer: str) -> None:
    insert_knowledge(question, answer)

def remove_knowledge(entry: str) -> bool:
    return remove_knowledge(entry)

def get_knowledge_base() -> list:
    knowledge_entries = get_all_knowledge()
    return [(q, a) for q, a in knowledge_entries]

def query_gemini_llm(answer: str) -> str:
    """Query the Gemini API to rewrite the provided answer."""
    prompt = f"Please rewrite the following response in a more humanized way but having the exact same meaning and return just 1 exactly trimmed rewrited sentence in english: '{answer}'"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    logger.info("Gemini API response: %s", response.text)
    
    if response.status_code == 200:
        return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "An error occured in preparing answer.")
    else:
        logger.error("Error from Gemini API: %s", response.text)
        return answer

def insert_knowledge(question: str, answer: str) -> None:
    # Concatenate question and answer for embedding
    combined_text = f"{question} {answer}"  # Combine question and answer
    embedding = get_embedding(combined_text)  # Calculate the embedding for the combined text
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO knowledge_base (question, answer, embedding) VALUES (%s, %s, %s)",
        (question, answer, embedding.tolist())  # Store the embedding in the database
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_answer(question: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get the embedding for the user's question
    question_embedding = get_embedding(question)
    
    # Check for NaN values in the question embedding
    if np.isnan(question_embedding).any():
        logger.error("Question embedding contains NaN values.")
        return None  # Or handle this case as needed

    # Fetch all knowledge base entries
    cursor.execute("SELECT question, answer, embedding FROM knowledge_base")
    rows = cursor.fetchall()
    
    best_match = None
    best_similarity = -1
    
    for row in rows:
        kb_question, answer, embedding = row
        
        # Convert the stored embedding from the database to a numpy array
        embedding = np.array(embedding, dtype=float)  # Ensure the embedding is a float array
        
        # Calculate cosine similarity between the user's question embedding and the stored embedding
        similarity = cosine_similarity(question_embedding.reshape(1, -1), embedding.reshape(1, -1))[0][0]
        
        logger.info("Comparing with KB question: '%s' | Similarity: %f", kb_question, similarity)  # Debugging info
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = answer
    
    cursor.close()
    conn.close()
    
    logger.info("Best match similarity: %f", best_similarity)  # Debugging info
    return best_match if best_similarity > 0.3 else None  # Return answer if similarity is above threshold
