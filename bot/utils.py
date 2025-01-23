from sentence_transformers import SentenceTransformer
import numpy as np

# Load the lightweight embedding model
embedding_model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

def get_embedding(text: str) -> np.ndarray:
    """Get embeddings for the given text using the lightweight model."""
    embedding = embedding_model.encode(text)
    return embedding