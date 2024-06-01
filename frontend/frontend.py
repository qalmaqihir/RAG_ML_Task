import streamlit as st
import requests

st.title("PDF Question Answering App 📚 📖")

uploaded_file = st.file_uploader("🪩 Upload a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("🪹 Create New Database"):
        response = requests.post("http://pdf_qa_backend:8000/upload-pdf/", files={"file": uploaded_file})
        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error(response.json()["detail"])

    if st.button("🪺 Update Existing Database"):
        response = requests.post("http://pdf_qa_backend:8000/update-db/", files={"file": uploaded_file})
        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error(response.json()["detail"])

query = st.text_input("Enter your question about the PDF 🧑🏼‍💻")

# if query:
#     response = requests.post("http://pdf_qa_backend:8000/query/", json={"question": query})
#     if response.status_code == 200:
#         print(f"answer: {response}")
#         st.write("✍️", response.json()["answer"])
#     else:
#         print(f"answer: {response}")
#         st.error(response.json()["answer"])


if query:
    print(f"From 2nd Query block...\n")
    response = requests.post("http://pdf_qa_backend:8000/query/", json={"question": query})
    print(f"question {query} is being send to the /query endpoint\n")
    st.write(f"question {query} is being send to the /query endpoint\n")
    st.write(f"\nResponse from Backend: {response}")
    
    # Update this section in frontend.py
    if response.status_code == 200:
        response_json = response.json()
        print("Response JSON:", response_json)
        st.write("✍️", response_json)

        if "answer" in response_json:
            st.write("✍️", response_json["answer"])
        else:
            st.error("Response does not contain 'answer' key:", response_json)
    else:
        st.error(response.text)



# import streamlit as st
# import requests

# st.title("PDF Question Answering App 📚 📖")

# uploaded_file = st.file_uploader("🪩 Upload a PDF file", type="pdf")

# if uploaded_file is not None:
#     if st.button("🪹 Create New Database"):
#         response = requests.post("http://pdf_qa_backend:8000/upload-pdf/", files={"file": uploaded_file})
#         if response.status_code == 200:
#             st.success(response.json()["message"])
#         else:
#             st.error(response.json()["detail"])

#     if st.button("🪺 Update Existing Database"):
#         response = requests.post("http://pdf_qa_backend:8000/update-db/", files={"file": uploaded_file})
#         if response.status_code == 200:
#             st.success(response.json()["message"])
#         else:
#             st.error(response.json()["detail"])

# query = str(st.text_input("Enter your question about the PDF 🧑🏼‍💻"))

# if query:
#     response = requests.post("http://pdf_qa_backend:8000/query/", json={"question": query})
#     if response.status_code == 200:
#         response_json = response.json()
#         st.write("✍️", response_json.get("answer", "No answer provided"))

#         if "context" in response_json:
#             context = response_json["context"][0]
#             answer = context['answer']
#             source = context["metadata"].get("source", "Unknown Source")
#             page = context["metadata"].get("page", "Unknown Page")
#             best_paragraph = context.get("page_content", "No content available")
#             st.write(f"Response: {answer}\n")
#             st.write(f"\n📖 Source: {source}, Page: {page}\n")
#             st.write(f"Best Paragraph: {best_paragraph}\n")
#     else:
#         st.error("Failed to get the answer:\n", response)
