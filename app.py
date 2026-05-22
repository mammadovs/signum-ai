import streamlit as st
import google.generativeai as genai
import pypdf
import os
from dotenv import load_dotenv

load_dotenv()

# API setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# System prompt for AI to behave like a legal assistant
LEGAL_PROMPT = """
You are a qualified legal AI assistant.

Your task is to analyze provided documents and answer user questions strictly based on the document text.

If the document does not contain an answer, honestly say so. Highlight important risks, deadlines, and obligations of the parties.

Respond in a structured format using lists.
"""

st.set_page_config(page_title="Signum AI", page_icon="⚖️")

st.title("⚖️ Signum AI")

# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

# Sidebar for document upload
with st.sidebar:
    st.header("Document Upload")

    uploaded_file = st.file_uploader(
        "Upload a contract or agreement (PDF)",
        type=["pdf"]
    )

    if uploaded_file and not st.session_state.doc_text:
        with st.spinner("Analyzing document..."):
            reader = pypdf.PdfReader(uploaded_file)
            text = ""

            for page in reader.pages:
                text += page.extract_text() + "\n"

            st.session_state.doc_text = text
            st.success("Document successfully uploaded and processed!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input field
if user_input := st.chat_input("Ask a question about the document (e.g., What are the risks?):"):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build context for the model
    context = (
        f"Document context:\n{st.session_state.doc_text}\n\nQuestion: {user_input}"
        if st.session_state.doc_text
        else user_input
    )

    # LLM request
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",  # fast and cheap for hackathons
                    system_instruction=LEGAL_PROMPT
                )

                response = model.generate_content(context)
                output_text = response.text

                st.markdown(output_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": output_text}
                )

            except Exception as e:
                st.error(f"API error: {e}")

