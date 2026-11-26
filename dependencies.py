from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.jwt_auth import JWTBearer
from db import get_session
from models.users import User



SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(payload: dict = Depends(JWTBearer()), session: AsyncSession = Depends(get_session)):
    identifier = payload.get("identifier", {})
    user_id = identifier.get("id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    result = await session.exec(
        select(User).where(User.id == user_id)
    )

    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user