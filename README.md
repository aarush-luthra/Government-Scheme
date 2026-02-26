
# Government Scheme Assistant

An AI-powered platform that helps Indian citizens discover, understand, and track government welfare schemes in any of 16 supported Indian languages.

---

## Problem Statement

India operates one of the world's largest social welfare ecosystems, with thousands of central and state government schemes addressing education, healthcare, housing, employment, agriculture, and more. Yet millions of eligible citizens fail to benefit because of:

- Language barriers -- official documentation is overwhelmingly in English or bureaucratic Hindi
- No single, citizen-facing platform that surfaces relevant schemes based on individual profile attributes
- Information overload across government portals with dense legal language
- No proactive deadline alerts or tracking mechanisms

---

## Features

### Multilingual Conversational AI
- Chat in Hindi, Tamil, Bengali, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu, Kashmiri, Maithili, Nepali, or English
- Automatic language detection with response in the same language via Facebook NLLB-200
- Profile-aware scheme retrieval using RAG (Retrieval-Augmented Generation) over 19,000+ scheme documents
- Conversational memory within sessions for contextual follow-up questions

### User Management and Authentication
- Profile creation with guided form (gender, age, state, category, employment, income, disability status)
- Guest mode with 3 free messages before sign-in required
- JWT-based authentication with HTTP-only session cookies
- JWT refresh token mechanism (`POST /auth/refresh`) for session renewal without re-authentication

### Document Intelligence (OCR)
- Auto-fill profile from Aadhaar, PAN, or other ID documents via EasyOCR + Tesseract
- PDF support through pdf2image conversion
- Multi-document upload with sequential processing and data merge

### Scheme Saving and Tracking
- Save schemes from chat to a personal dashboard (`/saved.html`)
- Deadline reminders and alert subscriptions for scheme categories
- PDF export of saved schemes with jsPDF (including statuses, deadlines, and reminders)
- Pagination on `/api/v1/saved-dashboard` with `limit` and `offset` query parameters

### Admin Dashboard
- KPI cards: total searches, saved schemes, failed comparisons, alert success rate
- Chart.js visualizations: horizontal bar chart for feature usage breakdown, doughnut chart for alert delivery rates
- Ingestion health monitoring (source coverage, parser confidence, broken links)
- Background task failure log
- Manual alert dispatch trigger

---

## Technical Features

### Security

**Rate Limiting (slowapi)**
API endpoints are rate-limited using slowapi with `get_remote_address` for client identification:
- `/chat` -- 10 requests/minute
- `/auth/login` -- 5 requests/minute
- `/profile` -- 5 requests/minute
- `/translate` -- 20 requests/minute

**XSS Protection (DOMPurify)**
All markdown rendered via `marked.parse()` is sanitized through DOMPurify before DOM injection. The `sanitizeHTML()` wrapper in `script.js` prevents script injection in chat responses.

**JWT Refresh Tokens**
Login returns both an `access_token` (2-hour TTL) and a `refresh_token` (7-day TTL). The frontend automatically attempts token refresh on 401 responses before prompting re-authentication. Refresh tokens are signed with a separate secret suffix.

### Performance

**In-Memory TTL Cache**
An in-memory cache (`_API_CACHE`) with configurable TTL is applied to frequently accessed endpoints:
- `/schemes/search` and `/autosuggest` -- 60-second TTL
- `/translate` and `/translate/batch` -- 120-second TTL
- `_build_scheme_catalog()` -- 60-second TTL for filesystem scan results

Cache keys incorporate request parameters (query, language codes, profile hints) to prevent stale cross-user results.

**WebSocket Streaming (`/ws/chat`)**
A WebSocket endpoint streams chat responses word-by-word for a typewriter effect. The frontend client (`sendViaWebSocket`) creates a persistent connection with automatic reconnection (exponential backoff, max 5 retries). Falls back to standard HTTP POST if WebSocket is unavailable.

### Progressive Web App (PWA)

**Service Worker (`sw.js`)**
- Cache-first strategy for static assets (HTML, CSS, JS, fonts)
- Network-first strategy for API calls with cache fallback for offline access
- Saved dashboard responses are cached for offline viewing
- Navigation fallback to `/index.html` when offline

