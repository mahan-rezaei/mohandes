from fastapi import APIRouter, status, HTTPException
from dependencies import SessionDep
from schemas.users import UserCreate
from sqlmodel import select
from models.users import User, OTP
from core.security import Hasher
from core.jwt_auth import sign_jwt
from fastapi.background import BackgroundTasks
from services.smtp import send_email


router = APIRouter(prefix="/users")


@router.post('/register', status_code=status.HTTP_200_OK)
async def register_user(user: UserCreate, session: SessionDep, background_task: BackgroundTasks):
    user_exists = await session.exec(select(User).where(User.email==user.email))

    if user_exists.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered.")

    hashed_password = Hasher.get_hashed_password(user.password)
    user_obj = User.model_validate(user, update={'password': hashed_password})
    session.add(user_obj)
    await session.flush()

    otp = OTP.generate(user_obj.email)
    session.add(otp)

    await session.commit()
    await session.refresh(user_obj)
    await session.refresh(otp)

    background_task.add_task(send_email, user_obj.email, otp.code)
    return sign_jwt(user_obj.email, user_obj.id)


@router.post('/verify', status_code=status.HTTP_200_OK)
async def verify_user():
    pass