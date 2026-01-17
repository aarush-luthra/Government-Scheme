
# 🇮🇳 Government Scheme Assistant

A modern, AI-powered assistant designed to help Indian citizens discover and understand government schemes in their native languages. This system combines **Retrieval-Augmented Generation (RAG)** with **Multilingual Neural Machine Translation (NLLB-200)** to provide accurate, personalized answers in 14+ Indic languages.

## ✨ Features

### Core Capabilities
- **🌐 Multilingual Support** - Ask questions in Hindi, Tamil, Bengali, Marathi, and 11+ more Indian languages
- **🎯 Personalized Recommendations** - Get scheme suggestions based on your profile (age, location, category, employment status)
- **🧠 Conversational Memory** - Maintains context across messages for natural dialogue
- **📚 RAG-Powered Accuracy** - Retrieves information from curated government scheme documents
- **⚡ Real-time Translation** - Powered by Facebook's NLLB-200 model

### User Experience
- **🎨 Modern UI** - Clean, professional interface with dark/light mode support
- **📱 Responsive Design** - Works seamlessly on desktop and mobile devices
- **👤 User Profiles** - Create an account to save preferences and get personalized recommendations
- **🚶 Guest Mode** - Continue as a guest without signing up
- **🔤 Interface Translation** - The entire UI translates to your selected language

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python) |
| **Frontend** | HTML5, Vanilla JS, CSS3 |
| **LLM** | OpenAI GPT-4o-mini |
| **Vector Database** | FAISS |
| **Translation** | Facebook NLLB-200-distilled-600M |
| **Embeddings** | OpenAI text-embedding-3-small |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (Recommended: 3.12)
- OpenAI API Key

### Installation

```bash
# Clone the repository
git clone https://github.com/aarush-luthra/Government-Scheme.git
cd Government-Scheme

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Initial Setup (Database Generation)

Since the vector database is large, you must generate it locally after cloning:

```bash
python backend/ingestion/ingestion_runner.py
```

### Run the Application

```bash
python -m backend.app
```

Open your browser to: **[http://localhost:8000](http://localhost:8000)**

## 🌍 Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en_XX` | English | `hi_IN` | हिन्दी (Hindi) |
| `bn_IN` | বাংলা (Bengali) | `ta_IN` | தமிழ் (Tamil) |
| `te_IN` | తెలుగు (Telugu) | `mr_IN` | मराठी (Marathi) |
| `gu_IN` | ગુજરાતી (Gujarati) | `kn_IN` | ಕನ್ನಡ (Kannada) |
| `ml_IN` | മലയാളം (Malayalam) | `pa_IN` | ਪੰਜਾਬੀ (Punjabi) |
| `or_IN` | ଓଡ଼ିଆ (Odia) | `as_IN` | অসমীয়া (Assamese) |
| `ur_IN` | اردو (Urdu) | `ks_IN` | कॉशुर (Kashmiri) |
| `mai_IN` | मैथिली (Maithili) | `ne_IN` | नेपाली (Nepali) |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User (Browser)                        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Static    │  │    Auth     │  │    Chat     │     │
│  │   Files     │  │  Endpoints  │  │     API     │     │
│  └─────────────┘  └─────────────┘  └──────┬──────┘     │
└───────────────────────────────────────────┼─────────────┘
                                            │
            ┌───────────────────────────────┼───────────────────────┐
            │                               │                       │
            ▼                               ▼                       ▼
    ┌───────────────┐              ┌───────────────┐      ┌───────────────┐
    │  Translator   │              │  RAG Engine   │      │   User DB     │
    │  (NLLB-200)   │              │  (FAISS +     │      │   (SQLite)    │
    │               │              │   OpenAI)     │      │               │
    └───────────────┘              └───────────────┘      └───────────────┘
```

## 📂 Project Structure

```
Government-Scheme/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── nlp/
│   │   └── indicbart.py       # NLLB Translation wrapper
│   ├── rag/
│   │   ├── generator.py       # LLM response generation
│   │   ├── retriever.py       # Vector search logic (FAISS)
│   │   └── vector_store.py    # FAISS storage implementation
│   └── data/                  # Vector DB & scheme data
├── frontend/
│   ├── index.html             # Main chat interface
│   ├── style.css              # Modern styling (dark/light mode)
│   ├── script.js              # Chat logic & UI interactions
│   ├── signup.html            # User profile setup
│   └── login.html             # User login
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve main frontend |
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Main chat endpoint |
| `POST` | `/translate` | Translate single text |
| `POST` | `/translate/batch` | Translate multiple texts |
| `GET` | `/languages` | List supported languages |
| `POST` | `/profile` | Create user profile |
| `GET` | `/auth/me` | Get current user info |

## 🐛 Troubleshooting

### Common Issues

**1. `ModuleNotFoundError: No module named 'backend'`**
```bash
# Run from the project root directory using:
python -m backend.app
```

**2. Chatbot returns empty results**
- Ensure you have run the ingestion script:
```bash
python backend/ingestion/ingestion_runner.py
```

**3. Translation Model Download Stuck**
- The NLLB model is ~1.3GB. First run requires internet for download.
- Subsequent runs load from cache.

**4. `Address already in use` Error**
```bash
# Kill existing process on port 8000
lsof -ti :8000 | xargs kill -9
# On Windows, use Task Manager or Resource Monitor
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

MIT License - Built with ❤️ for the citizens of India 🇮🇳
