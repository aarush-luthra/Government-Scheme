# Government Scheme Assistant (Multilingual RAG)

A state-of-the-art AI assistant designed to help Indian citizens understand government schemes in their native languages. This system combines **Retrieval-Augmented Generation (RAG)** with **Multilingual Neural Machine Translation (NLLB-200)** to provide accurate, context-aware answers in 14+ Indic languages.

![UI Preview](docs/ui_preview.png)

## 🚀 Key Features

- **🗣️ Multilingual Support**: Speak in your native language (Hindi, Tamil, Bengali, Marathi, etc.) and get responses in the same language.
- **🧠 Conversational Memory**: Remembers context from previous messages (e.g., "What is it?" followed by "Who is eligible?").
- **📚 RAG Engine**: Retrieves accurate information from a curated knowledge base of government schemes (Vector Store).
- **✨ Modern UI**: A clean, professional, and responsive chat interface built with HTML5/CSS3.
- **🔗 Integrated Stack**: unified FastAPI backend serving both the REST API and the Frontend.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, Vanilla JS, CSS3 (Modern, Responsive)
- **LLM**: OpenAI GPT-4o-mini (Reasoning & Generation)
- **Vector DB**: ChromaDB (Semantic Search)
- **Translation**: `facebook/nllb-200-distilled-600M` (HuggingFace)
- **Embeddings**: OpenAI `text-embedding-3-small`

## 📋 Prerequisites

- **Python 3.10+** (Recommended: 3.12)
- **OpenAI API Key** (Required for RAG & Chat)

## ⚡ Quick Start

### 1. Clone & Set Up

```bash
git clone https://github.com/aarush-luthra/Government-Scheme.git
cd Government-Scheme

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Run the Application

Start the unified server (Frontend + Backend):

```bash
python -m backend.app
```

### 4. Use the Assistant

Open your browser to: **[http://localhost:8000](http://localhost:8000)**

## 🌐 Supported Languages

The system automatically detects and translates the following languages:

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en_XX` | English | `hi_IN` | Hindi |
| `bn_IN` | Bengali | `ta_IN` | Tamil |
| `te_IN` | Telugu | `mr_IN` | Marathi |
| `gu_IN` | Gujarati | `kn_IN` | Kannada |
| `ml_IN` | Malayalam | `pa_IN` | Punjabi |
| `or_IN` | Odia | `as_IN` | Assamese |
| `ne_IN` | Nepali | `ur_IN` | Urdu |

## 🏗️ Architecture

```
User (Browser) <--> FastAPI (Backend)
                        |
        +---------------+---------------+
        |                               |
  [Static Files]                  [API Routes]
   (HTML/JS/CSS)                        |
                                        v
                                 [Orchestrator]
                                        |
                   +--------------------+--------------------+
                   |                                         |
           [Translator Node]                          [RAG Node]
       (Facebook NLLB-200 Model)                 (ChromaDB + OpenAI)
```

## 📂 Project Structure

```
Government-Scheme/
├── backend/
│   ├── app.py                 # Main application entry point
│   ├── nlp/
│   │   └── indicbart.py       # NLLB Translation wrapper
│   ├── rag/
│   │   ├── generator.py       # LLM Response generation
│   │   ├── retriever.py       # Vector search logic
│   │   └── embeddings.py      # Embedding generation
│   └── data/                  # Scheme data & Vector DB
├── frontend/                  # Static assets
│   ├── index.html             # Main UI
│   ├── style.css              # Modern styling
│   └── script.js              # Chat logic
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🐛 Troubleshooting

**1. `ModuleNotFoundError: No module named 'backend'`**
- Make sure you run the app using `python -m backend.app` from the project root.

**2. Translation Model Download Stuck**
- The NLLB model is ~1.3GB. The first run will take time to download. Ensure you have a stable internet connection.

**3. `OpenAI Error`**
- Check if your `OPENAI_API_KEY` is set correctly in `.env`.

## 📜 License

MIT License. Built for the citizens of India. 🇮🇳