# Government Scheme RAG Pipeline

A complete Retrieval-Augmented Generation (RAG) system for querying Indian Government Schemes using OpenAI API and ChromaDB vector search.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This RAG pipeline enables intelligent querying of government scheme data by:
1. Scraping scheme information from MyScheme website
2. Processing and chunking the data
3. Generating embeddings using OpenAI
4. Storing in ChromaDB vector database
5. Retrieving relevant information based on semantic search
6. Generating natural language responses using GPT-4

## 🏗️ Architecture

```
┌─────────────────┐
│  Data Sources   │
│  (MyScheme)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Web Scraper    │
│  (Selenium)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Processing │
│  & Chunking     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   OpenAI API    │
│   Embeddings    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ChromaDB      │
│ Vector Store    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Retrieval     │
│ (Top-K Search)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OpenAI GPT-4   │
│   Generation    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI REST   │
│      API        │
└─────────────────┘
```

## ✅ Prerequisites

### Required Software (Mac)
- **Python 3.9+** (check: `python3 --version`)
- **Google Chrome** (for web scraping)
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **VS Code** (recommended)

### Check Python Installation
```bash
python3 --version  # Should be 3.9 or higher
pip3 --version     # Should be available
```

### Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## 🚀 Installation

### Step 1: Clone/Navigate to Project Directory

```bash
cd ~/path/to/Government-Scheme-1
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your terminal should now show (venv) prefix
```

**Note**: Always activate the virtual environment before working on the project!

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (Web framework)
- OpenAI (API client)
- ChromaDB (Vector database)
- Selenium & BeautifulSoup (Web scraping)
- Other utilities

**Installation may take 5-10 minutes**

### Step 4: Install Chrome Driver

The web scraper uses Selenium with Chrome. The `webdriver-manager` package will automatically download the correct ChromeDriver when you first run the script.

Just make sure **Google Chrome is installed** on your Mac.

## ⚙️ Configuration

### Step 1: Create Environment File

```bash
# Copy the example file
cp .env.example .env

# Open in VS Code
code .env

# Or use nano
nano .env
```

### Step 2: Add Your OpenAI API Key

Edit the `.env` file and add your API key:

```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

**Get your API key**: https://platform.openai.com/api-keys

### Step 3: Verify Configuration

All other settings have sensible defaults:
- Embedding Model: `text-embedding-3-small`
- LLM Model: `gpt-4-turbo-preview`
- Chunk Size: 1000 characters
- Chunk Overlap: 200 characters
- Vector DB: `./data/chroma_db`

You can modify these in `.env` if needed.

## 📊 Usage

### 1️⃣ Ingest Government Scheme Data

This step scrapes schemes from MyScheme website and stores them in the vector database.

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Ingest 10 schemes (recommended for testing)
python backend/test_ingestion.py --limit 10

# Ingest more schemes
python backend/test_ingestion.py --limit 20

# Reset database and ingest fresh data
python backend/test_ingestion.py --limit 10 --reset
```

**Expected Output**:
```
======================================================================
GOVERNMENT SCHEME DATA INGESTION PIPELINE
======================================================================
Configuration:
  • Chunk Size: 1000
  • Chunk Overlap: 200
  • Embedding Model: text-embedding-3-small
  • Storage: ./data/chroma_db
======================================================================

[Step 1/6] Initializing components...
✓ Loaded existing collection: government_schemes
  Documents in collection: 0

[Step 2/6] Using existing vector database

[Step 3/6] Loading schemes from MyScheme website (limit: 10)...
============================================================
Loading Government Schemes from MyScheme Website
============================================================

Step 1: Fetching scheme list...
...

======================================================================
INGESTION COMPLETE ✓
======================================================================
Collection: government_schemes
Total Schemes: 10
Total Document Chunks: 45
Storage Location: ./data/chroma_db
Embedding Model: text-embedding-3-small
======================================================================
```

**Note**: 
- First run may take longer (5-10 minutes for 10 schemes)
- Data is scraped from the web + enhanced with sample data
- Embeddings are generated using OpenAI API (costs ~$0.01-0.02 for 10 schemes)

### 2️⃣ Start the API Server

```bash
# Make sure virtual environment is active
source venv/bin/activate

# Start the server
python backend/app.py
```

