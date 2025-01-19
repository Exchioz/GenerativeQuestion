from langchain_community.vectorstores import FAISS
import numpy as np

class VectorStore:
    def __init__(self, embed):
        self.embedding_model = embed
        self.vector_store = None

    def add(self, texts: list):
        self.vector_store = FAISS.from_texts(texts=texts, embedding=self.embedding_model)

    def save(self, filename: str):
        if self.vector_store is None:
            raise ValueError("Vector store is empty")
        self.vector_store.save_local(filename)

    def load(self, filename: str):
        self.vector_store = FAISS.load_local(filename, self.embedding_model, allow_dangerous_deserialization=True)