**Web App Manifest (`manifest.json`)**
- Standalone display mode with theme color `#047857`
- Installable on mobile home screens

### Database and Schema Management

**Alembic Migrations**
Schema versioning is managed through Alembic rather than inline `CREATE TABLE IF NOT EXISTS`:
- `alembic.ini` -- configuration pointing to SQLite database
- `migrations/env.py` -- online/offline migration support
- `migrations/versions/001_initial_schema.py` -- baseline migration stamping the existing schema
- New migrations are generated via `alembic revision --autogenerate -m "description"`

### Observability

**Enhanced Health Check (`GET /health`)**
Returns per-component status with HTTP 200 (healthy) or 503 (degraded):
```json
{
    "status": "healthy",
    "service": "Government Scheme Assistant",
    "components": {
        "sqlite": { "status": "ok" },
        "faiss": { "status": "ok", "documents_accessible": true },
        "translator": { "status": "ok", "languages": 16 }
    }
}
```

### Frontend

**Toast Notification System**
User-facing toast notifications replace silent `console.error` calls and `alert()` popups. Toasts support three types (error, success, warning) with slide-in animation, auto-dismiss after 4 seconds, and manual close button.

**PDF Export (jsPDF)**
The saved schemes dashboard includes an "Export PDF" button that generates a formatted PDF containing scheme names, statuses, deadlines, and reminders.

**Chart.js Analytics**
The admin dashboard renders two interactive charts:
- Feature usage horizontal bar chart (searches, saves, compares, autosuggest, checklists)
- Alert delivery doughnut chart (delivered vs. failed)

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend Framework | FastAPI (Python 3.12) | Async HTTP server with WebSocket support |
| Frontend | HTML5, Vanilla JS, CSS3 | No framework dependencies |
| Language Model | OpenAI GPT-4o-mini | Response generation from retrieved context |
| Vector Database | FAISS | Approximate nearest-neighbor search over 19K+ embeddings |
| Embeddings | OpenAI text-embedding-3-small | 1536-dimension dense vectors |
| Translation | Facebook NLLB-200 (distilled-600M) | Bi-directional translation, 16 Indian languages |
| Database | SQLite + Alembic | User data storage with versioned migrations |
| OCR | EasyOCR + Tesseract + pdf2image | Structured data extraction from ID documents |
| Auth | JWT + bcrypt + HTTP-only cookies | Token-based auth with refresh mechanism |
| Rate Limiting | slowapi | Per-endpoint request throttling |
| Caching | In-memory TTL cache | Reduced database and filesystem load |
| PDF Generation | jsPDF | Client-side PDF export |
| Charts | Chart.js 4.x | Admin analytics visualizations |
| PWA | Service Worker + manifest.json | Offline support and installability |

---

## Project Structure

```
Government-Scheme/
├── backend/
│   ├── app.py                 # FastAPI application, routes, middleware, chat logic
│   ├── auth.py                # JWT access/refresh token creation and validation
│   ├── database.py            # SQLite operations (users, sessions, schemes, reminders)
│   ├── notifications.py       # Alert dispatch and notification tracking
│   ├── config/                # Configuration management
│   ├── routes/
│   │   └── ocr_routes.py      # OCR upload and processing endpoints
│   ├── ocr/                   # EasyOCR, Tesseract, PDF processing pipeline
│   ├── nlp/
│   │   └── indicbart.py       # NLLB-200 translation wrapper (INT8 quantized)
│   ├── rag/
│   │   ├── generator.py       # GPT-4o response generation
│   │   ├── retriever.py       # Profile-aware FAISS vector search
│   │   └── vector_store.py    # FAISS index management
│   ├── ingestion/             # Scheme data ingestion pipelines
│   ├── worker/                # Background task runner
│   ├── data/                  # Vector DB files, scheme JSON documents
│   └── user_data/             # SQLite database (user.db)
│
├── frontend/
│   ├── index.html             # Landing page and chat interface
│   ├── style.css              # Design system (tokens, components, responsive, toasts)
│   ├── script.js              # Core logic (auth, chat, WebSocket, toasts, i18n)
│   ├── translations.js        # UI string translations for 16 languages
│   ├── saved.html             # Saved schemes dashboard with PDF export
│   ├── admin.html             # Admin dashboard with Chart.js analytics
│   ├── sw.js                  # Service Worker (PWA offline support)
│   └── manifest.json          # PWA web app manifest
│
├── migrations/
│   ├── env.py                 # Alembic environment configuration
│   ├── script.py.mako         # Migration template
│   └── versions/
│       └── 001_initial_schema.py  # Baseline migration
│
├── tests/                     # Integration and unit tests
├── alembic.ini                # Alembic configuration
├── requirements.txt           # Python dependencies
└── README.md
```

