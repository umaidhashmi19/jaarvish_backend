# import asyncio
# from openai import AsyncOpenAI
# from app.config import settings

# client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# MAX_RETRIES = 3
# EMBED_MODEL = "text-embedding-ada-002"


# async def embed_chunk(content: str, retries: int = MAX_RETRIES) -> list[float] | None:
#     """Embed a single chunk with retry logic."""
#     for attempt in range(retries):
#         try:
#             response = await client.embeddings.create(
#                 model=EMBED_MODEL,
#                 input=content
#             )
#             return response.data[0].embedding
#         except Exception as e:
#             if attempt == retries - 1:
#                 print(f"[embedder] Failed after {retries} attempts: {e}")
#                 return None
#             await asyncio.sleep(2 ** attempt)  # Exponential backoff
#     return None


# async def embed_chunks(chunks: list[str]) -> list[dict]:
#     """
#     Embed all chunks. Returns list of dicts with content, embedding, success flag.
#     Failed embeddings are marked but don't stop the pipeline.
#     """
#     results = []
#     for i, content in enumerate(chunks):
#         embedding = await embed_chunk(content)
#         results.append({
#             "chunk_index": i,
#             "content": content,
#             "embedding": embedding,
#             "success": embedding is not None
#         })
#     return results




# This is for the embedding of the chunks using huggingface

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")

async def embed_chunks(chunks: list[str]) -> list[dict]:
    results = []
    for i, content in enumerate(chunks):
        try:
            embedding = embed_model.get_text_embedding(content)
            results.append({
                "chunk_index": i,
                "content": content,
                "embedding": embedding,
                "success": True
            })
        except Exception as e:
            results.append({
                "chunk_index": i,
                "content": content,
                "embedding": None,
                "success": False,
                "error": str(e)
            })
    return results