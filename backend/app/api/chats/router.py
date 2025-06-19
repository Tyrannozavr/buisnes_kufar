from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter()


@router.post("")
async def create_chat(request: Request):
    print(request.body)  # Print the incoming request body
    return {"chat_id": 1}