from fastapi import HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from pydantic import ValidationError

from .models import User
from .schemas import UserCreate, UserLogin
from .utils import get_user_from_db, create_jwt_token

from app.core.cfg import settings


async def register_user_logic(request: Request, db: AsyncSession):
    try:
        if request.headers.get("Content-Type") == "application/json":
            body = await request.json()
            user_in = UserCreate(**body)
        else:
            form_data = await request.form()
            user_in = UserCreate(
                name=form_data["username"],
                email=form_data["email"],
                password=form_data["password"],
            )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
        )

    user = await get_user_from_db(user_in, db)

    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password=user_in.password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    if request.headers.get("Referer"):
        return RedirectResponse(url="/auth/login", status_code=303)
    else:
        return new_user


async def login_user_logic(response: Response, request: Request, db: AsyncSession):
    try:
        if request.headers.get("Content-Type") == "application/json":
            body = await request.json()
            user_in = UserLogin(**body)
        else:
            form_data = await request.form()
            user_in = UserLogin(
                email=form_data["email"], password=form_data["password"]
            )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
        )

    user = await get_user_from_db(user_in, db)

    if not user or user.password != user_in.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = {
        "sub": user.email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        "iss": settings.ISSUER,
    }

    access_token = create_jwt_token(user_data)

    if request.headers.get("Referer"):
        response = RedirectResponse(url="/chat/list", status_code=303)

    response.set_cookie(
        key="access_token",
        value=str(access_token),
        httponly=True,
        max_age=settings.ACCESS_COOKIE_EXPIRE_HOURS * 3600,
        path="/",
    )

    if request.headers.get("Referer"):
        return response
    else:
        return {"access_token": access_token, "token_type": "bearer"}
