# NAAC Compliance Intelligence System — MVSR Engineering College

A full-stack **Retrieval-Augmented Generation (RAG)** platform that helps IQAC,
faculty, and administrators understand NAAC requirements, retrieve MVSR
institutional evidence, and map MVSR practices to NAAC criteria.

---

## System Architecture

```
User Query
    ↓
Semantic Embedding (sentence-transformers all-MiniLM-L6-v2)
    ↓
Vector Retrieval (ChromaDB — two separate collections)
    ├── naac_requirements collection
    └── mvsr_evidence collection
    ↓
Dynamic Metadata Mapping (criterion / compliance status)
    ↓
Context-based LLM Reasoning (Ollama llama3)
    ↓
Structured Response
    {
      "naac_requirement": "...",
      "mvsr_evidence":    "...",
      "naac_mapping":     "Criterion 2.3.3",
      "status":           "Supported / Gap Identified"
    }
```

---

## Project Structure

```
backend/
 ├── api/
 │     └── main.py            # FastAPI application
 ├── rag/
 │     ├── retriever.py       # Dual-collection semantic retrieval
 │     ├── generator.py       # Ollama-based response generation
 │     ├── pipeline.py        # Full RAG query pipeline
 │     └── metadata_mapper.py # Dynamic criterion / status inference
 ├── ingestion/
 │     ├── pdf_loader.py      # pdfplumber PDF text extraction
 │     ├── chunker.py         # Overlapping text chunking
 │     └── ingest.py          # Ingestion orchestrator
 ├── db/
 │     └── chroma_store.py    # ChromaDB dual-collection setup
 ├── llm/
 │     └── ollama_client.py   # Ollama REST client
 ├── updater/
 │     ├── naac_watcher.py    # NAAC website change detection
 │     ├── downloader.py      # Document downloader
 │     ├── version_manager.py # Archive superseded documents
 │     └── auto_ingest.py     # Incremental ingestion of new files
 ├── scheduler/
 │     └── update_scheduler.py # APScheduler daily update job
 └── requirements.txt

frontend/
 ├── src/
 │     ├── App.js             # Root component with health/sync status
 │     ├── ChatUI.js          # Compliance chat interface
 │     ├── api.js             # Axios API wrapper
 │     └── index.js           # React entry point
 ├── public/
 │     └── index.html
 └── package.json

data/
 ├── naac_requirements/
 │     ├── criterion_1/       # Place NAAC Criterion 1 PDFs here
 │     ├── criterion_2/
 │     ├── criterion_3/
 │     ├── criterion_4/
 │     ├── criterion_5/
 │     ├── criterion_6/
 │     └── criterion_7/
 └── mvsr_evidence/
       ├── policies/          # Institutional policies
       ├── iqac/              # IQAC reports
       ├── governance/        # Governance documents
       ├── student_support/   # Student support records
       └── reports/           # Institutional reports

scripts/
 └── build_index.py           # One-shot index builder
```

---

## Tech Stack

| Layer      | Technology |
|------------|-----------|
| Backend    | Python + FastAPI |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector DB  | ChromaDB (persistent, local) |
| LLM        | Ollama (`llama3`) |
| PDF Parser | pdfplumber |
| Scheduler  | APScheduler |
| Frontend   | React 18 |

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running locally

### 1. Install Ollama and pull the model

```bash
# Install Ollama (see https://ollama.com/download)
ollama pull llama3
```

### 2. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Place your documents

Copy PDF documents into the appropriate directories:

```
data/naac_requirements/criterion_1/   ← NAAC Criterion 1 documents
data/naac_requirements/criterion_2/   ← NAAC Criterion 2 documents
...
data/mvsr_evidence/policies/          ← Institutional policies
data/mvsr_evidence/iqac/              ← IQAC reports
data/mvsr_evidence/governance/        ← Governance documents
data/mvsr_evidence/student_support/   ← Student support records
data/mvsr_evidence/reports/           ← Institutional reports
```

### 4. Build the vector index

```bash
# From the project root
python scripts/build_index.py
```

Options:
```
--naac-dir      Path to NAAC documents (default: data/naac_requirements)
--mvsr-dir      Path to MVSR documents (default: data/mvsr_evidence)
--naac-version  Version label (default: 2025)
--mvsr-year     Year label (default: 2024)
```

### 5. Start the backend

```bash
# From the project root
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### 6. Start the frontend

```bash
cd frontend
npm install
npm start
```

Frontend will open at `http://localhost:3000`

---

## API Reference

### `POST /query`

Run a compliance query.

**Request:**
```json
{
  "query": "Do we meet NAAC student support standards?",
  "n_naac": 4,
  "n_mvsr": 4,
  "model": "llama3"
}
```

**Response:**
```json
{
  "answer":           "...(full LLM analysis)...",
  "naac_requirement": "...(top NAAC chunk)...",
  "mvsr_evidence":    "...(top MVSR chunk)...",
  "naac_mapping":     "Criterion 5",
  "status":           "Supported"
}
```

### `POST /ingest`

Ingest documents into ChromaDB.

```json
{
  "naac_dir": "data/naac_requirements",
  "mvsr_dir": "data/mvsr_evidence",
  "naac_version": "2025",
  "mvsr_year": 2024
}
```

### `POST /force-update`

Trigger an immediate NAAC document update cycle.

### `GET /health`

Check status of Ollama and ChromaDB.

### `GET /last-sync`

Return the timestamp and statistics from the last NAAC document sync.

---

## Document Metadata

Each ingested chunk is stored with metadata:

**NAAC documents:**
```json
{
  "type":        "requirement",
  "criterion":   "2",
  "indicator":   "",
  "version":     "2025",
  "status":      "active",
  "source_file": "SSR_Manual_2025.pdf"
}
```

**MVSR documents:**
```json
{
  "type":        "evidence",
  "criterion":   "",
  "document":    "Mentoring_Policy.pdf",
  "category":    "policies",
  "year":        2024,
  "source_file": "Mentoring_Policy.pdf"
}
```

---

## Auto-Update System

The scheduler runs a daily update cycle at **02:00 UTC**:

1. Checks NAAC website pages for content changes (hash comparison)
2. Extracts new PDF/DOC links
3. Downloads new documents to the appropriate criterion directory
4. Archives superseded versions in `data/naac_requirements/_archive/`
5. Embeds and adds new chunks to ChromaDB

Trigger manually via `POST /force-update`.

---

## Example Queries

The system handles open-ended natural language queries. No hardcoded
templates or keyword matching — all responses are generated via semantic
retrieval and LLM reasoning.

- *"Do we meet NAAC student support standards?"*
- *"What proof exists for governance?"*
- *"Where do we align with teaching-learning guidelines?"*
- *"What is MVSR's research output?"*
- *"Does MVSR have an anti-ragging mechanism?"*
- *"What evidence do we have for infrastructure criteria?"*
