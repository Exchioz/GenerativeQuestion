from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.utils.pdf_processor import PDFProcessor
from src.models.llm import LLM
from src.models.vector_store import VectorStore
from src.quiz.generator import QuizGenerator
from src.quiz.retriever import Retriever

from dotenv import load_dotenv
import os

def main():
    # Setup
    config = ConfigLoader.load_config("data/config.yml")
    logger = setup_logger("QuizApp", level=config['logging']['level'])
    load_dotenv()
    llm = LLM(model_name=config['openai']['model_name'], embedding_model=config['openai']['embedding_model'], api_key=os.getenv("OPENAI_API_KEY"))

    # Check if vector store exists
    vector_store_name = config['vector_store']['path']
    vector_store = None
    
    if os.path.exists(vector_store_name):
        logger.info("Loading existing vector store...")
        first_embedding = llm.get_embedding([chunks[0]])
        vector_store = VectorStore(dimension=len(first_embedding))
        vector_store.load(vector_store_name)
        logger.info("Vector store loaded successfully")

    # If no vector store exists or loading failed, create new one
    if vector_store is None:
        # Extract text from PDF
        logger.info("Extracting text from PDF...")
        raw_text = PDFProcessor.extract_text(config['pdf']['path'])
        paragraphs = PDFProcessor.preprocess_text(raw_text)

        # Chunk text
        logger.info("Chunking text...")
        chunks = []
        for paragraph in paragraphs:
            chunks.extend(PDFProcessor.chunk_text(
                paragraph, 
                max_length=config['chunking']['max_length'], 
                overlap_length=config['chunking']['overlap_length']
            ))

        # Create VectorStore
        logger.info("Creating VectorStore...")
        
        # Get dimension from first embedding
        first_embedding = llm.get_embedding([chunks[0]])
        vector_store = VectorStore(dimension=len(first_embedding))

        # Process chunks
        logger.info(f"Processing {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks, 1):
            embedding = llm.get_embedding([chunk])
            vector_store.add(embedding, chunk)
            if i % 10 == 0:
                logger.info(f"Processed {i}/{len(chunks)} chunks")

        # Save vector store
        logger.info("Saving VectorStore...")
        try:
            vector_store.save(vector_store_name)
            logger.info("VectorStore saved successfully")
        except Exception as e:
            logger.error(f"Error saving VectorStore: {e}")

    # Interactive quiz generation loop
    while True:
        query = input("\nEnter a topic or question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break

        # Retrieve and generate questions
        logger.info("Retrieving quiz questions...")
        retriever = Retriever(vector_store, llm)
        relevant_contexts = retriever.retrieve(query, top_k=config['retriever']['top_k'])

        if not relevant_contexts:
            logger.warning("No relevant contexts found")
            continue

        # Generate quiz questions
        logger.info("Generating quiz questions...")
        quiz_generator = QuizGenerator(llm)
        
        for context, score in relevant_contexts:
            print(f"\nGenerating question (relevance score: {score:.2f})...")
            try:
                question = quiz_generator.generate(context)
                print(f"Question: {question}\n")
            except Exception as e:
                logger.error(f"Error generating question: {e}")

        print("\n" + "="*50)

if __name__ == "__main__":
    main()