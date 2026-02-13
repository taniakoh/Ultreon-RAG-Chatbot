use case: simple internal tool

Choosing of LLM Model
- is the data sensitive? no

Case Study: internal chatbot for documentation related queries
complexity:moderate
datatype: text

Key Benchmarks for choosing of the model
- MMLU Massive multitask language understaning -> needst o have reasoning
- MT Bench - conversational quality
3. LongBench — Long Document Understanding -> abiility to read long documents -> no need

Benchmark Type	Tests	Insurance Importance
Knowledge	General understanding	Critical
Reasoning	Logic, calculations	Critical
Conversational	Chat quality	Critical
Long-context	Reading documents	Critical
Factual accuracy	Truthfulness	Critical
Retrieval	Document lookup	Critical
Safety	Compliance	Critical
Coding	Programming	Optional

https://github.com/SciPhi-AI/R2R
About
SoTA production-ready AI retrieval system. Agentic Retrieval-Augmented Generation (RAG) with a RESTful API.

https://github.com/caiyinqiong/Semantic-Retrieval-Models

1. Core Architecture of a RAG System

A standard RAG pipeline has 5 components:

User Query
    ↓
Embedding Model → Vector Database (retrieve relevant chunks)
    ↓
Retrieved Context + Query
    ↓
LLM (Generation Model)
    ↓
Final Answer

1. data preparation
2. embedding model text to vector
3. store in vector db
4. retrieval based on similarity search
5.choose llm


6. Production upgrades (advanced)

Real production RAG uses:

hybrid search (vector + keyword)

reranking model (bge-reranker)

caching

streaming responses

agent routing

metadata filtering

7. If you're building a serious production-ready RAG

Best stack right now:

Embedding: BAAI/bge-large-en-v1.5
Vector DB: Qdrant
LLM: GPT-4o or Claude Sonnet
Framework: LlamaIndex
Backend: FastAPI


@mohansharma1989
3 weeks ago
This works only for simple texts but does not work for complex documents like legal documents where splitting clauses and definitions across chunks, losing crucial context, cross-references, and semantic meaning, leading to inaccurate or incomplete answers.

23


Reply


@skermunkel6002
3 weeks ago
Yeah you would need something like GraphRAG to check the relational connections between the chunks.

Top Recommended Embedding Models for RAG
Best Overall (Open Source): BGE-M3 (BAAI) is highly versatile, supporting multilingual, hybrid, and long-context (up to 8192 tokens) retrieval, making it a top choice for complex RAG tasks.
Best for Performance (Proprietary): Voyage-3-Large and OpenAI text-embedding-3-large are top performers for semantic search accuracy and handling complex queries.
Best for Speed & Efficiency: E5-Base-v2 and Nomic-Embed-v1 provide excellent balance between fast inference speed and high hit rates, suitable for real-time applications.
Best for Multi-lingual: Multilingual-E5-large-instruct is optimized for over 100 languages.
Best for Long Context/Code: Qwen3-8B-Embedding (often run in FP8) is a top contender for large-scale, high-

Key Factors for Selection
Domain Specificity: Models like bge-base-en-v1.5 are heavily tuned for English, while multilingual-e5 is best for cross-lingual tasks.
Context Length: If your RAG requires long document understanding, look for models supporting 8k+ tokens (e.g., BGE-M3, Qwen3).
Latency vs. Accuracy: High-accuracy models (Nomic-Embed) may have higher latency (41.9ms/1k tokens) compared to faster alternatives like MiniLM-L6-v2. 

choosing embedding model -> domain v small

OpenRouter is a unified API service that enables developers to access hundreds of different Large Language Models (LLMs) from various providers
There's a really good playbook we've developed internally and we use it only for client deployments etc.

Broadly:

generate ideal pairs for test set. This is virgin data, models never see this.

evaluate base embedding model on these pairs for retrieval @1, retrieval @3

human annotate 100-200 pairs

Annotate the rest with SLMs + few shots examples most relevant to the sample. We have a 3 model majority voting process we use with SLMs (qwen/llama/gemma etc)

curate, fine-tune models and compare against the virgin data. Once we start seeing numbers that are acceptable for the domain, we host it as the experimental version and checkpoint it. Usually there's data drift and a few checkpoints need to be trained, but clients are happy for the model specifically trained for their data as long as they own the actual model


dash_bro
•
5mo ago
These are cool, but you always need to optimize for what your data/domain is.

General purpose? The stella-400-en is my workhorse. This, with qwen3-0.6B-embed practically works across the board for me.

More specialised cases often require fine-tuning my own sentence transformer models - the gemma3-270m-embed looks like a great starting point.