---

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ (recommended 3.12) | Required |
| OpenAI API Key | -- | For GPT-4o-mini and embeddings |
| Tesseract OCR | Latest | Required for document scanning |
| Internet | -- | First run downloads NLLB model (~1.3 GB) |

### Installation

```bash
# Clone the repository
git clone https://github.com/aarush-luthra/Government-Scheme.git
cd Government-Scheme

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# Windows: https://github.com/UB-Mannheim/tesseract/wiki

# Configure environment
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Generate the FAISS vector database (first time only)
python backend/ingestion/ingestion_runner.py

# Run the application
python -m backend.app
```

Open `http://localhost:8000` in your browser.

Note: Always use `python -m backend.app` (not `python backend/app.py`) to ensure correct module imports.

### Database Migrations

```bash
# Stamp existing database at baseline
alembic stamp 001_initial

# Create a new migration after schema changes
alembic revision --autogenerate -m "add_new_column"

# Apply pending migrations
alembic upgrade head
```

---

## API Reference

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/health` | Enhanced health check (SQLite, FAISS, translator status) |
| GET | `/auth/me` | Current session info |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Sign in, returns access_token + refresh_token |
| POST | `/auth/refresh` | Exchange refresh_token for new access_token |
| POST | `/auth/logout` | Sign out, clears session |
| POST | `/profile` | Create new user profile |
| POST | `/edit` | Update existing profile |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send message (returns AI response + sources) |
| WS | `/ws/chat` | WebSocket for streaming chat responses |

### Scheme Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/saved-schemes` | Save a scheme |
| DELETE | `/api/v1/saved-schemes/{name}` | Remove a saved scheme |
| GET | `/api/v1/saved-dashboard?limit=20&offset=0` | Paginated saved schemes, reminders, alerts |
| POST | `/api/v1/reminders` | Set a deadline reminder |
| POST | `/api/v1/ocr` | Upload document for OCR |

### Admin (requires admin role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/analytics` | Platform usage analytics |
| GET | `/api/v1/admin/ingestion-health` | Ingestion pipeline status |
| GET | `/api/v1/admin/tasks/failures` | Task failure log |
| POST | `/api/v1/admin/alerts/dispatch` | Trigger alert notifications |

---

## Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| en_XX | English | hi_IN | Hindi |
| bn_IN | Bengali | ta_IN | Tamil |
| te_IN | Telugu | mr_IN | Marathi |
| gu_IN | Gujarati | kn_IN | Kannada |
| ml_IN | Malayalam | pa_IN | Punjabi |
| or_IN | Odia | as_IN | Assamese |
| ur_IN | Urdu | ks_IN | Kashmiri |
| mai_IN | Maithili | ne_IN | Nepali |

---

## Troubleshooting

**ModuleNotFoundError: No module named 'backend'**
Run from the project root: `python -m backend.app`

**Empty chatbot results**
Generate the FAISS index: `python backend/ingestion/ingestion_runner.py`

**Translation model download stalls**
NLLB-200 (~1.3 GB) downloads on first run. Ensure stable internet. Cached at `~/.cache/huggingface/`.

**Port 8000 in use**
```bash
lsof -ti :8000 | xargs kill -9
```

**Session not persisting**
Access via `http://localhost:8000`, not `http://127.0.0.1:8000`. Session cookies are hostname-bound.

---

## Contributing

Contributions are welcome. Please submit a Pull Request.

## License

MIT License
