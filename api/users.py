from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from dependencies import SessionDep
from schemas.users import UserCreate, UserVerify
from sqlmodel import select, desc
from models.users import User, OTP
from core.security import Hasher
from core.jwt_auth import sign_jwt
from fastapi.background import BackgroundTasks
from services.smtp import send_email
from dependencies import get_current_user


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
async def verify_user(code: UserVerify, session: SessionDep, current_user: User=Depends(get_current_user)):
    otp_instance = await session.exec(select(OTP).where(OTP.email==current_user.email, OTP.code==code.code,
                                                        OTP.is_used==False).order_by(desc(OTP.created_at)))
    otp_instance = otp_instance.first()

    if not otp_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User does not exist.")
    if otp_instance.is_expired():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="otp expired.")

    current_user.is_verified = True
    otp_instance.is_used = True

    session.add(current_user)
    session.add(otp_instance)
    await session.commit()

    return {'detail': "user verified successfully."}

