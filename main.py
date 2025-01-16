from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.utils.pdf_processor import PDFProcessor
from src.models.llm import LLM
from src.models.vector_store import VectorStore
from src.quiz.generator import QuizGenerator
from src.quiz.retriever import Retriever

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from dotenv import load_dotenv
from pathlib import Path
import shutil
import os

load_dotenv()
app = FastAPI()
reource_path = "./data/resource"
config = ConfigLoader.load_config("data/config.yml")
logger = setup_logger("QuizApp", level=config['logging']['level'])
llm = LLM(
    model_name=config['openai']['model_name'], 
    embedding_model=config['openai']['embedding_model'],
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.post("/upload_resouce")
def upload_resource(file: UploadFile = File(...), resource_name: str = Form(...)):
    if not resource_name:
        logger.error("Resource name is required")
        raise HTTPException(400, "Resource name is required")
    
    folder_path = Path(reource_path) / resource_name
    # if folder_path.exists():
    #     logger.error(f"Resource {resource_name} already exists")
    #     raise HTTPException(400, f"Resource {resource_name} already exists")
    
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
        vector_store.save(str(resource_loc).replace("\\", "/")+resource_name)
        logger.info("VectorStore saved successfully")
        return {"status": 200, "message": "Resource uploaded and processed successfully"}
    except Exception as e:
        logger.error(f"Error saving VectorStore: {e}")
        raise HTTPException(500, f"Failed to save VectorStore: {e}")


@app.post("/generate_question")
async def generate(quiz_type: str, resource_name: str, context: str, level: str, num_questions: int):
    if quiz_type not in ["multiple", "true_false", "fill_the_blank"]:
        logger.error(f"Invalid quiz type: {quiz_type}")
        raise HTTPException(400, "Invalid quiz type")
    if level not in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        logger.error(f"Invalid level: {level}")
        raise HTTPException(400, "Invalid level")
    if num_questions in range(1, 11):
        logger.error(f"Number of questions must be between 1 and 10: {num_questions}")
        raise HTTPException(400, "Number of questions must be greater than 0")
    if not resource_name:
        logger.error("Resource name is required")
        raise HTTPException(400, "Resource name is required")
    if not context:
        logger.error("Context is required")
        raise HTTPException(400, "Context is required")
    
    logger.info(f"Retrieving VectorStore for {resource_name}...")
    vector_store = VectorStore(384)
    vector_store.load(resource_name)
    logger.info("Vector store loaded successfully")

    logger.info("Retrieving quiz questions...")
    retriever = Retriever(vector_store, llm)
    relevant_contexts = retriever.retrieve(context, top_k=config['retriever']['top_k'])
    if not relevant_contexts:
        logger.error("No relevant contexts found")
        raise HTTPException(400,"No relevant contexts found")
    
    logger.info("Generating quiz questions...")
    quiz_generator = QuizGenerator(
        llm = llm,
        quiz_type = quiz_type,
        context = relevant_contexts,
        category = resource_name,
        level = level,
        num_questions = num_questions
    )

    prompt = quiz_generator.generate_prompt()
    return {"prompt": prompt}

@app.get("/")
def root():
    return {"message": "Welcome to QuizApp!"}