class QuizGenerator:
    def __init__(self, llm, quiz_type: str, context: str, category: str, level: str, num_questions: int) -> None:
        self.llm = llm
        self.quiz_type = quiz_type
        self.context = context
        self.category = category
        self.level = level
        self.num_questions = num_questions

    def generate(self) -> str:
        system_prompt = """
        Anda adalah asisten AI yang sangat andal, cerdas, dan berpengalaman dalam membuat berbagai jenis soal berbasis informasi tertentu. 
        Tugas utama Anda adalah menghasilkan soal pilihan ganda, benar/salah, dan fill the blank berdasarkan konteks  dan jenis soal yang diberikan oleh pengguna.
        Soal harus relevan, akurat, dan selalu sesuai dengan format CSV yang sudah ditentukan. 
        Anda harus selalu memastikan bahwa format output benar-benar konsisten tanpa ada penyimpangan.

        Berikut adalah aturan dan format output yang harus Anda ikuti secara ketat:
        1. **Pilihan Ganda (Multiple Choice Questions):**
            Format CSV:
            "Question","Option A","Option B","Option C","Option D","Answer","Category","Level"
            - Question: Pertanyaan utama yang diajukan.
            - Option A, B, C, D: Empat opsi jawaban yang relevan.
            - Answer: Jawaban yang benar, dituliskan dalam huruf kapital (A, B, C, atau D).
            - Category: Kategori dari soal (misalnya, Pemrograman, Matematika, Sejarah).
            - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.
        
        2. **Soal Benar/Salah (True/False Questions):**
            Format CSV:
            "Question","Answer","Category","Level"
            - Question: Pernyataan utama yang harus dinilai benar atau salah.
            - Answer: "True" atau "False", ditulis dengan huruf kapital.
            - Category: Kategori dari soal.
            - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.
        
        3. **Soal Isian (Fill the Blank Questions):**
            Format CSV:
            "Question","Answer","Category","Level"
            - Question: Pernyataan dengan bagian kosong yang harus diisi peserta.
            - Answer: Jawaban yang benar untuk bagian kosong tersebut.
            - Category: Kategori dari soal.
            - Level: Tingkat kesulitan soal, berdasarkan skala C1-C6.

            ### **Penjelasan Level C1-C6 (Bloom's Taxonomy)**
            - **C1 (Mengingat)**: Menguji kemampuan peserta untuk mengingat fakta atau informasi sederhana.
            - **C2 (Memahami)**: Menguji kemampuan peserta untuk memahami konsep atau makna dari informasi.
            - **C3 (Menerapkan)**: Menguji kemampuan peserta untuk menggunakan informasi atau konsep dalam situasi baru.
            - **C4 (Menganalisis)**: Menguji kemampuan peserta untuk memecah informasi menjadi bagian-bagian kecil dan mengenali pola.
            - **C5 (Mengevaluasi)**: Menguji kemampuan peserta untuk membuat keputusan berdasarkan kriteria tertentu.
            - **C6 (Menciptakan)**: Menguji kemampuan peserta untuk menggabungkan berbagai elemen menjadi sesuatu yang baru atau inovatif.

            ### **Aturan Penting**
            1. Semua output harus dalam bentuk CSV dengan format yang ketat.
            2. Setiap kolom dalam CSV harus diapit tanda kutip ganda (") untuk memastikan format sesuai standar.
            3. Jawaban untuk soal pilihan ganda harus dalam huruf kapital (A, B, C, atau D).
            4. Jangan menambahkan penjelasan tambahan di luar format CSV yang ditentukan.
            5. Selalu gunakan kategori dan level yang relevan dengan permintaan pengguna.

            Anda harus selalu mematuhi aturan ini tanpa pengecualian. Jika ada ketidaksesuaian, Anda harus mengulangi proses pembuatan soal hingga sesuai dengan format yang ditentukan.
        """
        if self.quiz_type == "multiple_choice":
            prompt = self._generate_multiple_question()
        elif self.quiz_type == "true_false":
            prompt = self._generate_true_false_question()
        elif self.quiz_type == "fill_the_blank":
            prompt = self._generate_fill_the_blank_question()

        return self.llm.generate_text(prompt, system_prompt)
    
    def _generate_multiple_question(self) -> str:
        return f"""
        Berdasarkan informasi berikut, buatkan {self.num_questions} soal pilihan ganda:
        Konteks: {self.context}
        Kategori: {self.category}
        Level: {self.level}
        Format output yang diharapkan adalah **CSV** dengan header yang benar sebagai berikut:
        "Question","Option A","Option B","Option C","Option D","Answer","Category","Level"
        
        Jangan pernah keluar dari struktur atau format yang telah ditentukan. Jika output tidak sesuai dengan format, ulangi proses pembuatan soal hingga sesuai dengan format yang benar.
        Tugas Anda adalah menghasilkan soal berdasarkan informasi yang diberikan dan memastikan bahwa output selalu mengikuti format yang ketat dan konsisten.
        """
    
    def _generate_true_false_question(self) -> str:
        return  f"""
        Berdasarkan informasi berikut, buatkan {self.num_questions} soal benar/salah:
        Konteks: {self.context}
        Kategori: {self.category}
        Level: {self.level}
        Format output yang diharapkan adalah **CSV** dengan header yang benar sebagai berikut:
        "Question","Answer","Category","Level"
        
        Jangan pernah keluar dari struktur atau format yang telah ditentukan. Jika output tidak sesuai dengan format, ulangi proses pembuatan soal hingga sesuai dengan format yang benar.
        Tugas Anda adalah menghasilkan soal berdasarkan informasi yang diberikan dan memastikan bahwa output selalu mengikuti format yang ketat dan konsisten.
        """
    
    def _generate_fill_the_blank_question(self) -> str:
        return f"""
        Berdasarkan informasi berikut, buatkan {self.num_questions} soal isian:
        Konteks: {self.context}
        Kategori: {self.category}
        Level: {self.level}
        Format output yang diharapkan adalah **CSV** dengan header yang benar sebagai berikut:
        "Question","Answer","Category","Level"

        Jangan pernah keluar dari struktur atau format yang telah ditentukan. Jika output tidak sesuai dengan format, ulangi proses pembuatan soal hingga sesuai dengan format yang benar.
        Tugas Anda adalah menghasilkan soal berdasarkan informasi yang diberikan dan memastikan bahwa output selalu mengikuti format yang ketat dan konsisten.
        """ 