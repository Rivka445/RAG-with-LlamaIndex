# Project Document Analysis & QA Agent

A knowledge management system that transforms raw project documentation into a queryable knowledge base.
Built with LlamaIndex Workflows and a hybrid routing architecture.

---

## The Problem

Some questions can't be answered well with semantic search alone:

| Type | Example | Why semantic search falls short |
|---|---|---|
| Full list | "Give me all technical decisions" | Returns only top-K results, misses items spread across files |
| Recency | "What's the latest guideline on RTL?" | Can't distinguish old vs. current versions |
| Structured filter | "How many rules did cursor document?" | Semantic similarity ≠ counting or filtering |

## The Solution

Two complementary retrieval paths, with an LLM router deciding which to use:

```
User question
      │
      ▼
 LLM Router (LlamaIndex RouterQueryEngine)
      │
      ├── Semantic Search ──► RAGWorkflow (embedding + vector search + GPT answer)
      │
      └── Structured Query ─► LLM builds JSON filter ──► query structured_project_data.json ──► GPT answer
```

---

## Architecture

```
RAG/
├── data/                        # Source documentation (.md files)
│   ├── cursor/                  # Cursor AI project docs
│   └── claude/                  # Claude AI project docs
│
├── extraction/                  # Structured data extraction
│   ├── models.py                # Pydantic schema (Decision, Rule, WarningItem)
│   ├── extract.py               # LlamaIndex structured_predict → JSON
│   └── structured_project_data.json   # Extracted structured data
│
├── workflows/                   # Core application
│   ├── server.py                # RAGWorkflow (ingest → embed → retrieve → generate)
│   ├── events.py                # Typed workflow events (Pydantic)
│   ├── router.py                # LlamaIndex RouterQueryEngine (semantic / structured)
│   └── run_workflow.py          # Gradio UI + entry point
│
├── index_storage/               # Persisted vector index (auto-generated)
├── .env                         # API keys
└── requirements.txt
```

### RAG Workflow steps (`server.py`)

```
StartEvent → ingest_step → validate_step → embedding_step → retrieval_step → generation_step → StopEvent
```

| Step | What it does |
|---|---|
| `ingest_step` | Loads index from disk or builds it from `data/` |
| `validate_step` | Validates query, assigns request ID |
| `embedding_step` | Embeds query with Cohere multilingual |
| `retrieval_step` | Retrieves top-10 semantically similar chunks |
| `generation_step` | GPT-4o-mini generates a cited answer |

### Structured Query flow (`router.py`)

1. **LLM Router** — `LLMSingleSelector` reads tool descriptions and picks semantic or structured
2. **Filter generation** — LLM receives the schema and returns a JSON query plan: `{category, tool_filter, operation, search_term}`
3. **Data retrieval** — filters `structured_project_data.json` directly
4. **Answer generation** — LLM formats the results into a final answer

### Structured data schema (`extraction/models.py`)

Three item types extracted from every `.md` file:

```json
{
  "decisions": [{ "id": "dec-001", "title": "...", "summary": "...", "tags": [], "source": {...}, "observed_at": "..." }],
  "rules":     [{ "id": "rule-001", "rule": "...", "scope": "...", "notes": "...", "source": {...}, "observed_at": "..." }],
  "warnings":  [{ "id": "warn-001", "area": "...", "message": "...", "severity": "high|medium|low", "source": {...}, "observed_at": "..." }]
}
```

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Create `.env`**
```
OPENAI_API_KEY=<your-openai-api-key>
COHERE_API_KEY=<your-cohere-api-key>
```

**3. Extract structured data** (run once, or after adding new docs)
```bash
cd extraction
python extract.py
```

**4. Run**
```bash
cd workflows
python run_workflow.py
```

Open `http://127.0.0.1:7860`

---

## Example Questions

**→ Semantic search** (open-ended, requires understanding):
- "How does the authentication flow work?"
- "What is the overall architecture of the project?"
- "Explain the order management process"

**→ Structured query** (lists, counts, filters):
- "How many rules did cursor document?"
- "Give me all technical decisions related to auth"
- "What warnings exist about JWT?"
- "List all decisions made by claude"
- "What is rule-007?"

---

## Re-indexing

After adding new `.md` files to `data/`:

```bash
# Rebuild vector index
rmdir /s /q index_storage        # Windows
rm -rf index_storage             # macOS/Linux

# Re-extract structured data
cd extraction
python extract.py
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Workflow engine | LlamaIndex Workflows |
| LLM router | LlamaIndex `RouterQueryEngine` + `LLMSingleSelector` |
| Embedding model | Cohere `embed-multilingual-v3.0` |
| LLM | OpenAI `gpt-4o-mini` |
| Structured extraction | LlamaIndex `structured_predict` + Pydantic |
| UI | Gradio |
