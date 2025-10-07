from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

#Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


#Load faiss index
index = faiss.IndexFlatL2(model.get_sentence_embedding_dimension())



def embed_text(text: str) -> np.ndarray:
    return model.encode([text])[0]




def add_embedding_to_index(embedding: np.ndarray, id: int):
    index.add(np.array([embedding], dtype=np.float32))

def search_embedding(query_embedding: np.ndarray, top_k: int = 5):
    D, I = index.search(np.array([query_embedding], dtype=np.float32), top_k)
    return I, D