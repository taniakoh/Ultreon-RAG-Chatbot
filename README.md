# Ultreon RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for **TanLaw Advisory**, designed to let non-technical staff ask natural language questions about internal policy documents and receive AI-generated answers with source attribution.

---

## Project Setup & Configuration

This project uses a single `.env` file in the root directory to manage configuration for both the frontend and backend services.

### 1. Create the `.env` File

Copy the `.env.template` and replace the placeholder values with your actual keys:

```env
OPENROUTER_API_KEY=your_sk_or_v1_key_here
```

### 2. Build and Start the Stack

From the project root, build Docker images and start all services:

```bash
docker compose up --build
```

### 3. Index Your Documents

With the containers running, open a new terminal and run the ingestion script to process the sample documents:

```bash
docker compose exec backend python ingest.py
```

This triggers the LlamaIndex pipeline to parse files in `/sample-documents` and store them in the persistent vector store.

### 4. Access the Application

| Service      | URL                              | Description                          |
|--------------|----------------------------------|--------------------------------------|
| Frontend     | http://localhost:3000             | Main chat interface for Ultreon      |
| Backend API  | http://localhost:8000/docs        | Interactive Swagger UI for API testing |

---

## Development

### Dev Mode with Hot Reload

For local development with live-reloading, use the dev-specific Docker Compose file:

```bash
docker compose -f docker-compose.dev.yml up --build
```

File changes in `app/`, `components/`, and `backend/` will auto-reload without restarting containers.

### Running Tests

The test suite uses **LLM-as-a-judge** evaluation, so a valid `OPENROUTER_API_KEY` must be set in your `.env`.

**Via Docker** (with containers running):

```bash
docker compose exec backend uv run pytest backend/tests/ -v
```

**Locally** (from the `backend/` directory):

```bash
uv run pytest ../tests/ -v
```

---

## Architecture Rationale

This project implements a RAG pipeline designed for high accuracy and "Honest Uncertainty," specifically tailored for TanLaw Advisory's internal policy documents.

### 1. Document Processing & Storage

To transform static text files into a searchable knowledge base, the ingestion pipeline follows these stages:

- **Loading** — LlamaIndex reads the five provided text files from `sample-documents/`.
- **Chunking** — Documents are split using a Recursive Character Text Splitter with a chunk size of 800 characters and 10% overlap. This is the "Goldilocks zone" for legal/policy text — large enough to keep a rule and its exception together, but small enough to avoid "Lost in the Middle" syndrome.
- **Embedding** — Each chunk is converted into a vector using the `bge-small-en-v1.5` model, a lightweight, high-performance local model.
- **Vector Store** — Embeddings are stored in ChromaDB, a persistent local vector database requiring zero server overhead.

### 2. The Retrieval Pipeline

When a staff member asks a question:

1. **Vectorization** — The question is converted into a vector using the same `bge-small` model.
2. **Semantic Search** — A similarity search in ChromaDB retrieves the top 3 most relevant document chunks.
3. **Threshold Filtering** — If the best-matching chunk doesn't meet a minimum confidence score (0.75), the system triggers "Honest Uncertainty" mode.
4. **Context Injection** — Retrieved chunks are injected into a specialized system prompt for Claude 3.5 Sonnet.
5. **Grounded Generation** — The LLM generates an answer based only on the provided context, citing the document name and source passage for verification.

### 3. CI/CD Pipeline

Automated testing and deployment is handled through four GitHub Actions workflows:

| Workflow | Trigger | What It Does |
|---|---|---|
| **RAG Accuracy Tests** | Push to `main` | Installs Python 3.13 + uv, runs the LLM-as-a-judge pytest suite against the live RAG pipeline |
| **Deploy Backend** | Push to `main` (changes in `backend/`) | Builds the production Docker image, pushes to Google Artifact Registry, and deploys to Cloud Run (asia-southeast1) |
| **Vercel Production** | Push to `main` | Builds and deploys the Next.js frontend to Vercel production |
| **Vercel Preview** | Push to non-main branches | Deploys a preview build to Vercel for review before merging |

This ensures every merge to `main` is automatically tested for RAG accuracy and deployed to both the backend (Cloud Run) and frontend (Vercel) without manual intervention.