**Expected Output**:
```
======================================================================
STARTING GOVERNMENT SCHEME RAG API SERVER
======================================================================
Host: 0.0.0.0
Port: 8000
Debug: True
Docs: http://localhost:8000/docs
======================================================================

Initializing RAG components...
✓ Loaded existing collection: government_schemes
  Documents in collection: 45
✓ RAG components initialized

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The server is now running! Keep this terminal open.

### 3️⃣ Test the API

Open a **new terminal** window/tab:

#### Option A: Using `curl`

```bash
# Test health check
curl http://localhost:8000/health

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is PM-KISAN scheme?",
    "top_k": 5
  }'

# Test with category filter
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "schemes for farmers",
    "category": "Agriculture"
  }'

# Get statistics
curl http://localhost:8000/stats
```

#### Option B: Using Python

Create a test file `test_api.py`:

```python
import requests
import json

# Test query
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What schemes are available for farmers?",
        "top_k": 5
    }
)

result = response.json()
print("Question:", result['query'])
print("\nAnswer:", result['answer'])
print(f"\nSources: {len(result['sources'])} documents")

for i, source in enumerate(result['sources'][:3], 1):
    print(f"\n{i}. {source['title']}")
    print(f"   Category: {source['category']}")
    print(f"   Relevance: {source['relevance_score']}")
```

Run it:
```bash
python test_api.py
```

#### Option C: Interactive API Documentation

Open your browser and go to:
```
http://localhost:8000/docs
```

This provides an interactive interface where you can test all endpoints!

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. **GET /** - Root
Get API information

```bash
curl http://localhost:8000/
```

#### 2. **GET /health** - Health Check
Check if the API is running

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "vector_store": "connected",
  "document_count": 45
}
```

#### 3. **GET /stats** - Statistics
Get database statistics

```bash
curl http://localhost:8000/stats
```

Response:
```json
{
  "collection_name": "government_schemes",
  "document_count": 45,
  "persist_directory": "./data/chroma_db",
  "embedding_model": "text-embedding-3-small",
  "llm_model": "gpt-4-turbo-preview",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

#### 4. **POST /query** - Query Knowledge Base
Ask questions about government schemes

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Ayushman Bharat scheme?",
    "top_k": 5,
    "category": "Health"
  }'
```

Request Body:
```json
{
  "query": "What schemes help farmers?",  // Required
  "top_k": 5,                             // Optional (default: 5)
  "category": "Agriculture"               // Optional filter
}
```

Response:
```json
{
  "query": "What schemes help farmers?",
  "answer": "Several schemes help farmers in India...",
  "sources": [
    {
      "title": "PM-KISAN",
      "department": "Ministry of Agriculture",
      "category": "Agriculture",
      "relevance_score": 0.892,
      "content_preview": "Income support scheme...",
      "url": "https://pmkisan.gov.in"
    }
  ],
  "metadata": {
    "retrieved_count": 5,
    "top_k": 5,
    "category_filter": "Agriculture"
  }
}
```

#### 5. **POST /retrieve** - Retrieve Documents
Get relevant documents without LLM generation

```bash
curl -X POST http://localhost:8000/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "health insurance schemes",
    "top_k": 3
  }'
```

#### 6. **GET /categories** - Get Categories
Get list of available scheme categories

```bash
curl http://localhost:8000/categories
```

#### 7. **POST /add_documents** - Add Documents
Add custom documents to the database

```bash
curl -X POST http://localhost:8000/add_documents \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["New scheme description..."],
    "metadatas": [{"title": "New Scheme", "category": "Finance"}]
  }'
```

#### 8. **POST /reset** - Reset Database
⚠️ **WARNING**: Deletes all data!

```bash
curl -X POST http://localhost:8000/reset
```

## 🔧 Project Structure

```
Government-Scheme-1/
├── backend/
│   ├── config/
│   │   └── settings.py              # Configuration
│   ├── ingestion/
│   │   └── __pycache__/
│   │       └── myscheme_loader.py   # Web scraper
│   ├── rag/
│   │   ├── embeddings.py            # OpenAI embeddings
│   │   ├── generator.py             # Response generation
│   │   └── retriever.py             # Vector store
│   ├── app.py                       # FastAPI app
│   └── test_ingestion.py            # Ingestion script
├── data/
│   ├── chroma_db/                   # Vector database
│   └── ingested_schemes.json        # Raw scheme data
├── venv/                            # Virtual environment
├── .env                             # Environment variables (DO NOT COMMIT)
├── .env.example                     # Example env file
├── .gitignore                       # Git ignore file
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🐛 Troubleshooting

### Issue 1: ModuleNotFoundError

**Problem**:
```
ModuleNotFoundError: No module named 'openai'
```

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: OpenAI API Key Error

**Problem**:
```
Error: Invalid API key
```

**Solution**:
1. Check your `.env` file has the correct key
2. Make sure there are no spaces around the `=` sign
3. Verify the key at https://platform.openai.com/api-keys
4. Restart the server after updating `.env`

### Issue 3: Chrome Driver Error

**Problem**:
```
selenium.common.exceptions.WebDriverException
```

**Solution**:
```bash
# Make sure Chrome is installed
open -a "Google Chrome"

