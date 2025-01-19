import numpy as np

class Retriever:
    def __init__(self, vector_store, embed):
        self.embed = embed
        self.vector_store = vector_store
    
    def retrieve(self, query:str, top_k: int) -> str:
        if not self.vector_store:
            raise ValueError("Vector store is not initialized or empty")
        results = self.vector_store.similarity_search(query,k=top_k)
        retrieved_texts = [doc.page_content for doc in results]

        return " ".join(retrieved_texts)