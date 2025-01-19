import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class PDFProcessor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        pdf_loader = PyPDFLoader(file_path)
        docs = pdf_loader.load()
        return "\n".join([doc.page_content for doc in docs])

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