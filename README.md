⚙️ Project Setup & Configuration

This project uses a single .env file in the root directory to manage configuration for both the frontend and backend services.

1. Create the .env File

In the root of the project, create a file named .env.

Copy the .env.template and replace the placeholder values with your actual keys:

OPENROUTER_API_KEY=your_sk_or_v1_key_here

🚀 Getting Started
1. Build and Start the Stack

Run the following command in your terminal from the project root. This will build Docker images and start all services in the background:

docker compose up --build

2. Index Your Documents

To enable the RAG (Retrieval-Augmented Generation) system, you need to process your sample documents. With the containers running, open a new terminal and run:

docker compose exec backend python ingest.py

This will trigger the LlamaIndex pipeline to parse files in /sample-documents and store them in the persistent chroma_db.

🔗 Access the Application
Service	URL	Description
Frontend	http://localhost:3000
	Main chat interface for Ultreon
Backend API	http://localhost:8000/docs
	Interactive Swagger UI for API testing

Gemini said
Architecture Rationale
This project implements a Retrieval-Augmented Generation (RAG) pipeline designed for high accuracy and "Honest Uncertainty," specifically tailored for TanLaw Advisory’s internal policy documents.

1. Document Processing & Storage
To transform static text files into a searchable knowledge base, I followed a multi-stage ingestion pipeline:

Loading: I used LlamaIndex to read the five provided text files from the sample-documents/ directory.

Chunking: Documents are split using a Recursive Character Text Splitter with a chunk size of 800 characters and a 10% overlap.

Why: 800 characters is the "Goldilocks zone" for legal/policy text—large enough to keep a rule and its exception together, but small enough to avoid "Lost in the Middle" syndrome where the LLM gets distracted by irrelevant noise.

Embedding: Each chunk is converted into a vector using the bge-small-en-v1.5 model. This is a lightweight, high-performance local model that ensures the "search" part of the process stays entirely on the local machine.

Vector Store: The resulting embeddings are stored in ChromaDB, a persistent, local vector database that requires zero server overhead.

2. The Retrieval Pipeline
When a staff member asks a question, the system executes the following flow:

Vectorization: The user's plain-English question is converted into a vector using the same bge-small model.

Semantic Search: The system performs a similarity search in ChromaDB, retrieving the Top 3 most relevant document chunks.

Threshold Filtering: I implemented a Similarity Threshold. If the best-matching chunk doesn't meet a minimum confidence score (0.75), the system triggers the "Honest Uncertainty" mode.

Context Injection: The retrieved chunks are injected into a specialized "System Prompt" for Claude 3.5 Sonnet.

Grounded Generation: The LLM generates an answer based only on the provided context. It is explicitly instructed to cite the document name and provide a "Source Passage" for verification.

3. Database Schema Rationale
I opted for a Stateless Vector-Only Schema using ChromaDB.

Design: I utilized a single collection in ChromaDB where each entry contains:

id: A unique hash of the content.

embedding: The vector representation.

metadata: Stores the filename (e.g., annual-leave-policy.txt) and the raw text passage.

Reasoning: Since the client requested a "simple search tool" and the documents change only quarterly, a relational database (like PostgreSQL) would have been over-engineering. This schema allows for sub-millisecond search times and zero maintenance.

Tech Stack

Framework: LlamaIndex (Better out-of-the-box performance for document retrieval).

LLM: Claude 3.5 Sonnet (via OpenRouter). It has been tested to be the best at negative constraints which is what is required in the feature scope.

Embeddings: bge-small-en-v1.5 (Small model due to the small domain size of the texts, Fast, local, and efficient for English text).

Vector Store: ChromaDB (Persistent, local, and requires zero server setup).

Backend: FastAPI (Asynchronous and standard for AI tool builds)

Frontend Hosting: Vercel for ease of use.

Key Tradeoffs & Assumptions
1. ChromaDB vs. PostgreSQL (pgvector)
The Choice: I stuck with ChromaDB to keep the stack isolated and simple.

The Assumption: If I were integrating this into an existing company portal that already uses PostgreSQL, I definitely would have gone with pgvector instead. It would allow us to join the document search directly with existing users tables for RBAC (Role-Based Access Control) and keep all backups in one place. 

2. Cloud LLM (Sonnet) vs. Local LLM
The Choice: Claude 3.5 Sonnet.

The Assumption: I assumed the data sensitivity is "Moderate" (internal policies, technical manuals). Since there’s no PII (Personally Identifiable Information) or payment data involved, I prioritized Sonnet’s high-level reasoning over the absolute data sovereignty of a local model.

Tradeoff: A local model (like Llama 3) would be 100% private, but it would require expensive on-prem GPUs and usually underperforms on complex "refusal" logic compared to Sonnet.

Stateless Design (No Chat History)

- For simplicity and accuracy sake as well as the functional requirements describing it as a search tool, i assumed there was no need for storing of chat history for multi-turn conversations, however if required:
it would be implemented through a context window

4. Chunking Strategy: Fixed-Size vs. Semantic Chunking
The Choice: I implemented a Recursive Character Text Splitter with a chunk size of 800 characters and a 10% overlap.

The Assumption: Given that legal and policy documents often contain long, nested clauses, I assumed that a mid-sized fixed chunk with overlap would be safer than very small chunks. It ensures that a "definition" at the start of a paragraph isn't separated from the "rule" at the end of it.

Tradeoff: I avoided complex "Semantic Chunking" (which splits based on AI-detected topic changes) because, for 120KB of data, it adds unnecessary processing time without a significant gain in retrieval accuracy.

6. Static Ingestion vs. Dynamic Uploads
The Choice: Pre-loaded ingestion via a dedicated scripts/ingest.py (or similar) script.

The Assumption: Sarah Tan mentioned these documents only change quarterly. Therefore, I assumed a "Static RAG" approach was best. The documents are indexed once at build time rather than building a complex UI for file uploads and real-time indexing.

Tradeoff: This makes the app much faster and more stable, but it means an admin has to restart the container (or re-run a script) to update the policies. If the documents changed daily, I would have built a specialized /upload endpoint.


