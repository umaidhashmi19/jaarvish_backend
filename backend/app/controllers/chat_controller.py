from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.chat_schema import ChatQueryRequest, ChatQueryResponse
from app.services.query_service import run_query


async def handle_query(
    request: ChatQueryRequest,
    db: Session,
    user_id: str
) -> ChatQueryResponse:
    try:
        answer = await run_query(
            db=db,
            chatbot_id=str(request.chatbot_id),
            question=request.question,
            user_id=user_id
        )
        return ChatQueryResponse(
            answer=answer,
            chatbot_id=request.chatbot_id,
            question=request.question
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")