6
u/CaptainSnackbar avatar
CaptainSnackbar
•
5mo ago
I am currently finetuning an embedding model. How did you generate sufficient training data? Manual annotation, LLM-generated, or unsupervised methods?
\
1.split data in chunks -> necessary for small domain? -> how do i optimise the data?
2. embedding: use small model due to small domain -> how do i optimise the embeddings? -> create vector embeddings: vector representations of the words such that the coordinates reflect semantic meaning -> calculates the simularity
evaluator to compare distance(cosine similarity, euclidean)
generate vector using llm
3. create database -> needs to persist
4. Querying for relevant data
- use database and embedding function used
- embed query and scan thru database to find chunks of data
- returns top results from the query
- returns tuple of doc with relevant score
- if below threshold stop searching
5. use the relevant data to get the ai to use the info to respond
- feed into openai to answer based on prompt template -> optimise the prompt template?
- send to the llm for the reply
- responds with the sources used from the data

The requirements say documents "don't change often — maybe once a quarter." You have  
  exactly 5 small text files (~120KB total).
https://www.youtube.com/watch?v=tcqEUSNCn8I


Mixture of Experts (MoE) for RAG means using multiple specialized models (experts) and a router that decides which expert should handle each query or retrieval step.

Instead of using one single embedding model or LLM for everything, you use multiple experts and dynamically choose the best one.

Basic idea

Normal RAG:

User Query → Retriever → LLM → Answer

MoE RAG:

User Query
    ↓
Router (decides best expert)
    ↓
Expert Retriever or Expert LLM
    ↓
Answer
Why use Mixture of Experts in RAG?

Because different experts are better at different things.

Example:

Expert	Best at
Expert 1	coding questions
Expert 2	legal documents
Expert 3	internal company docs
Expert 4	general knowledge

Router picks the best expert automatically.

Where MoE can be applied in RAG

There are 3 main places:

1️⃣ Multiple embedding models

Example:

coding queries → use code embedding model
general queries → use general embedding model
legal queries → use legal embedding model

Improves retrieval accuracy.

2️⃣ Multiple vector databases

Example:

Query → router →

→ engineering database
→ HR database
→ legal database

Each database is an expert in its domain.

3️⃣ Multiple LLMs

Example:

Simple question → use small cheap LLM
Complex reasoning → use powerful LLM
Code question → use code-specialized LLM

Saves cost and improves performance.

Real-world example architecture
                User Query
                     ↓
                   Router
         ┌──────────┼──────────┐
         ↓          ↓          ↓
    Code Expert  Legal Expert  General Expert
         ↓          ↓          ↓
     Vector DB   Vector DB   Vector DB
         ↓          ↓          ↓
            Best LLM generates answer
Example implementation concept
def route_query(query):
    if "code" in query:
        return code_rag
    elif "policy" in query:
        return policy_rag
    else:
        return general_rag

rag_system = route_query(query)
answer = rag_system.run(query)

Langchain is a more general-purpose framework that can be used to build a wide variety of applications. It provides tools for loading, processing, and indexing data, as well as for interacting with LLMs. Langchain is also more flexible than LlamaIndex, allowing users to customize the behavior of their applications.

LlamaIndex is specifically designed for building search and retrieval applications. It provides a simple interface for querying LLMs and retrieving relevant documents. LlamaIndex is also more efficient than Langchain, making it a better choice for applications that need to process large amounts of data.

If you are building a general-purpose application that needs to be flexible and extensible, then Langchain is a good choice. If you are building a search and retrieval application that needs to be efficient and simple, then LlamaIndex is a better choice.



https://qdrant.tech/ fast and easy to install & use

At the end of the day, no matter which vector DB you pick they're all pretty similar in terms of usage patterns. If you already use postgres might as well use pgvector instead of a dedicated vector db


Just to round out the picture, if your number of documents is in the hundreds, thousands or tens of thousands, you may not need a vector database. A SQL database is more than up to the task of retrieving similar documents based on embeddings. I say this not because a SQL database is a better solution, but because if you already have one in your stack there may be no need to add another dependency in the form of a vector database.


5
Leather-Departure-38
OP
•
1y ago
Interesting view, in your view what is the approximate threshold to move away from traditional relational database?


2
OrbMan99
•
1y ago
I haven't tested this limit personally as the maximum document count for me was around 10,000 and performance was great for that quantity. Obviously this depends on having optimized tables/queries/indexes, etc. I had fully intended to implement using a vector db and had just thrown things into SQL in the meantime while I sorted out which one to use before I discovered I was fine as-is. If you are on Postgres you have the best of both worlds as you can use the pgvector extension if you wish. So, I guess there is a point to be made for a beginner that you don't HAVE to have a vector db. So maybe it's a good idea to start without one while learning, and then see what it adds to the equation. You could even start with just storing data in files and matching in memory. That's going to work fine for smaller data sets. Also, implementing yourself, e.g., in a SQL query will show you the math of how the matching is done.


