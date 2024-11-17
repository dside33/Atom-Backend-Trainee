from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates

from .schemas import UserCreate, UserLogin, Token, UserOut
from .logic import register_user_logic, login_user_logic

from app.core.database import get_async_session


auth_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@auth_router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@auth_router.post("/register", response_model=UserOut)
async def register_user(
    request: Request, db: AsyncSession = Depends(get_async_session)
):
    return await register_user_logic(request, db)


@auth_router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    return await login_user_logic(response, request, db)
