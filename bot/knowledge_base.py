import requests
import logging
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from bot.database import insert_knowledge, remove_knowledge, get_all_knowledge
from sklearn.metrics.pairwise import cosine_similarity

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

def get_embedding(text: str) -> np.ndarray:
    """Get embeddings for the given text using the BERT model."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1)  # Average pooling
    return embedding.squeeze().numpy()

def query_gemini_llm(answer: str) -> str:
    """Query the Gemini API to rewrite the provided answer."""
    prompt = f"Please rewrite the following response in a more humanized way but having the exact same meaning and return just 1 exactly trimmed rewrited sentence in persian: '{answer}'"
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
        return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "خطایی هنگام آماده کردن پاسخ رخ داد.")
    else:
        logger.error("Error from Gemini API: %s", response.text)
        return "خطایی هنگام دریافت پاسخ از سرویس خارجی رخ داد"

def get_answer(question: str) -> str:
    """Get the best answer for the user's question from the knowledge base."""
    knowledge_entries = get_knowledge_base()
    questions = [q for q, _ in knowledge_entries]  # Extract only the questions

    # Get embeddings for the user's question
    question_embedding = get_embedding(question)

    # Get embeddings for all knowledge base questions
    knowledge_embeddings = [get_embedding(q) for q in questions]

    # Filter out None values from embeddings
    knowledge_embeddings = [emb for emb in knowledge_embeddings if emb is not None]

    # Calculate cosine similarity
    if question_embedding is not None and len(knowledge_embeddings) > 0:
        similarities = cosine_similarity(question_embedding.reshape(1, -1), np.array(knowledge_embeddings))

        # Find the index of the most similar question
        best_match_index = np.argmax(similarities)

        # Check if the similarity is above a certain threshold (e.g., 0.7)
        if similarities[0][best_match_index] > 0.7:
            best_match_question = questions[best_match_index]
            # Retrieve the corresponding answer from the knowledge base
            for kq, ka in knowledge_entries:
                if kq == best_match_question:  # Exact match
                    # Use the Gemini API to humanize the answer
                    humanized_answer = query_gemini_llm(ka)
                    return humanized_answer

    # If no good match is found, return a fallback response
    return "متاسفانه من پاسخ سوال شما را نمی‌دانم."