1. Data Preparation & Chunking
For a "small domain" of 120KB, chunking is less about managing database limits and more about precision.

Is it necessary? Yes, because it allows the LLM to cite specific sections and reduces noise. However, you do not need complex "semantic chunking" for this volume.

Optimization: Use a Recursive Character Text Splitter with a chunk size of ~500–800 tokens and a 10–15% overlap. This ensures that definitions or clauses (as mentioned in the YouTube comment research) aren't cut in half.

Small Domain Tip: Since you only have 5 files, you can manually verify if any "breaking points" (like tables or headers) are being split awkwardly and adjust your separators accordingly.

2. Embedding Model Selection
Small Model vs. Large Model: For a "small domain" and 120KB of data, bge-small-en-v1.5 or all-MiniLM-L6-v2 are excellent because they are fast and can run locally.

Optimization: You likely do not need to fine-tune. Instead, optimize via Metadata Filtering. Tag each chunk with the filename or category (e.g., policy, technical_manual). When a user asks about a "policy," you can filter the search to only those chunks, drastically increasing accuracy.

Evaluation: Create 10 "Golden Questions" based on your 5 files. Run a simple script to see if the correct chunk is returned in the top 3 results. If yes, your embeddings are sufficient.

3. Database Selection
Recommendation: Avoid a dedicated Vector DB. * Adding Qdrant or Pinecone for 120KB of data adds unnecessary architectural overhead.

Better Options:

ChromaDB (Local/Persistent): Extremely easy to set up with Python.

Numpy/FAISS: If you want zero dependencies, you can literally store the embeddings in a .npy file and search them in memory.

pgvector: Only use this if you are already using PostgreSQL for other parts of the tool.

4. Querying & Retrieval
Similarity Threshold: With such a small dataset, set a conservative threshold (e.g., 0.7 cosine similarity). If the best result is 0.5, the system should say, "I couldn't find relevant information in the documentation," rather than hallucinating.

Optimization: Use Query Expansion. For small documentation sets, users might use different terminology than the text. Use a cheap LLM (like GPT-4o-mini) to rewrite the user query into 3 variations, search for all 3, and take the top unique results.

5. LLM & Prompt Optimization
Model: GPT-4o-mini or Claude 3 Haiku. They are more than capable of handling documentation queries for 120KB of text at a fraction of the cost of "flagship" models.

Prompt Template Optimization:

Plaintext
You are an internal documentation assistant. Use ONLY the provided context to answer. 
If the answer isn't in the context, say you don't know. 
Context: {retrieved_chunks}
Question: {user_query}
Cite your source using the filename provided in the context metadata.
Source Attribution: Ensure your retrieval step returns a dictionary containing { "text": "...", "source": "file_a.txt" }. Pass this to the LLM so it can say, "According to file_a.txt, the process is..."

Is "Mixture of Experts" (MoE) or GraphRAG needed?
No. * MoE: This is overkill for 5 files. You don't need a "router" to decide between a "Legal Expert" and a "Code Expert" when one model can hold all 120KB in its active memory.

GraphRAG: Only useful if your 5 files have complex, overlapping relational data (e.g., "Employee A is mentioned in File 1 but their permissions are in File 3"). For standard documentation, standard RAG is faster and easier to maintain.

Recommended "Lean" Tech Stack
Framework: LlamaIndex (Better for RAG-specific "out of the box" performance).

Backend: FastAPI.

Embeddings: text-embedding-3-small (OpenAI) or bge-small-en-v1.5 (Local).

Vector Store: ChromaDB (Persistent local storage).

LLM: GPT-4o-mini.


Final Thought: Because your dataset is so small (~120KB), you could actually bypass RAG entirely and just put the full text of all 5 files into the System Prompt every time. This is called "Long Context" prompting. It is 100% accurate because the model sees everything, but it is slightly more expensive per message than RAG. For an internal tool with low traffic, this might be the most "optimized" solution of all.


4. Strategic Recommendation
If Privacy is #1:
Deploy Llama 3.2 1B or Gemma 3 1B locally. They are incredibly small, can run on a standard laptop CPU, and are surprisingly smart at summarizing short documents.

If Accuracy is #1:
Use GPT-4o-mini via API. It is the "gold standard" for small RAG tools in 2026 because it has near-flagship intelligence for a fraction of the price.

If the Documentation is "Legal-Heavy":
Go with Claude 3.5 Sonnet. Historically, Anthropic’s models are more cautious and follow "negative constraints" (e.g., "Do not mention anything outside the text") better than others.


Gemini said
Handling "Honest Uncertainty" is the difference between a tool that is a helpful assistant and one that is a liability. In a RAG (Retrieval-Augmented Generation) system, this is managed through a "defense-in-depth" approach across three layers: the Retriever, the Prompt, and the LLM.

