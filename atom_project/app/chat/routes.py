from fastapi import (
    APIRouter,
    Request,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    status,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from pydantic import ValidationError

from .websocket import ConnectionManager
from .schemas import ChatCreate, UserEmail
from .utils import verify_user_belongs_to_chat

from app.auth.models import User, UserRole
from app.chat.models import Chat, Message
from app.auth.utils import get_user_from_token, get_user_from_token_in_ws
from app.core.database import get_async_session


chat_router = APIRouter()
manager = ConnectionManager()
templates = Jinja2Templates(directory="app/templates")


@chat_router.get("/my/{chat_id}")
async def view_chat(
    chat_id: int,
    request: Request,
    user: User = Depends(get_user_from_token),
    db: AsyncSession = Depends(get_async_session),
):
    user_access = await verify_user_belongs_to_chat(chat_id, user, db)

    if not user_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this chat.",
        )

    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    result_messages = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.timestamp.asc())
    )
    messages = result_messages.scalars().all()

    sender_names = {}
    for message in messages:
        if message.sender_id not in sender_names:
            sender_result = await db.execute(
                select(User.name).where(User.id == message.sender_id)
            )
            sender_name = sender_result.scalar_one_or_none()
            sender_names[message.sender_id] = sender_name

    data = {
        "request": request,
        "username": user.name,
        "chat_id": chat_id,
        "messages": messages,
        "sender_names": sender_names,
        "user_role": user.role.value,
        "can_write": user.can_write,
    }

    return templates.TemplateResponse("chat/chat.html", data)


@chat_router.get("/list")
async def view_chat(
    request: Request,
    user: User = Depends(get_user_from_token),
    db: AsyncSession = Depends(get_async_session),
):
    if user.role == UserRole.MODERATOR:
        result = await db.execute(
            select(Chat).options(joinedload(Chat.user1), joinedload(Chat.user2))
        )
    else:
        result = await db.execute(
            select(Chat)
            .options(joinedload(Chat.user1), joinedload(Chat.user2))
            .where((Chat.user1_id == user.id) | (Chat.user2_id == user.id))
        )

    chat_lst = [
        {"id": chat.id, "user1_id": chat.user1.name, "user2_id": chat.user2.name}
        for chat in result.scalars().all()
    ]

    data = {
        "request": request,
        "username": user.name,
        "chat_lst": chat_lst,
        "user_role": user.role.value,
    }

    return templates.TemplateResponse("chat/chat_list.html", data)


@chat_router.get("/new")
async def create_chat(request: Request, user: User = Depends(get_user_from_token)):
    return templates.TemplateResponse(
        "chat/create_chat.html", {"request": request, "user_role": user.role.value}
    )


@chat_router.post("/new")
async def create_chat(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_user_from_token),
):
    try:
        if request.headers.get("Content-Type") == "application/json":
            body = await request.json()
            chat_in = ChatCreate(**body)
        else:
            form_data = await request.form()
            chat_in = ChatCreate(user_id=form_data["other_user_id"])
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
        )

    if user.id == chat_in.user_id:
        return {"error": "Невозможно создать чат с самим собой."}

    result = await db.execute(select(User).where(User.id == chat_in.user_id))
    second_user = result.scalar_one_or_none()

    if second_user is None:
        return {"error": "Пользователь с таким ID не найден."}

    new_chat = Chat(user1_id=user.id, user2_id=chat_in.user_id)
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)

    if request.headers.get("Referer"):
        return RedirectResponse(url="/chat/list", status_code=303)
    else:
        return {"message": "Чат создан"}


@chat_router.get("/block_user/")
async def create_chat(request: Request, user: User = Depends(get_user_from_token)):
    if user.role != UserRole.MODERATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return templates.TemplateResponse(
        "chat/block_user.html", {"request": request, "user_role": user.role.value}
    )


@chat_router.post("/block_user/")
async def block_user(
    request: Request,
    user: User = Depends(get_user_from_token),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        if request.headers.get("Content-Type") == "application/json":
            body = await request.json()
            email = UserEmail(**body)
        else:
            form_data = await request.form()
            email = UserEmail(user_email=form_data["email"])
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
        )

    if user.role != UserRole.MODERATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = await db.execute(select(User).where(User.email == email.user_email))
    user_to_block = result.scalar_one_or_none()

    if user_to_block is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    user_to_block.can_write = False
    await db.commit()

    return {"message": f"Пользователь с email {email.user_email} успешно заблокирован"}


@chat_router.websocket("/my/{chat_id}/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    client_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    user = await get_user_from_token_in_ws(websocket, db)

    await manager.connect(websocket)
    try:
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()

        if not chat:
            await websocket.send_text("Chat not found")
            await manager.disconnect(websocket)
            return

        if chat.user1_id == user.id:
            receiver_id = chat.user2_id
        else:
            receiver_id = chat.user1_id

        while True:
            data = await websocket.receive_text()

            if not user.can_write:
                return

            new_message = Message(
                content=data,
                sender_id=user.id,
                receiver_id=receiver_id,
                chat_id=chat_id,
            )
            print(new_message)
            db.add(new_message)
            await db.commit()
            await db.refresh(new_message)

            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
