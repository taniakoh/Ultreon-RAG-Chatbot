"""Build LlamaIndex query engine over persisted vector store."""

from llama_index.core import PromptTemplate, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.settings import Settings as LlamaSettings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter

from backend.config import STORE_DIR, settings

QA_PROMPT_TMPL = """\
You are a helpful assistant for TanLaw Advisory staff. Answer the question using ONLY the provided context passages. Follow these rules strictly:

1. Base your answer exclusively on the context below. Do not use outside knowledge.
2. If the context does not contain enough information to answer, say "I don't have enough information in the available documents to answer that question."
3. When you use information from a passage, cite the document name in parentheses, e.g. (Annual Leave Policy).
4. Be concise and professional. Use bullet points for lists.
5. If different documents contain conflicting information, mention both and note the discrepancy.

Context:
-----
{context_str}
-----

Question: {query_str}

Answer:"""

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
    embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
    LlamaSettings.embed_model = embed_model

    # Load persisted index
    storage_context = StorageContext.from_defaults(persist_dir=str(STORE_DIR))
    index = load_index_from_storage(
        storage_context=storage_context,
        embed_model=embed_model,
    )

    # Build query engine
    query_engine = index.as_query_engine(
        similarity_top_k=settings.SIMILARITY_TOP_K,
        text_qa_template=QA_PROMPT,
    )

    return query_engine
