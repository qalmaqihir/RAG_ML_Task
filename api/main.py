from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import tempfile
import os

app = FastAPI()

# Initialize the FAISS database
db = None

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    global db
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file.file.read())
        file_name = tmp_file.name

    loader = PyPDFLoader(file_name)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    documents = text_splitter.split_documents(docs)

    db = FAISS.from_documents(documents, OpenAIEmbeddings())
    
    os.remove(file_name)
    return {"message": "New database created."}

@app.post("/update-db/")
async def update_db(file: UploadFile = File(...)):
    global db
    if db is None:
        raise HTTPException(status_code=400, detail="Database is not initialized.")
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file.file.read())
        file_name = tmp_file.name

    loader = PyPDFLoader(file_name)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    documents = text_splitter.split_documents(docs)

    try:
        db.add_documents(documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the database: {e}")
    finally:
        os.remove(file_name)
    
    return {"message": "Database updated with new documents."}

class QueryModel(BaseModel):
    question: str

@app.post("/query/")
async def query(query: QueryModel):
    global db
    if db is None:
        raise HTTPException(status_code=400, detail="Database is not initialized.")
    
    llm = OpenAI()
    prompt = ChatPromptTemplate.from_template(
        """
        Answer the following question based only on the provided context.
        Think step by step before providing a detailed answer.
        If the question is not relevant to the provided context, inform the user that the question is not applicable.
        <context>
        {context}
        </context>

        Question: {input}
        """
    )

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = db.as_retriever()
    retriever_chain = create_retrieval_chain(retriever, document_chain)

    guardrails_prompt = ChatPromptTemplate.from_template(
        """
        You are an assistant that helps to determine if questions are appropriate and relevant.
        Analyze the following question and answer whether it contains any inappropriate content or if it is irrelevant to the given context.

        Question: {question}
        
        Respond with one of the following:
        1. "Inappropriate" - if the question contains inappropriate content.
        2. "Irrelevant" - if the question is not relevant to the provided context.
        3. "Appropriate and Relevant" - if the question is appropriate and relevant to the provided context.
        """
    )

    def check_guardrails(question):
        response = llm.invoke(guardrails_prompt.format(question=question))
        return response

    guardrails_result = check_guardrails(query.question)

    if "Inappropriate" in guardrails_result:
        return JSONResponse(content={"answer": "The question contains inappropriate content and cannot be answered."}, status_code=400)
    elif "Irrelevant" in guardrails_result:
        return JSONResponse(content={"answer": "The question is not relevant to the content of the documents."}, status_code=400)
    
    results = retriever_chain.invoke({"input": query.question})
    
    if "not applicable" in results['answer']:
        return JSONResponse(content={"answer": "The question is not relevant to the content of the documents."}, status_code=400)
    
    # Return JSON response directly
    # return JSONResponse(content=results)
    best_paragraph = results['context'][0].page_content
    doc_name = results['context'][0].metadata['source']
    doc_page = results['context'][0].metadata.get('page', 'unknown')
    answer = results['answer']
    response = f"{answer}\n\n\t{'--'*10} :Source & Page: {'--'*10}\n{doc_name}, Page  {doc_page},\n\n\t{'--'*10} :Best Paragraph: {'--'*10}\n{best_paragraph}"
    
    return {"answer": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
