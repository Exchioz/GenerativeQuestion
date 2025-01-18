from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.utils.pdf_processor import PDFProcessor
from src.models.llm import LLM
from src.models.vector_store import VectorStore
from src.quiz.generator import QuizGenerator
from src.quiz.retriever import Retriever
from src.utils.db_handler import DBHandler

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import shutil
import os

load_dotenv()
app = FastAPI()
reource_path = Path("./data/resource")
reource_path.mkdir(parents=True, exist_ok=True)
config = ConfigLoader.load_config("data/config.yml")
logger = setup_logger("QuizApp", level=config['logging']['level'])
llm = LLM(
    model_name=config['openai']['model_name'], 
    embedding_model=config['openai']['embedding_model'],
    api_key=os.getenv("OPENAI_API_KEY")
)

class QuizRequest(BaseModel):
    quiz_type: str
    resource_name: str
    context: str
    level: str
    num_questions: int

class UploadRequest(BaseModel):
    resource_name: str
    file: UploadFile

@app.post("/upload_resouce")
async def upload_resource(file: UploadFile = File(...), resource_name: str = Form(...)):
    if not resource_name:
        logger.error("Resource name is required")
        raise HTTPException(400, "Resource name is required")
    if not file.filename.endswith(".pdf"):
        logger.error("File must be PDF format")
        raise HTTPException(400, "File must be PDF format")
    
    folder_path = Path(reource_path) / resource_name
    if folder_path.exists():
        logger.error(f"Resource {resource_name} already exists")
        raise HTTPException(400, f"Resource {resource_name} already exists")
    
    folder_path.mkdir(parents=True, exist_ok=True)
    resource_loc = folder_path / resource_name
    pdf_path = f"{resource_loc}.pdf"

    try:
        logger.info(f"Uploading {resource_name}...")
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(500, f"Failed to save file: {e}")
    
    logger.info(f"Extracting text from {resource_name}...")
    raw_text = PDFProcessor.extract_text(pdf_path)
    paragraphs = PDFProcessor.preprocess_text(raw_text)
    
    logger.info("Chunking text...")
    chunks = []
    for paragraph in paragraphs:
        chunks.extend(PDFProcessor.chunk_text(
            paragraph, 
            max_length=config['chunking']['max_length'], 
            overlap_length=config['chunking']['overlap_length']
        ))
    
    logger.info("Creating VectorStore...")
    first_embedding = llm.get_embedding([chunks[0]])
    vector_store = VectorStore(dimension=len(first_embedding))
    
    logger.info(f"Processing {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks, 1):
        embedding = llm.get_embedding([chunk])
        vector_store.add(embedding, chunk)
        if i % 10 == 0:
            logger.info(f"Processed {i}/{len(chunks)} chunks")
    
    logger.info("Saving VectorStore...")
    try:
        vector_store_dir = str(resource_loc).replace("\\", "/")+resource_name
        vector_store.save(vector_store_dir)
        logger.info("VectorStore saved successfully")
        return {"message": "Resource uploaded and processed successfully"}
    except Exception as e:
        logger.error(f"Error saving VectorStore: {e}")
        raise HTTPException(500, f"Failed to save VectorStore: {e}")


@app.post("/generate_question")
async def generate(question: QuizRequest):
    if question.quiz_type not in ["multiple", "true_false", "fill_the_blank"]:
        logger.error(f"Invalid quiz type: {question.quiz_type}")
        raise HTTPException(400, "Invalid quiz type")
    if question.level not in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        logger.error(f"Invalid level: {question.level}")
        raise HTTPException(400, "Invalid level")
    if question.num_questions < 1 or question.num_questions > 10:
        logger.error(f"Number of questions must be between 1 and 10: {question.num_questions}")
        raise HTTPException(400, "Number of questions must be greater than 0")
    if not question.resource_name:
        logger.error("Resource name is required")
        raise HTTPException(400, "Resource name is required")
    if not question.context:
        logger.error("Context is required")
        raise HTTPException(400, "Context is required")
    
    logger.info(f"Retrieving VectorStore for {question.resource_name}...")
    
    folder_path = Path(reource_path) / question.resource_name
    resource_loc = folder_path / question.resource_name
    vector_store_dir = str(resource_loc).replace("\\", "/")+question.resource_name
    vector_store = VectorStore(384)
    vector_store.load(vector_store_dir)
    logger.info("Vector store loaded successfully")

    logger.info("Retrieving quiz questions...")
    retriever = Retriever(vector_store, llm)
    relevant_contexts = retriever.retrieve(question.context, top_k=config['retriever']['top_k'])
    if not relevant_contexts:
        logger.error("No relevant contexts found")
        raise HTTPException(400,"No relevant contexts found")
    
    print(relevant_contexts)
    
    logger.info("Generating quiz questions...")
    quiz_generator = QuizGenerator(
        llm = llm,
        quiz_type = question.quiz_type,
        context = relevant_contexts,
        category = question.resource_name,
        level = question.level,
        num_questions = question.num_questions
    )

    output = quiz_generator.make_question()
    logger.info("Quiz questions generated successfully")
    print(output)

    if not isinstance(output, dict):
        logger.error("Failed to generate quiz questions")
        raise HTTPException(500, "Failed to generate quiz questions")
    
    logger.info("Adding the question to DB...")
    db_handler = DBHandler(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['database']
    )
    try:
        db_handler.connect()
        db_handler.add_question(output)
        db_handler.close()
        logger.info("Quiz questions added to DB successfully")
        return {"message": "Quiz questions generated and added to DB successfully"}
    except Exception as e:
        logger.error(f"Failed to add question to DB: {e}")
        raise HTTPException(500, f"Failed to add question to DB: {e}")
    
@app.get("/")
def root():
    return {"message": "Welcome to QuizApp!"}