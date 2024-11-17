import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Request, WebSocket
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

from .schemas import UserLogin
from .models import User

from app.core.cfg import settings
from app.core.database import get_async_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(data: dict):
    to_encode = data.copy()

    return jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)


async def get_user_from_db(user_in: UserLogin, db: AsyncSession):
    if db is None:
        raise HTTPException(
            status_code=500, detail="Database session could not be obtained"
        )

    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    return user


async def get_user_from_token(
    request: Request, db: AsyncSession = Depends(get_async_session)
):
    token = request.headers.get("Authorization")

    if "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_iss": True},
            issuer=settings.ISSUER,
        )

        user_email = payload.get("sub")

        if user_email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: subject not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await db.execute(select(User).where(User.email == user_email))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_from_token_in_ws(
    websocket: WebSocket, db: AsyncSession = Depends(get_async_session)
):
    token = websocket.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found"
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET,
            algorithms=[settings.ALGORITHM],
            issuer=settings.ISSUER,
        )
        user_email = payload.get("sub")

        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: subject not found",
            )

        result = await db.execute(select(User).where(User.email == user_email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return user

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
