# Yojana Mitra

Yojana Mitra is an AI-powered offline assistant that helps users understand government welfare schemes by answering specific questions from uploaded documents instead of displaying the entire document.

The application allows users to upload scheme PDFs or images, ask questions using text or voice, and receive concise, context-aware answers with references to the source document.

## Features

- Upload PDF documents
- Upload scanned images
- OCR for scanned documents
- Text-based question answering
- Voice-based question answering
- Offline Large Language Model (LLM)
- Retrieval-Augmented Generation (RAG)
- Multilingual support
- Source citation
- Low-resource device compatibility

## Technology Stack

- Python
- Streamlit
- Ollama
- LangChain
- ChromaDB
- PyMuPDF
- EasyOCR
- Faster-Whisper
- Sentence Transformers

## Project Structure

```
yojana-mitra/
│
├── src/
├── data/
├── uploads/
├── outputs/
├── docs/
├── tests/
├── models/
├── README.md
├── CONTRIBUTING.md
├── USER_MANUAL.md
└── AGENTS.md
```

## Installation

```bash
git clone https://code.swecha.org/<username>/yojana-mitra.git

cd yojana-mitra

pip install -r requirements.txt
```

## Running

```bash
streamlit run app.py
```

## Team

- Akshaya Garela
- Project Partner

## License

This project is developed for educational and research purposes.