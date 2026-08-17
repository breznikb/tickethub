from functools import lru_cache

from fastembed import TextEmbedding

from tickethub.core.config import EMBEDDING_CACHE_DIR, EMBEDDING_MODEL


@lru_cache
def get_embedding_model() -> TextEmbedding:
    return TextEmbedding(
        model_name=EMBEDDING_MODEL,
        cache_dir=EMBEDDING_CACHE_DIR,
    )


def embed_documents(texts: list[str]) -> list[list[float]]:
    embeddings = get_embedding_model().embed(texts)
    return [embedding.tolist() for embedding in embeddings]


def embed_query(text: str) -> list[float]:
    embeddings = get_embedding_model().query_embed(text)
    return next(embeddings).tolist()
