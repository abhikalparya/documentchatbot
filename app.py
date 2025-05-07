import logging
import os
import uuid

import streamlit as st
from dotenv import load_dotenv

from chatbot import get_conversational_rag_chain, history, set_up_vectordb
from process_data import process_pdf

load_dotenv()

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def set_up(dbname, file=None):
    bar = st.progress(0, text="Processing PDF...")

    logger.info(f"SET_UP: {dbname}, {file}")

    if file:
        logger.info("SET_UP: Processing PDF")
        docs = process_pdf(file)
    else:
        docs = None

    bar.progress(0.33, text="Setting up Chroma Vector DB...")

    logger.info("SET_UP: Setting up Chroma Vector DB")
    retriever = set_up_vectordb(dbname=dbname, docs=docs)

    bar.progress(0.66, text="Setting up the conversational RAG chain...")

    logger.info("SET_UP: Setting up the conversational RAG chain")
    rag_chain = get_conversational_rag_chain(retriever)

    bar.progress(1.0, text="Done!")
    return rag_chain


def get_vector_store_name(filename):
    for k in st.session_state.uploaded_docs:
        if k[0] == filename:
            return k[1]
    return None


def get_filename_from_vector_store(dbname):
    for k in st.session_state.uploaded_docs:
        if k[1] == dbname:
            return k[0]
    return None


def callback():
    """Callback function for the file uploader, sets the selected document and updates loaded vector store."""
    filename = st.session_state["file_uploader"].name
    st.session_state.selected_doc = filename
    
    dbname = get_vector_store_name(filename)
    if dbname:
        st.session_state.loaded_vector_store = dbname
    return


api_key = os.getenv("GOOGLE_API_KEY")

if "uploaded_docs" not in st.session_state:
    st.session_state["uploaded_docs"] = []

if "loaded_vector_store" not in st.session_state:
    st.session_state["loaded_vector_store"] = None

if "selected_doc" not in st.session_state:
    st.session_state["selected_doc"] = None

if "rag_chain" not in st.session_state:
    st.session_state["rag_chain"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! How can I help you?"}
    ]

logger.info(f"uploaded_docs: {st.session_state.uploaded_docs}")
logger.info(f"loaded_vector_store: {st.session_state.loaded_vector_store}")
logger.info(f"selected_doc: {st.session_state.selected_doc}")

st.title("💬 Document Chatbot")

uploaded_file = st.file_uploader(
    "Upload a PDF", type=("pdf"), key="file_uploader", on_change=callback
)

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


logger.info(f"uploaded_file: {uploaded_file}")
if uploaded_file:
    if not api_key:
        st.info("Please add your GCP API key to continue.")
        st.stop()

    filename = uploaded_file.name

    if filename not in [doc[0] for doc in st.session_state.uploaded_docs]:
        logger.info(
            "File is not in the uploaded docs list. Setting up the vector store."
        )
        dbname = uuid.uuid4().hex
        st.session_state.uploaded_docs.append((filename, dbname))
        rag_chain = set_up(dbname=dbname, file=uploaded_file)
        st.session_state.loaded_vector_store = dbname
        st.session_state.rag_chain = rag_chain
        # Clear chat history when loading a new document
        history.clear()
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hello! I've loaded {filename}. How can I help you?"}
        ]
        st.rerun()

        logger.info(f"new uploaded_docs: {st.session_state.uploaded_docs}")
        logger.info(f"new loaded_vector_store: {st.session_state.loaded_vector_store}")
        logger.info(f"new selected_doc: {st.session_state.selected_doc}")
        logger.info(f"dbname: {dbname}")

if st.session_state.selected_doc and st.session_state.selected_doc != get_filename_from_vector_store(
    st.session_state.loaded_vector_store
):
    logger.info("Selected document's vector store is not loaded. Loading it.")
    logger.info(f"selected_doc: {st.session_state.selected_doc}")
    logger.info(f"loaded_vector_store: {st.session_state.loaded_vector_store}")
    
    # Get the vector store name for the selected document
    dbname = get_vector_store_name(st.session_state.selected_doc)
    if dbname:
        st.session_state.loaded_vector_store = dbname
        st.session_state.rag_chain = set_up(dbname=dbname)
        # Clear chat history when switching documents
        history.clear()
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hello! I've loaded {st.session_state.selected_doc}. How can I help you?"}
        ]
        st.rerun()


logging.info(f"\n history: \n {history} \n")

if prompt := st.chat_input(
    placeholder="Can you give me a short summary?", disabled=not uploaded_file
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Make sure we have a RAG chain
    if st.session_state.rag_chain:
        response = st.session_state.rag_chain.invoke(
            {"input": prompt},
            config={"configurable": {"session_id": "0"}},
        )["answer"]

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
    else:
        error_msg = "Please select a document first."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.chat_message("assistant").write(error_msg)
