# PDF Question Answering App

This application allows you to upload a PDF, create a searchable database, and ask questions about the content of the PDF. The solution is implemented using FastAPI for the backend, Streamlit for the frontend, and containerized using Docker.

## Features
- Upload a PDF and create a new searchable database.
- Update the existing database with new PDF content.
- Ask questions about the PDF and get answers based on the content.

## Requirements
- Docker
- Docker Compose

## Setup Instructions

1. **Clone the repository:**
    ```sh
    git clone https://github.com/qalmaqihir/RAG_ML_Task/tree/main
    cd ML_Task
    ```
- Create a .env and put your `OPENAI_API_KEY`.

```bash 

OPENAI_API_KEY="dasf23432"

```

2. **Build and run the containers:**
    ```sh
    docker-compose up --build
    ```
    
- if there is any issue with the docker, you can run `steaamlit run test_app4.py` to check out the app.



3. **Access the applications:**
   - FastAPI (Backend): `http://localhost:8000`
   - Streamlit (Frontend): `http://localhost:8501`
  
## API Endpoints

- **Upload PDF and create/update the database:**
  - **Endpoint:** `POST /upload/`
  - **Description:** Upload a PDF file to create a new FAISS database or update an existing one with the content of the PDF.
  - **Request Parameters:**
    - `file` (form-data): The PDF file to be uploaded.
  - **Response:**
    - `200 OK`: On successful upload and database creation/update.
      ```json
      {
        "message": "New database created."
      }
      ```
      or
      ```json
      {
        "message": "Database updated with new documents."
      }
      ```
    - `500 Internal Server Error`: On failure during the upload or database update process.
      ```json
      {
        "detail": "Error message."
      }
      ```

- **Query the PDF content:**
  - **Endpoint:** `POST /query/`
  - **Description:** Ask a question about the content of the PDF and get an answer based on the content.
  - **Request Parameters:**
    - `question` (json): The question to ask about the PDF content.
      ```json
      {
        "question": "Your question here"
      }
      ```
  - **Response:**
    - `200 OK`: On successful retrieval of the answer.
      ```json
      {
        "answer": "The answer to the question.",
        "source": "Name of the PDF file",
        "page": "Page number where the best paragraph is found",
        "best_paragraph": "The best paragraph from the PDF related to the question."
      }
      ```
    - `400 Bad Request`: If the database is not initialized.
      ```json
      {
        "detail": "Database is not initialized."
      }
      ```
    - `500 Internal Server Error`: On failure during the query process.
      ```json
      {
        "detail": "Error message."
      }
      ```

## Technical Details

### Backend
The backend is implemented using FastAPI. It includes endpoints to upload PDF files and create or update a FAISS vector store database, as well as to query the database with a user-provided question.

### Frontend
The frontend is implemented using Streamlit. It provides an interface to upload PDF files and submit questions about the PDF content. The frontend interacts with the FastAPI backend to process uploads and queries.

### Containerization
The solution is containerized using Docker, with a `docker-compose.yml` file to orchestrate the containers for the backend and frontend.

### Environment Variables
Create a `.env` file in the root directory with the following content to configure environment-specific settings:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Development

1. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Run FastAPI locally:**
    ```sh
    uvicorn app:app --reload
    ```

3. **Run Streamlit locally:**
    ```sh
    streamlit run frontend.py

    or streamlit run test_app4.py
    ```

## Challenges and Solutions

### PDF Processing and Text Splitting
- **Challenge:** Extracting and processing text from PDFs.
- **Solution:** Used `PyPDFLoader` for robust PDF loading and `RecursiveCharacterTextSplitter` for splitting text into manageable chunks.

### Database Management
- **Challenge:** Efficiently managing the FAISS vector store.
- **Solution:** Implemented functions to initialize and update the FAISS database without reinitializing.

### Question Relevance and Appropriateness Check
- **Challenge:** Ensuring the relevance and appropriateness of user questions.
- **Solution:** Created a guardrails prompt to filter questions based on relevance and appropriateness.

### API and Frontend Integration
- **Challenge:** Seamless integration of backend API with frontend.
- **Solution:** Used `requests` library in Streamlit to interact with FastAPI, providing clear feedback to users.

## Future Improvements
- **Enhanced Security:** Implement authentication and authorization mechanisms for the API.
- **Scalability:** Optimize for handling larger PDFs and more concurrent users.
- **Advanced Querying:** Implement more advanced querying capabilities, such as keyword highlighting and context expansion.

## Authors
- Jawad Haider

## License
This project is licensed under the MIT License - see the LICENSE file for details.

------------------------------------------------------------------------------------------------------

