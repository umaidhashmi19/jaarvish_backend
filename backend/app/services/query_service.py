from sqlalchemy.orm import Session
from sqlalchemy import text
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.models.chatbot import Chatbot

# Same model used for ingestion
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")


def get_query_embedding(question: str) -> list[float]:
    """Step 2 — Convert question to vector using same BGE model."""
    return embed_model.get_text_embedding(question)


def search_chunks(
    db: Session,
    chatbot_id: str,
    query_embedding: list[float],
    limit: int = 5
) -> list[str]:
    """
    Step 3 — Vector similarity search in pgvector.
    Filters by chatbot_id to prevent data mixing.
    """
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    sql = text("""
        SELECT content
        FROM document_chunks
        WHERE chatbot_id = :chatbot_id
        ORDER BY embedding <-> CAST(:embedding AS vector)
        LIMIT :limit
    """)

    results = db.execute(sql, {
        "chatbot_id": str(chatbot_id),
        "embedding": embedding_str,
        "limit": limit
    }).fetchall()

    return [row[0] for row in results]


def build_context(chunks: list[str]) -> str:
    """Step 4 — Combine retrieved chunks into context string."""
    return "\n\n".join(chunks)


def build_prompt(context: str, question: str) -> str:
    """Step 5 — Build the final prompt for the LLM."""
    return f"""You are a helpful support assistant.

Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
----------------
{context}
----------------

Question:
{question}"""


async def run_query(
    db: Session,
    chatbot_id: str,
    question: str,
    user_id: str
) -> str:
    """
    Full RAG query pipeline.
    Steps: Embed → Search → Build Context → Prompt → LLM → Answer
    """

    # Security check — verify chatbot belongs to this user
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.owner_id == user_id,       # ← prevents cross-user access
        Chatbot.is_active == True
    ).first()

    if not chatbot:
        raise ValueError("Chatbot not found or access denied.")

    # Step 2 — Embed the question
    query_embedding = get_query_embedding(question)

    # Step 3 — Search pgvector
    chunks = search_chunks(db, chatbot_id, query_embedding)

    if not chunks:
        return "I don't have enough information to answer that question yet."

    # Step 4 — Build context
    context = build_context(chunks)

    # Step 5 — Build prompt
    prompt = build_prompt(context, question)

    # Step 6 — Send to LLM and get answer
    answer = await call_llm(prompt)

    return answer


async def call_llm(prompt: str) -> str:
    """
    Step 6 — Call the LLM with the prompt.
    Using Groq (free) for testing. Swap to OpenAI at launch.
    """
    from groq import AsyncGroq
    from app.config import settings

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # free + fast
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message.content