# ConCiencia Financiera API

REST API that extracts structured financial data (expenses, income, investments) from documents using LLMs. It processes PDFs, images, audio, text files, and Excel spreadsheets, then returns normalized items ready to be stored in a database.

Built as the backend for a personal finance PWA aimed at young adults in Colombia. The frontend is a React app built with [Lovable](https://lovable.dev); this API serves as the bridge between it and a Supabase/PostgreSQL database for tasks that require LLM processing.

## Stack

- **Python 3.12+** with [uv](https://docs.astral.sh/uv/) for dependency management
- **FastAPI** — async REST framework
- **LangChain + OpenAI** — LLM-powered extraction (GPT-4o-mini) and audio transcription (Whisper)
- **Supabase** — PostgreSQL database with row-level security
- **Pydantic** — request/response validation and structured output
- **PyMuPDF** — PDF to image conversion for vision-based extraction
- **Docker** — containerized deployment

## Endpoints

| Method | Path | Description |
|:---|:---|:---|
| `GET` | `/health` | Health check (no auth) |
| `POST` | `/extract/presupuesto` | Extract budget items (income/expenses) from a file |
| `POST` | `/extract/inversiones` | Extract investment items from a file |

Both extraction endpoints require an `X-API-Key` header and accept a file upload (`multipart/form-data`). Supported file types: PDF, images (PNG/JPEG/WebP/GIF), audio (MP3/WAV/OGG/M4A/WebM/FLAC), text, and Excel.

## Setup

```bash
# Clone and install
git clone <repo-url>
cd concienciafinanciera-api
uv sync

# Configure environment
cp .env.example .env
# Fill in your API keys in .env

# Run
uv run main.py
```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

## Environment Variables

See [`.env.example`](.env.example) for the full list. Required:

| Variable | Description |
|:---|:---|
| `OPENAI_API_KEY` | OpenAI API key for GPT and Whisper |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SECRET_KEY` | Supabase service role key |
| `API_KEY` | API key for authenticating requests |

## Tests

```bash
uv sync --extra dev
uv run pytest -v
```

## Docker

```bash
docker build -t concienciafinanciera-api .
docker run -p 8000:8000 --env-file .env concienciafinanciera-api
```

## Project Structure

```
├── main.py                  # App entrypoint
├── app/
│   ├── config.py            # Settings (env vars)
│   ├── dependencies.py      # Auth dependency
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   └── extraction.py    # API endpoints
│   ├── services/
│   │   ├── extraction.py    # LLM extraction logic
│   │   ├── preprocessors.py # File processing (PDF, images, audio, Excel)
│   │   └── supabase_client.py # Database queries
│   └── prompts/
│       └── system_prompts.py # LLM prompt templates
├── tests/                   # Test suite
├── Dockerfile
└── pyproject.toml
```

---

> This is an adapted version for portfolio purposes. The original project is a shared venture where I serve as the developer and analytics lead.
