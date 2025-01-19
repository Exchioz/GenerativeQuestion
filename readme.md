# Generative Questions

**GenerativeQuestion** is a FastAPI-based application used for uploading and processing PDF files, generating quiz questions based on the content of those files, and saving them into a database for later use.

The app leverages the OpenAI API to generate questions and uses Faiss to manage vector data for information retrieval.

## Key Features

- **Upload PDF Resource**: Upload PDF files and extract text to generate quiz questions.
- **Quiz Generator**: Generate quiz questions based on context extracted from PDF files.
- **Data Management**: Save resource information and quiz questions into a MySQL database.
- **Search & Retrieval**: Use vector store and FAISS-based search to retrieve relevant context for quiz generation.

## Prerequisites

Before you start, ensure you have the following:

- **Python 3.10.11**
- **Required Packages**:
  - `fastapi`
  - `langchain_openai`
  - `mysql-connector-python`
  - `faiss-cpu`
  - etc...
- **MySQL Database**: Database with tables to store resources and questions.
- **OpenAI API Key**: You’ll need OpenAI API key to use the LLM (Language Model) service.

## Installation

### 1. Clone the Repository

Start by cloning this repository to your local machine:

```bash
git clone https://github.com/Exchioz/GenerativeQuestion.git
cd GenerativeQuestion
```

### 2. Create a Virtual Environment

It’s recommended to use a virtual environment to manage dependencies:

```bash
# Create Virtual Environment
python -m venv genques_venv

# Activate Venv in Linux/MacOS
source genques_venv/bin/activate

# Activate Venv in Windows
genques_venv\Scripts\activate
```

### 3. Install Dependencies

Install all the required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure `.env` File

Create new file named `.env` and put OpenAI Keys in this file.

```bash
OPENAI_API_KEY = "sk-XXXXXXX"
```

### 5. Set Up the Database

Ensure you have MySQL installed and running on your system. Import the database schema by executing the `db.sql` file.

### 6. Configure data/config.yml

Check the `data/config.yml` file and update it with your application settings.

## Running the Application

Once you’ve installed all dependencies and configured the app, you can run it using Uvicorn:

```bash
uvicorn main:app --reload
```

The app will run at `http://127.0.0.1:8000`

## API Endpoints

### 1. Upload Resource (PDF)

**Endpoint**: `POST /upload_resouce`

**Description**: Uploads a PDF file and adds the resource to the database.

**Form Data**:

- `resource_name`: Name of the resource (e.g., "computer_history").
- `file`: The PDF file to be processed.

**Example Request**:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload_resouce' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'resource_name="computer_history"' \
  -F 'file=@path_to_your_file.pdf'
```

**Response**:

```json
{
  "message": "Resource uploaded and processed successfully"
}
```

## 2. Generate Quiz Questions

**Endpoint**: `POST /generate_question`

**Description**: Generates quiz questions based on the context extracted from the uploaded resource.

**Request Body**:

```json
{
  "quiz_type": "multiple_choices", // Quiz type: "multiple_choices", "true_false", "fill_the_blank"
  "resource_name": "computer_history", // The resource name to use
  "context": "Some context from the resource", // Context for generating questions
  "level": "C1", // Difficulty level: C1, C2, C3, C4, C5, C6
  "num_questions": 5 // Number of questions to generate
}
```

**Example Request**:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate_question' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "quiz_type": "multiple",
    "resource_name": "computer_history",
    "context": "History of computers...",
    "level": "C1",
    "num_questions": 5
  }'
```

**Response**:

```json
{
  "message": "Quiz questions generated and added to DB successfully"
}
```