# Reinstall webdriver-manager
pip install --upgrade webdriver-manager
```

### Issue 4: Port Already in Use

**Problem**:
```
Error: Address already in use
```

**Solution**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
# Edit .env and change APP_PORT=8001
```

### Issue 5: Permission Denied (ChromaDB)

**Problem**:
```
PermissionError: [Errno 13] Permission denied: './data/chroma_db'
```

**Solution**:
```bash
# Fix permissions
chmod -R 755 data/

# Or delete and recreate
rm -rf data/chroma_db
python backend/test_ingestion.py --limit 10
```

### Issue 6: Virtual Environment Not Found

**Problem**:
```
source: venv/bin/activate: No such file or directory
```

**Solution**:
```bash
# Create new virtual environment
python3 -m venv venv

# Then activate and install
source venv/bin/activate
pip install -r requirements.txt
```

## 💡 Tips for Mac Users

### 1. Using VS Code Terminal
```bash
# Open VS Code in project directory
code .

# Use integrated terminal: Terminal → New Terminal
# Or use keyboard shortcut: Control + `
```

### 2. Running in Background
```bash
# Run server in background
nohup python backend/app.py > server.log 2>&1 &

# View logs
tail -f server.log

# Stop server
pkill -f "python backend/app.py"
```

### 3. Auto-activate Virtual Environment
Add to your `~/.zshrc` or `~/.bash_profile`:
```bash
# Auto-activate venv when entering project directory
cd() {
  builtin cd "$@"
  if [[ -d ./venv ]]; then
    source ./venv/bin/activate
  fi
}
```

## 📈 Cost Estimation

OpenAI API costs (approximate):

**Embeddings** (text-embedding-3-small):
- $0.00002 per 1K tokens
- 10 schemes ≈ 20K tokens ≈ $0.40
- 50 schemes ≈ 100K tokens ≈ $2.00

**Generation** (gpt-4-turbo-preview):
- $0.01 per 1K input tokens
- $0.03 per 1K output tokens
- Average query ≈ $0.02-0.05

**Total for testing** (10 schemes + 20 queries):
- Embedding: $0.40
- Queries: $0.60
- **Total: ~$1.00**

## 🎓 Example Queries

Try these queries to test the system:

```python
queries = [
    "What is PM-KISAN and who can apply?",
    "Tell me about health insurance schemes",
    "What schemes are available for women?",
    "How do I apply for housing schemes?",
    "What documents are needed for farmer schemes?",
    "Which schemes provide financial assistance?",
    "What is Ayushman Bharat scheme?",
    "Are there any schemes for students?",
    "What benefits does PM Ujjwala Yojana provide?",
    "How can I get a loan under MUDRA scheme?"
]
```

## 🔐 Security Notes

1. **Never commit `.env` file** - It contains your API key
2. **.gitignore is configured** - `.env` is already excluded
3. **Use environment variables** for all secrets
4. **Rotate API keys** regularly
5. **Monitor API usage** at OpenAI dashboard

## 🚀 Next Steps

1. **Add More Data Sources**
   - PDF documents from government websites
   - Excel files with scheme data
   - Official circulars and notifications

2. **Improve Retrieval**
   - Implement hybrid search (keyword + semantic)
   - Add re-ranking
   - Use metadata filtering more extensively

3. **Build Frontend**
   - React web app
   - Mobile app
   - Chatbot interface

4. **Deploy to Production**
   - Docker containerization
   - Deploy to AWS/GCP/Azure
   - Add monitoring and logging
   - Implement caching

## 📞 Support

For issues:
1. Check this README
2. Review the troubleshooting section
3. Check OpenAI documentation
4. Check ChromaDB documentation

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for making government schemes accessible to all citizens**