import faiss
import pickle
import numpy as np

class VectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)
        self.data = []

    def add(self, embeddings: list[float], texts: str) -> None:
        embedding_array = np.array([embeddings], dtype=np.float32)
        self.index.add(embedding_array)
        self.data.append(texts)

    def search(self, query_embedding: list[float], top_k: int) -> list[tuple[str, float]]:
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, k=min(top_k, len(self.data)))
        
        results = []
        for idx, (distance, index) in enumerate(zip(distances[0], indices[0])):
            if index < len(self.data):
                results.append((self.data[index], float(distance)))
        return results

    def save(self, filename: str):
        faiss.write_index(self.index, filename)
        with open(f"{filename}.pkl", 'wb') as f:
            pickle.dump(self.data, f)

    def load(self, filename: str):
        self.index = faiss.read_index(filename)
        with open(f"{filename}.pkl", 'rb') as f:
            self.data = pickle.load(f)