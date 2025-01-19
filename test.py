from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

class MultipleQuestion(BaseModel):
    question: str = Field(..., description="Question to generate")
    option_a: str = Field(..., description="Option A")
    option_b: str = Field(..., description="Option B")
    option_c: str = Field(..., description="Option C")
    option_d: str = Field(..., description="Option D")
    answer: str = Field(..., description="Correct answer", pattern="[A-D]")
    category: str = Field(..., description="Category of the question")
    level: str = Field(..., description="Level of the question", pattern="C[1-6]")

class TrueFalseQuestion(BaseModel):
    question: str = Field(..., description="Question to generate")
    answer: bool = Field(..., description="Correct answer", pattern="True|False")
    category: str = Field(..., description="Category of the question")
    level: str = Field(..., description="Level of the question", pattern="C[1-6]")

class FillTheBlankQuestion(BaseModel):
    question: str = Field(..., description="Question to generate")
    answer: str = Field(..., description="Correct answer")
    category: str = Field(..., description="Category of the question")
    level: str = Field(..., description="Level of the question", pattern="C[1-6]")

class QuizGenerator:
    def __init__(self, llm, quiz_type: str, context: str, category: str, level: str, num_questions: int) -> None:
        self.llm = llm
        self.quiz_type = quiz_type
        self.context = context
        self.category = category
        self.level = level
        self.num_questions = num_questions
        self.parser = self._get_parser()

    def _get_parser(self):
        parsers = {
            "multiple": JsonOutputParser(pydantic_object=MultipleQuestion),
            "true_false": JsonOutputParser(pydantic_object=TrueFalseQuestion),
            "fill_the_blank": JsonOutputParser(pydantic_object=FillTheBlankQuestion),
        }
        return parsers.get(self.quiz_type)

    def _get_rules(self):
        rules = {
            "multiple": """
            Aturan untuk soal Pilihan Ganda:
            1. Pertanyaan harus jelas dan mudah dipahami
            2. Semua opsi jawaban (A, B, C, D) harus masuk akal dan relevan
            3. Hanya ada satu jawaban yang benar
            4. Gunakan bahasa yang netral
            5. Setiap soal harus sesuai dengan tingkat kesulitan yang diminta
            """,
            "true_false": """
            Aturan untuk soal Benar/Salah:
            1. Pernyataan harus jelas dan tidak ambigu
            2. Jawaban hanya dapat berupa "True" atau "False"
            3. Tidak boleh ada pernyataan yang membingungkan
            4. Pastikan soal sesuai dengan level yang diminta
            """,
            "fill_the_blank": """
            Aturan untuk soal Isian:
            1. Pertanyaan harus jelas dan mudah dipahami
            2. Jawaban harus sesuai dengan konteks
            3. Gunakan '___' untuk bagian kosong
            4. Jawaban harus berupa kata atau frasa singkat
            5. Fokus pada satu konsep kunci per pertanyaan
            6. Pastikan soal sesuai dengan level yang diminta
            """
        }
        return rules.get(self.quiz_type)
    
    def _get_level_info(self):
        level_info = {
            "C1": {
                "description": "Memeriksa dan mengevaluasi",
                "tasks": ["Menganalisis", "Mengevaluasi", "Membuat keputusan"]
            },
            "C2": {
                "description": "Membuat model",
                "tasks": ["Mengorganisir", "Menggabungkan", "Merancang"]
            },
            "C3": {
                "description": "Menghasilkan",
                "tasks": ["Membuat", "Menghasilkan", "Mengembangkan"]
            },
            "C4": {
                "description": "Memahami",
                "tasks": ["Menjelaskan", "Meringkas", "Mengidentifikasi"]
            },
            "C5": {
                "description": "Mengingat",
                "tasks": ["Mengingat", "Mengenali", "Mengulang"]
            },
            "C6": {
                "description": "Mengenal",
                "tasks": ["Mengenal", "Mengidentifikasi", "Mengklasifikasikan"]
            }
        }
        return level_info.get(self.level)

    def generate(self):
        if not self.parser:
            raise ValueError("Invalid quiz type")
        
        query = f"""
        Buatkan {self.num_questions} soal {self.quiz_type.replace('_', ' ')} dengan konteks berikut:
        <start>
        {self.context}
        <end>
        Kategori: {self.category}

        Tingkat dalam Taxonomy Bloom: {self.level}
        - {self._get_level_info()['description']}
        - Tugas yang harus dilakukan: {', '.join(self._get_level_info()['tasks'])}

        {self.parser.get_format_instructions()}
        {self._get_rules()}
        """
        
        prompt = PromptTemplate(
            template="Jawab pertanyaan pengguna.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        chain = prompt | self.llm | self.parser
        print(query)
        return chain.invoke({"query": query})


model = ChatOpenAI(model_name="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
generate = QuizGenerator(
    llm=model,
    quiz_type="true_false",
    context="Pada tahun 2019, Indonesia berhasil memperoleh medali emas di ajang SEA Games.",
    category="Olahraga",
    level="C1",
    num_questions=2
)

output = generate.generate()
print(output)
