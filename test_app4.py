import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain_openai import OpenAI
from langchain_openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv
import tempfile
import os

load_dotenv()

st.title("PDF Question Answering App 📚 📖")

# Initialize or load the FAISS database
if 'db' not in st.session_state:
    st.session_state.db = None

uploaded_file = st.file_uploader("🪩 Upload a PDF file", type="pdf")

if uploaded_file is not None:
    _, file_name = tempfile.mkstemp(suffix='.pdf')

    with open(file_name, 'wb') as tmp_file:
        tmp_file.write(uploaded_file.read())
        
    # with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    #     tmp_file.write(uploaded_file.read())
    #     file_name = tmp_file.name

    # Load the PDF file
    loader = PyPDFLoader(file_name)
    docs = loader.load()

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    documents = text_splitter.split_documents(docs)


    if st.button("🪹 Create New Database"):
        # Create a new FAISS vector store
        st.session_state.db = FAISS.from_documents(documents, OpenAIEmbeddings())
        st.success("New database created.")

    if st.button("🪺 Update Existing Database") and st.session_state.db is not None:
        try:
            # Add documents to the existing FAISS vector store
            st.session_state.db.add_documents(documents)
            st.success("Database updated with new documents.")
        except Exception as e:
            st.error(f"An error occurred while updating the database: {e}")

    # Clean up temporary file
    os.remove(file_name)
    
    # # Check if the database exists in session state
    # if st.session_state.db is None:
    #     st.error("Database is not initialized.")
    # else:
    #     if st.button("🪺 Update Existing Database"):
    #         try:
    #             # Add documents to the existing FAISS vector store
    #             st.session_state.db.add_documents(documents)
    #             st.success("Database updated with new documents.")
    #         except FAISS.Error as e:
    #             st.error(f"An error occurred while updating the database: {e}")
    #         except Exception as e:
    #             st.error(f"An unexpected error occurred: {e}")

    # Clean up temporary file if necessary
    # os.remove(file_name)


if st.session_state.db is not None:
    # Set up the LLM
    llm = OpenAI()

    # Create the prompt template with relevance check
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

    # Create the document chain
    document_chain = create_stuff_documents_chain(llm, prompt)

    # Set up the retriever
    retriever = st.session_state.db.as_retriever()

    # Combine the document chain and retriever into a retriever chain
    retriever_chain = create_retrieval_chain(retriever, document_chain)

    # Define the guardrails LLM prompt
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
        return response  # response['answer']

    def answer_question_with_guardrails(question):
        guardrails_result = check_guardrails(question)

        if "Inappropriate" in guardrails_result:
            return "The question contains inappropriate content and cannot be answered."
        elif "Irrelevant" in guardrails_result:
            return "The question is not relevant to the content of the documents."
        
        results = retriever_chain.invoke({"input": question})
        
        if "not applicable" in results['answer']:
            return "The question is not relevant to the content of the documents."
        
        best_paragraph = results['context'][0].page_content
        doc_name = results['context'][0].metadata['source']
        doc_page = results['context'][0].metadata.get('page', 'unknown')  # Assuming metadata might have 'page' info
        answer = results['answer']
        # response = f"{answer}\n\n\t{'---'*10} :Source & Page: {'---'*10}\n{doc_name}, Page {doc_page},\n\n\t{'---'*10} :Best Paragraph: {'---'*10}\n{best_paragraph}"
        response = f"{answer}\n\n\t{'--'*10} :Source & Page: {'--'*10}\n{doc_name}, Page  {doc_page},\n\n\t{'--'*10} :Best Paragraph: {'--'*10}\n{best_paragraph}"

        return response

    # Get the user query
    query = st.text_input("Enter your question about the PDF 🧑🏼‍💻")

    if query:
        response = answer_question_with_guardrails(query)
        st.write("✍️", response)
