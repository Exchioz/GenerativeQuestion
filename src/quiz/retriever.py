class Retriever:
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm

    def retrieve(self, prompt: str, top_k: int) -> str:
        embedding = self.llm.get_embedding([prompt])
        results = self.vector_store.search(embedding, top_k)
        combined_result = " ".join([result[0] for result in results])

        return combined_result