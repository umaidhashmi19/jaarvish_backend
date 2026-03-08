from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.chat_schema import ChatQueryRequest, ChatQueryResponse
from app.controllers.chat_controller import handle_query
from app.db import get_db
from app.utils.dependencies import get_current_user  # your existing auth

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query", response_model=ChatQueryResponse)
async def query_chatbot(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await handle_query(
        request=request,
        db=db,
        user_id=str(current_user.id)
    )