1. The Retriever Layer (Thresholding)
Before the LLM even sees the question, your system should decide if the retrieved data is actually relevant. If your vector search returns a "best match" with a very low similarity score, the documents likely don't contain the answer.

Similarity Threshold: Set a cutoff (e.g., 0.75 or 0.80 for Cosine Similarity). If the top chunks fall below this, stop the process and return a pre-written message: "I couldn't find any documents in our library that specifically address that."

LlamaIndex Tip: You can implement this using a SimilarityPostprocessor.

Python
from llama_index.core.postprocessor import SimilarityPostprocessor

# Only allow chunks that are at least 80% similar to the query
node_postprocessor = SimilarityPostprocessor(similarity_cutoff=0.8)

query_engine = index.as_query_engine(
    node_postprocessors=[node_postprocessor]
)
2. The Prompting Layer (Negative Constraints)
You must explicitly tell the LLM that it is "allowed" to fail. Most models are RLHF-trained (Reinforcement Learning from Human Feedback) to be helpful, which inadvertently makes them "people pleasers" that try to answer even when they shouldn't.

Refined System Prompt:

"You are a professional advisor. You will be provided with context from internal documents. Your goal is to answer the query ONLY using that context.

STRICT RULE: If the context provided does not contain a direct answer, or if the information is too vague to be certain, you MUST respond exactly with: 'I am sorry, but the provided documentation does not contain enough information to answer this question accurately.'

DO NOT use your own pre-trained knowledge to fill in gaps."

3. The LLM Layer (Model Selection)
Not all models are equally "honest."

Large Models (GPT-4o, Claude 3.5 Sonnet): These are excellent at following "negative constraints" (e.g., "Do not do X").

Small Models (GPT-4o-mini, Llama 3-8B): These are more prone to "hallucinating" or trying to be helpful by using their general training data if the context is thin.

Pro-tip for 2026: If you use Claude 3.5, use their "system-prompt" block specifically. Anthropic models are currently the industry leaders in "refusal accuracy"—the ability to say "I don't know" when instructed.


1. Cloud LLM (OpenRouter/OpenAI/Claude)Best for: Maximum intelligence, fast setup, and "moderate" complexity logic.Privacy Reality: In 2026, most "Enterprise" or "API" tiers of cloud providers (like OpenAI or Anthropic) have strict contractual clauses stating that your data is not used to train their models.The Risk: Even with those clauses, your data still leaves your network. If your 5 files contain highly sensitive "Restricted" data (e.g., private client names, trade secrets, or regulated health data), your legal/compliance team might veto any cloud-based solution.Advantage: Models like gpt-4o-mini are significantly smarter at following your custom prompt rules (like the "Honest Uncertainty" rule) than small local models.2. Local LLM (Llama 3.2, Qwen, or Gemma via Ollama/LocalAI)Best for: 100% Data Sovereignty, zero cost per query, and high-security environments.Privacy Reality: The data never leaves your machine or your company’s internal server. This is the "gold standard" for security.The Cost: While the software is free, you need a decent GPU (e.g., NVIDIA RTX 3060 or better) to get acceptable speeds.The Performance Gap: For "Basic" questions, a 7B or 13B local model is perfect. However, for your "Questions requiring nuance" (like the business trip to Japan), local models are more prone to getting "confused" or hallucinating unless you use a very large (and slow) local model.3. The "Mid-Way" Solution: The Proxy PatternSince you are using OpenRouter, you can actually have the best of both worlds. You can use OpenRouter's unified API to point to LocalAI or Ollama running on your own server.How to implement the security for an internal tool:If you stick with a cloud LLM (OpenRouter), you can make it "internal-only" by adding these three layers:Redaction: Use a simple Python script to swap out sensitive names/numbers with generic placeholders (e.g., Client_A, Amount_X) before sending the text to the LLM.API Key Management: Do not hardcode your OpenRouter key. Use a .env file and, if you deploy this, use a "Secret Manager" (like AWS Secrets Manager or HashiCorp Vault).Identity-First Access: Wrap your FastAPI tool in your company's SSO (Single Sign-On). Only employees with a specific "Legal" or "HR" tag in your active directory should be able to hit the /query endpoint.Summary Table: Which one should you pick?RequirementUse Cloud LLM (OpenRouter)Use Local LLM (Ollama)Data SensitivityLow to Medium (Public/Internal)High (Restricted/Confidential)Accuracy NeedsHigh (Complex reasoning)Moderate (Simple lookups)HardwareAnything (Laptop/Cloud)Requires GPU/ServerUsage VolumeLow (Pay-as-you-go)High (Free unlimited queries)