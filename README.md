
# 📄 Document Chatbot

An interactive document-based chatbot built with [Streamlit](https://streamlit.io/), [LangChain](https://www.langchain.com/), and [Google's Gemini LLM](https://ai.google/discover/gemini/). Upload a PDF and chat with it to get contextual answers using a Conversational RAG (Retrieval-Augmented Generation) pipeline.

---

## 🚀 Features

- 📤 Upload and interact with your PDFs  
- 🧠 Uses Google's Gemini 1.5 Pro for intelligent responses  
- 🔍 Context-aware question reformulation  
- 🧾 Chat history memory for continuity  
- 🗃️ Persistent Chroma vector store for embeddings  
- 🔐 Environment-configured API key support  

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/document-chatbot.git
cd document-chatbot
```

### 2. Install dependencies

Make sure you have Python 3.10+, then run:

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory and add your Google API Key:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📦 Dependencies

- `streamlit`  
- `langchain`  
- `langchain_community`  
- `langchain_chroma`  
- `langchain_google_genai`  
- `python-dotenv`  
- `PyMuPDF`  

Install all with:

```bash
pip install -r requirements.txt
```

---

## 🧠 How It Works

1. User uploads a PDF via Streamlit.  
2. The PDF is parsed and split into text chunks.  
3. Text chunks are embedded using Google's `text-embedding-004` model.  
4. Chroma stores these embeddings and serves as a retriever.  
5. User inputs are reformulated to standalone questions (if necessary).  
6. Relevant document chunks are retrieved.  
7. Gemini LLM answers the question with in-context documents.  
8. Chat history ensures continuity of conversation.  

---

## 📌 Notes

- Each uploaded document is tied to a UUID-based vector store.  
- Only PDFs are supported currently.  
- Make sure your `.env` file includes the correct Google API key for Gemini and embeddings.  


