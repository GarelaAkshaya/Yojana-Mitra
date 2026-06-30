# Yojana Mitra User Manual

## Introduction

Yojana Mitra helps users quickly obtain answers from government scheme documents without reading the entire document.

---

## Requirements

- Python 3.11+
- Ollama installed
- Internet only required for initial model download

---

## Installation

Clone the repository.

```bash
git clone https://code.swecha.org/<username>/yojana-mitra.git
```

Install dependencies.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

For OCR, voice transcription, local embeddings, and local LLM answers, install
the full offline stack:

```bash
.venv/bin/python -m pip install -r requirements-full.txt
```

---

## Launch Application

```bash
.venv/bin/streamlit run frontend/app.py
```

---

## Using the Application

### Step 1

Open the application in your browser.

### Step 2

Upload a PDF or image.

### Step 3

Wait until processing completes.

### Step 4

Ask your question using

- Text
- Voice

### Step 5

Read the generated answer.

The answer includes:

- Relevant information
- Source page
- Confidence (if implemented)

---

## Supported Formats

- PDF
- JPG
- PNG
- JPEG

---

## Features

- OCR
- Voice input
- Offline AI
- Semantic search
- Multilingual support

---

## Troubleshooting

### Model not responding

Ensure Ollama is running.

### PDF not loading

Check if the file is corrupted.

### Voice not working

Verify microphone permissions.

---

## Contact

For issues, create an issue in the project repository.
