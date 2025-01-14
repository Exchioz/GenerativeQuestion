class QuizGenerator:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, context: str) -> str:
        prompt = f"Buatkan saya soal pilihan ganda berdasarkan informasi berikut:\n\n{context}"
        return self.llm.generate_text(prompt)