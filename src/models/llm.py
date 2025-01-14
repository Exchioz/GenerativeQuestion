from openai import OpenAI

class LLM:
    def __init__(self, model_name: str, embedding_model: str, api_key: str):
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.client = OpenAI(
            api_key=api_key
        )

    def generate_text(self, prompt: str, max_tokens: int = 50, temperature: float = 0.5) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    
    def get_embedding(self, text: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding