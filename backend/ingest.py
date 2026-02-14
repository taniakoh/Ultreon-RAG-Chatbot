"""Ingest sample documents into SimpleVectorStore."""

from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.settings import Settings as LlamaSettings
from llama_index.embeddings.openai import OpenAIEmbedding

from backend.config import DOCS_DIR, STORE_DIR, settings


def ingest() -> None:
    # Configure embedding model
    embed_model = OpenAIEmbedding(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENROUTER_API_KEY,
        api_base="https://openrouter.ai/api/v1",
    )
    LlamaSettings.embed_model = embed_model

    # Load documents
    reader = SimpleDirectoryReader(input_dir=str(DOCS_DIR), filename_as_id=True)
    documents = reader.load_data()

    # Enrich metadata with document title from first line
    for doc in documents:
        first_line = doc.text.strip().split("\n")[0].strip()
        doc.metadata["document_title"] = first_line
        file_name = doc.metadata.get("file_name", "")
        doc.metadata["document_name"] = (
            file_name.replace("-", " ").replace(".txt", "").title()
        )

    # Chunk documents
    splitter = SentenceSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    nodes = splitter.get_nodes_from_documents(documents)

    # Build index and persist to disk
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    storage_context = StorageContext.from_defaults()
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    storage_context.persist(persist_dir=str(STORE_DIR))

    print(f"Ingested {len(documents)} documents, ~{len(nodes)} chunks")
    print(f"Vector store saved to {STORE_DIR}")


if __name__ == "__main__":
    ingest()
