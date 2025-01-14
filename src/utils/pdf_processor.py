import re
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter

class PDFProcessor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        text = ''
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        return text

    @staticmethod
    def preprocess_text(text: str) -> list[str]:
        text = re.sub(r'\s+', ' ', text)
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]

    @staticmethod
    def chunk_text(text, max_length: int, overlap_length: int) -> list[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_length,
            chunk_overlap=overlap_length,
        )
        return text_splitter.split_text(text)