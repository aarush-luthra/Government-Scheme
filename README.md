# 🇮🇳 Government Scheme Assistant

> *Empowering Indian citizens to discover and understand government schemes in their native language*

A powerful **Multilingual AI Assistant** built with **RAG (Retrieval-Augmented Generation)** that helps citizens navigate 100+ government welfare schemes. Ask questions in Hindi, Tamil, Bengali, or 11 other languages — and get accurate, context-aware responses.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **14+ Languages** | Full support for Indic languages via NLLB-200 neural translation |
| 🧠 **Smart Context** | Conversational memory maintains context across messages |
| 📚 **RAG-Powered** | Retrieves accurate info from a curated knowledge base |
| 👤 **User Profiles** | Personalized scheme recommendations based on your profile |
| 🔐 **Authentication** | Secure signup/login with session management |
| 📄 **PDF Ingestion** | Ingest scheme documents with semantic chunking |
| ✨ **Modern UI** | Clean, responsive interface with real-time chat |

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND          │  HTML5 • CSS3 • Vanilla JavaScript │
├────────────────────┼────────────────────────────────────┤
│  BACKEND           │  FastAPI (Python 3.10+)            │
├────────────────────┼────────────────────────────────────┤
│  LLM               │  OpenAI GPT-4o-mini                │
├────────────────────┼────────────────────────────────────┤
│  VECTOR DB         │  ChromaDB                          │
├────────────────────┼────────────────────────────────────┤
│  EMBEDDINGS        │  OpenAI text-embedding-3-small     │
├────────────────────┼────────────────────────────────────┤
│  TRANSLATION       │  facebook/nllb-200-distilled-600M  │
└────────────────────┴────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10+** (recommended: 3.12)
- OpenAI API Key

### 1. Clone & Install

```bash
git clone https://github.com/aarush-luthra/Government-Scheme.git
cd Government-Scheme

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Run

```bash
python -m backend.app
```

Open **http://localhost:8000** in your browser.

---

## 🌐 Supported Languages

<table>
<tr><td><b>Hindi</b> (hi_IN)</td><td><b>Bengali</b> (bn_IN)</td><td><b>Tamil</b> (ta_IN)</td><td><b>Telugu</b> (te_IN)</td></tr>
<tr><td><b>Marathi</b> (mr_IN)</td><td><b>Gujarati</b> (gu_IN)</td><td><b>Kannada</b> (kn_IN)</td><td><b>Malayalam</b> (ml_IN)</td></tr>
<tr><td><b>Punjabi</b> (pa_IN)</td><td><b>Odia</b> (or_IN)</td><td><b>Assamese</b> (as_IN)</td><td><b>Nepali</b> (ne_IN)</td></tr>
<tr><td><b>Urdu</b> (ur_IN)</td><td><b>English</b> (en_XX)</td><td colspan="2"></td></tr>
</table>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│             (HTML/CSS/JS @ localhost:8000)                   │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTP
┌─────────────────────────▼────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │    Auth      │  │  Translator  │  │   RAG Pipeline   │    │
│  │   Module     │  │   (NLLB-200) │  │                  │    │
│  └──────────────┘  └──────────────┘  │ ┌──────────────┐ │    │
│                                      │ │  Retriever   │ │    │
│                                      │ │  (ChromaDB)  │ │    │
│                                      │ ├──────────────┤ │    │
│                                      │ │  Generator   │ │    │
│                                      │ │  (OpenAI)    │ │    │
│                                      │ └──────────────┘ │    │
│                                      └──────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
Government-Scheme/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── auth.py             # Authentication logic
│   ├── database.py         # Session & user management
│   ├── config/             # Configuration settings
│   ├── nlp/
│   │   └── indicbart.py    # NLLB translation wrapper
│   ├── rag/
│   │   ├── generator.py    # LLM response generation
│   │   ├── retriever.py    # Vector search
│   │   ├── embeddings.py   # Embedding generation
│   │   └── vector_store.py # ChromaDB interface
│   ├── ingestion/
│   │   ├── pdf_loader.py   # PDF document loader
│   │   ├── chunker.py      # Text chunking
│   │   └── normalizer.py   # Text normalization
│   └── data/               # Vector DB & scheme data
├── frontend/
│   ├── index.html          # Main UI
│   ├── style.css           # Styling
│   └── script.js           # Chat logic
├── data/                    # Raw scheme documents
├── requirements.txt
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Serve frontend |
| `GET`  | `/health` | Health check |
| `POST` | `/api/chat` | Send message to assistant |
| `POST` | `/api/translate` | Translate text |
| `POST` | `/api/batch-translate` | Batch translation |
| `GET`  | `/api/languages` | List supported languages |
| `POST` | `/api/auth/signup` | Register new user |
| `POST` | `/api/auth/login` | User login |
| `POST` | `/api/auth/logout` | User logout |
| `GET`  | `/api/auth/me` | Get current session |
| `POST` | `/api/profile` | Save user profile |

---

## 🐛 Troubleshooting

<details>
<summary><b>ModuleNotFoundError: No module named 'backend'</b></summary>

Always run from the project root:
```bash
python -m backend.app
```
</details>

<details>
<summary><b>Translation model download stuck</b></summary>

The NLLB model is ~1.3GB. First launch may take 5-10 minutes to download. Ensure stable internet.
</details>

<details>
<summary><b>OpenAI API errors</b></summary>

- Check `.env` file has correct `OPENAI_API_KEY`
- Verify your API key has sufficient credits
</details>

<details>
<summary><b>ChromaDB errors</b></summary>

If vector store is corrupted, delete `backend/data/chroma_db/` and re-run ingestion.
</details>

---

## 📥 Adding New Schemes

1. Add PDF documents to the `data/` folder
2. Run the ingestion pipeline:

```bash
python -m backend.ingestion.pdf_ingestion_runner
```

The pipeline will:
- Extract text from PDFs
- Chunk into semantic segments
- Generate embeddings
- Store in ChromaDB (with deduplication)

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📜 License

MIT License • Built with ❤️ for the citizens of India 🇮🇳
