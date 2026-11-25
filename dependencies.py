from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession


SessionDep = Annotated[AsyncSession, Depends(get_session)]