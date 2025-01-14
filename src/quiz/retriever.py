class Retriever:
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm

    def retrieve(self, prompt: str, top_k: int = 5) -> list[tuple[str, float]]:
        embedding = self.llm.get_embedding([prompt])
        return self.vector_store.search(embedding, top_k)