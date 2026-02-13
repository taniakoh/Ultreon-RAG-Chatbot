"""Build LlamaIndex query engine over persisted vector store."""

from llama_index.core import PromptTemplate, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.settings import Settings as LlamaSettings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter

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