### 4. Database Schema

A **Stateless Vector-Only Schema** using ChromaDB with a single collection where each entry contains:

| Field       | Description                                              |
|-------------|----------------------------------------------------------|
| `id`        | Unique hash of the content                               |
| `embedding` | Vector representation                                    |
| `metadata`  | Filename (e.g., `annual-leave-policy.txt`) and raw text  |

Since the documents change only quarterly, a relational database would be over-engineering. This schema provides sub-millisecond search times and zero maintenance.

---

## Tech Stack

| Component    | Technology                       | Rationale                                              |
|--------------|----------------------------------|--------------------------------------------------------|
| Framework    | LlamaIndex                       | Best out-of-the-box performance for document retrieval |
| LLM          | Claude 3.5 Sonnet (via OpenRouter) | Best at negative constraints required by the feature scope |
| Embeddings   | `bge-small-en-v1.5`             | Fast, local, efficient for small English text domains  |
| Vector Store | ChromaDB                         | Persistent, local, zero server setup                   |
| Backend      | FastAPI                          | Asynchronous, standard for AI tool builds              |
| Frontend     | Next.js (Vercel)                 | Ease of deployment                                     |

---

## Key Tradeoffs & Assumptions

### ChromaDB vs. PostgreSQL (pgvector)

> **Choice:** ChromaDB to keep the stack isolated and simple.

If integrating into an existing company portal with PostgreSQL, `pgvector` would be preferable — enabling joins with user tables for RBAC and consolidated backups.

### Cloud LLM (Sonnet) vs. Local LLM

> **Choice:** Claude 3.5 Sonnet.
>
> **Assumption:** Data sensitivity is "Moderate" (internal policies, no PII or payment data).

A local model (e.g., Llama 3) would be 100% private but requires expensive on-prem GPUs and typically underperforms on complex "refusal" logic.

### Stateless Design (No Chat History)

> **Choice:** No multi-turn conversation storage.

For simplicity, accuracy, and alignment with the functional requirements describing it as a search tool. If required, chat history could be implemented through a context window.

### Chunking Strategy: Fixed-Size vs. Semantic

> **Choice:** Recursive Character Text Splitter — 800 characters, 10% overlap.

Legal/policy documents contain long, nested clauses. A mid-sized fixed chunk with overlap keeps "definitions" and "rules" together. Semantic chunking was avoided since it adds unnecessary processing time for ~120KB of data without significant accuracy gains.

### Static Ingestion vs. Dynamic Uploads

> **Choice:** Pre-loaded ingestion via a dedicated `ingest.py` script.

Documents change quarterly, so a "Static RAG" approach is optimal — indexed once at build time. This makes the app faster and more stable. If documents changed daily, a `/upload` endpoint would be built instead.


### Testing: LLM-as-a-Judge with LlamaIndex Evaluators

> **Choice:** LlamaIndex's built-in `FaithfulnessEvaluator` and `RelevancyEvaluator` for automated RAG accuracy testing.

The test suite uses an **LLM-as-a-judge** approach — rather than brittle string matching, a second LLM call evaluates each answer on two dimensions:

- **FaithfulnessEvaluator** — Checks whether the generated answer is grounded in the retrieved source chunks. A failing score indicates hallucination (the model invented information not present in the documents).
- **RelevancyEvaluator** — Checks whether the answer actually addresses the user's question given the retrieved context. A failing score indicates the response is off-topic or unhelpful.

Tests are organized into four categories across 14 parametrized cases:

| Category | Tests | What It Validates |
|---|---|---|
| **Basic** | 4 | Single-document lookups with clear answers |
| **Nuance** | 5 | Edge cases, exceptions, and conditional rules |
| **Multi-document** | 3 | Questions spanning multiple policy documents |
| **Out-of-scope** | 2 | Questions the system should refuse to answer |

For out-of-scope questions, the assertion is inverted — the test passes when the evaluator flags the response as *not* faithful, confirming the system correctly refused rather than hallucinating an answer.

This approach could be extended with more advanced methods (e.g., RAG Triad evaluation, retrieval benchmarking) or additional test cases for broader coverage.

