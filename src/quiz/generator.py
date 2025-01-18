class QuizGenerator:
    def __init__(self, llm, quiz_type: str, context: str, category: str, level: str, num_questions: int) -> None:
        self.llm = llm
        self.quiz_type = quiz_type
        self.context = context
        self.category = category
        self.level = level
        self.num_questions = num_questions
    
    def make_question(self) -> list:
        if self.quiz_type == "multiple":
            quiz_type =  "pilihan ganda"
        elif self.quiz_type == "true_false":
            quiz_type = "benar/salah"
        elif self.quiz_type == "fill_the_blank":
            quiz_type = "fill the blank"

        format_info = self._get_question_format()

        message = [
            {
                "role": "system",
                "content": self._get_base_system_prompt(quiz_type)
            },
            {
                'role': 'user',
                'content': f"""
                Buatkan {self.num_questions} soal {quiz_type} berdasarkan informasi berikut:
                Konteks: {self.context}
                Kategori: {self.category}
                Level: {self.level}

                Format CSV dengan header:
                {format_info['header']}\n{format_info['desc']}
                """
            }
        ]

        return self.llm.generate_question(message)

    @staticmethod
    def _get_base_system_prompt(quiz_type) -> str:
        return f"""
        Anda adalah asisten AI yang sangat andal, cerdas, dan berpengalaman dalam membuat soal {quiz_type} berbasis informasi tertentu. 
        Soal harus relevan, akurat, dan selalu sesuai dengan format CSV yang sudah ditentukan. 
        Anda harus selalu memastikan bahwa format output benar-benar konsisten tanpa ada penyimpangan.

        Kriteria Kualitas Soal:
        - Bahasa yang jelas dan tidak ambigu
        - Setiap pilihan jawaban harus masuk akal
        - Hindari petunjuk gramatikal yang tidak disengaja
        - Pastikan soal seusai dengan level yang diminta
        - Pastikan hanya ada satu jawaban yang benar

        Taxonomy Bloom (C1-C6):
        C1: Mengingat - fakta sederhana
        C2: Memahami - konsep dan makna
        C3: Menerapkan - aplikasi dalam situasi baru
        C4: Menganalisis - identifikasi pola dan struktur
        C5: Mengevaluasi - membuat penilaian berdasar kriteria
        C6: Menciptakan - menggabungkan elemen menjadi hal baru
        
        Aturan output:
        - Format harus CSV dengan header yang sesuai
        - Gunakan tanda kutip ganda (") untuk setiap kolom
        - Tidak ada penjelasan tambahan di luar format CSV
        """
    
    @property
    def _get_question_format(self) -> dict:
        format = {
            "multiple": {
                "header": "Question,Option A,Option B,Option C,Option D,Answer,Category,Level",
                "desc": """
                - Question: Pertanyaan utama yang diajukan.
                - Option A, B, C, D: Empat opsi jawaban yang relevan.
                - Answer: Jawaban yang benar, dituliskan dalam huruf kapital (A, B, C, atau D).
                - Category: Kategori dari soal berdasarkan yang diminta.
                - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.
                """
            },
            "true_false": {
                "header": "Question,Answer,Category,Level",
                "desc": """
                - Question: Pernyataan utama yang harus dinilai benar atau salah.
                - Answer: "True" atau "False", ditulis dengan huruf kapital.
                - Category: Kategori dari soal berdasarkan yang diminta.
                - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.
                """
            },
            "fill_the_blank": {
                "header": "Question,Answer,Category,Level",
                "desc": """
                - Question: Pertanyaan terdapat '___' untuk bagian yang harus diisi peserta.
                - Answer: Jawaban yang benar untuk bagian kosong tersebut.
                - Category: Kategori dari soal berdasarkan yang diminta.
                - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.
                """
            }
        }

        return format.get(self.quiz_type)