from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.api.authentication.services.auth_service import AuthService
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.user import User
from app.api.dependencies import get_async_db

router = APIRouter()

@router.get("/me", response_model=dict)
async def get_company_info(
    request: Request,
    db: get_async_db
):
    """
    Get current company information based on the authenticated user
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # For now, return mock data
    # TODO: Replace with actual company data from database
    return {
        "companyName": "КосмоПорт",
        "companyLogo": "https://sun9-64.userapi.com/impg/IRHOxDleaLUBKmbafJ-j_3Z5Y-pYSMHou64S9A/kASuUQJDYrY.jpg?size=728x546&quality=96&sign=cdbf008a6c9d088a665d8e0b2fb5141a&c_uniq_tag=YJ1-dsBQHtkD4Ssy2wd5CaQpmFxJcQVaq3xbhyqOo38&type=album"
    } 