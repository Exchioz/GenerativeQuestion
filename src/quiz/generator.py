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

        format_info = self._get_question_format

        message = [
            {
                "role": "system",
                "content": self._get_base_system_prompt(quiz_type)
            },
            {
                'role': 'user',
                'content': f"""
                Buatkan {self.num_questions} soal {quiz_type} dengan mengikuti aturan yang berdasarkan informasi berikut:\n
                <start>
                {self.context}
                <end>
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
        Soal harus relevan, akurat, singkat, padat, jelas, dan selalu sesuai dengan format CSV yang sudah ditentukan.

        Kriteria Kualitas Soal:
        - Gunakan kalimat yang sangat ringkas (maksimal 8 kata untuk fill the blank)
        - Fokus pada satu konsep kunci per pertanyaan
        - Bahasa yang jelas dan tidak ambigu
        - Hindari kata-kata tidak penting atau berlebihan
        - Pastikan soal sesuai dengan level yang diminta
        - Soal harus sesuai dengan kategori, konteks, dan informasi yang diminta
        - Untuk fill the blank, gunakan maksimal satu bagian kosong per kalimat

        Taxonomy Bloom (C1-C6):
        C1: Mengingat - fakta sederhana
        C2: Memahami - konsep dan makna
        C3: Menerapkan - aplikasi dalam situasi baru
        C4: Menganalisis - identifikasi pola dan struktur
        C5: Mengevaluasi - membuat penilaian berdasar kriteria
        C6: Menciptakan - menggabungkan elemen menjadi hal baru
        
        Aturan output:
        - Fokus pada inti pertanyaan
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
                - Question: Pertanyaan singkat yang diajukan.
                - Option A, B, C, D: Empat opsi jawaban yang relevan.
                - Answer: Jawaban yang benar, dituliskan dalam huruf kapital (A, B, C, atau D).
                - Category: Kategori dari soal berdasarkan yang diminta.
                - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.

                Aturan untuk soal Pilihan Ganda:
                1. Pertanyaan harus jelas dan mudah dipahami.
                2. Semua opsi jawaban (A, B, C, D) harus masuk akal dan relevan dengan pertanyaan.
                3. Hanya ada satu jawaban yang benar. Pastikan tidak ada lebih dari satu jawaban yang benar.
                4. Gunakan bahasa yang netral dan tidak mengarahkan peserta didik ke jawaban tertentu.
                5. Setiap soal harus sesuai dengan tingkat kesulitan yang diminta (C1-C6).
                """
            },
            "true_false": {
                "header": "Question,Answer,Category,Level",
                "desc": """
                - Question: Pernyataan singkat yang harus dinilai benar atau salah.
                - Answer: "True" atau "False", ditulis dengan huruf kapital.
                - Category: Kategori dari soal berdasarkan yang diminta.
                - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.

                Aturan untuk soal Benar/Salah:
                1. Pernyataan harus jelas dan tidak ambigu.
                2. Jawaban hanya dapat berupa "True" atau "False".
                3. Tidak boleh ada pernyataan yang membingungkan atau memiliki interpretasi ganda.
                4. Pastikan soal sesuai dengan level yang diminta (C1-C6).
                """
            },
            "fill_the_blank": {
                "header": "Question,Answer,Category,Level",
                "desc": """
                - Question: Kalimat singkat dengan satu bagian kosong (___).
                - Answer: Jawaban singkat untuk mengisi bagian kosong.
                - Category: Kategori dari soal berdasarkan yang diminta.
                - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.

                Aturan untuk soal Isi Bagian Kosong (Fill the Blank):
                1. Kalimat maksimal 8 kata termasuk bagian kosong.
                2. Gunakan tepat satu '___' untuk bagian kosong.
                3. Jawaban harus berupa kata atau frasa singkat yang berhubungan dengan konteks (jangan kata sambung).
                4. Fokus pada satu konsep kunci per pertanyaan.
                5. Hindari kalimat kompleks atau berbelit.
                """
            }
        }

        return format.get(self.quiz_type)