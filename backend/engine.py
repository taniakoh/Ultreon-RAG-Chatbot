"""Build LlamaIndex query engine over persisted vector store."""

from llama_index.core import PromptTemplate, StorageContext, VectorStoreIndex, get_response_synthesizer, load_index_from_storage
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever, VectorIndexRetriever
from llama_index.core.settings import Settings as LlamaSettings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openrouter import OpenRouter
from llama_index.retrievers.bm25 import BM25Retriever

from backend.config import STORE_DIR, settings

QA_PROMPT_TMPL = """\
You are a professional Internal Policy Assistant for TanLaw Advisory. Your goal is to provide high-accuracy information grounded strictly in company documentation. Answer the question using ONLY the provided context passages. Follow these rules strictly:

### RULES
1. **Source Grounding**: Use ONLY the provided context. If the answer isn't there, do not invent it.
2. **Strict Refusal**: If the context is missing info, or the query is a greeting/nonsense (e.g., "hi", "test"), respond EXACTLY with: "I don't have enough information in the available documents to answer that question."
3. **Citations**: Append the document name in parentheses at the end of every sentence that uses information from that source, e.g., (Annual Leave Policy).
4. **Readability**: Use a professional tone and bullet points for lists.
5. **Conflict Resolution**: If documents provide conflicting rules, explicitly state: "Note: There is a discrepancy between [Doc A] and [Doc B]..."
### CONTEXT
{context_str}

### QUESTION
{query_str}

### ANSWER (Grounded and Cited):
"""

QA_PROMPT = PromptTemplate(QA_PROMPT_TMPL)


def build_query_engine():
    # Configure LLM
    llm = OpenRouter(
        api_key=settings.OPENROUTER_API_KEY,
        model=settings.LLM_MODEL,
        max_tokens=1024,
    )
    LlamaSettings.llm = llm

    # Configure embedding model
    embed_model = OpenAIEmbedding(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENROUTER_API_KEY,
        api_base="https://openrouter.ai/api/v1",
    )
    LlamaSettings.embed_model = embed_model

    # Load persisted index
    storage_context = StorageContext.from_defaults(persist_dir=str(STORE_DIR))
    index = load_index_from_storage(
        storage_context=storage_context,
        embed_model=embed_model,
    )

    # Configure retriever (hybrid or vector-only)
    if settings.USE_HYBRID_SEARCH:
        vector_retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=settings.SIMILARITY_TOP_K,
        )
        nodes = list(index.docstore.docs.values())
        bm25_retriever = BM25Retriever.from_defaults(
            nodes=nodes,
            similarity_top_k=settings.SIMILARITY_TOP_K,
        )
        retriever = QueryFusionRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            similarity_top_k=settings.SIMILARITY_TOP_K,
            num_queries=1,
            mode="reciprocal_rerank",
            use_async=False,
        )
    else:
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=settings.SIMILARITY_TOP_K,
        )

    # Configure reranker
    node_postprocessors = []
    if settings.USE_RERANKER:
        reranker = SentenceTransformerRerank(
            model=settings.RERANKER_MODEL,
            top_n=settings.RERANK_TOP_N,
        )
        node_postprocessors.append(reranker)

    # Build query engine
    response_synthesizer = get_response_synthesizer(
        text_qa_template=QA_PROMPT,
    )
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=node_postprocessors,
    )

    return query_engine
