from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.auth.routes import auth_router
from app.chat.routes import chat_router

from app.auth.models import User
from app.auth.utils import get_user_from_token


app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])

templates = Jinja2Templates("app/templates")


@app.get("/")
def login_form(request: Request, user: User = Depends(get_user_from_token)):
    data = {"request": request, "user_role": user.role.value}
    return templates.TemplateResponse("base.html", data)
