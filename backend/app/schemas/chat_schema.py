from pydantic import BaseModel
from uuid import UUID


class ChatQueryRequest(BaseModel):
    chatbot_id: UUID
    question: str


class ChatQueryResponse(BaseModel):
    answer: str
    chatbot_id: UUID
    question: str