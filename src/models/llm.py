from openai import OpenAI
import json

class LLM:
    def __init__(self, model_name: str, embedding_model: str, api_key: str):
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.client = OpenAI(
            api_key=api_key
        )

    def generate_question(self, message: list) -> dict:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            functions=self._function_calling(),
            function_call="auto"
        )

        return json.loads(response.choices[0].message.function_call.arguments)
    
    def get_embedding(self, text: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    @staticmethod
    def _function_calling():
        return [
            {
                "name": "generate_csv",
                "description": "Generate quiz questions in CSV format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "multiple_choices": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "option_a": {"type": "string"},
                                    "option_b": {"type": "string"},
                                    "option_c": {"type": "string"},
                                    "option_d": {"type": "string"},
                                    "answer": {"type": "string", "enum": ["A", "B", "C", "D"]},
                                    "category": {"type": "string"},
                                    "level": {"type": "string", "enum": ["C1", "C2", "C3", "C4", "C5", "C6"]}
                                },
                                "required": ["question", "option_a", "option_b", "option_c", "option_d", "answer", "category", "level"]
                            }
                        },
                        "true_false": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "answer": {"type": "string", "enum": ["True", "False"]},
                                    "category": {"type": "string"},
                                    "level": {"type": "string", "enum": ["C1", "C2", "C3", "C4", "C5", "C6"]}
                                },
                                "required": ["question", "answer", "category", "level"]
                            }
                        },
                        "fill_the_blank": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "answer": {"type": "string"},
                                    "category": {"type": "string"},
                                    "level": {"type": "string", "enum": ["C1", "C2", "C3", "C4", "C5", "C6"]}
                                },
                                "required": ["question", "answer", "category", "level"]
                            }
                        }
                    },
                    "required": []
                }
            }
        ]