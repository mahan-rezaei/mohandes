import jwt
import time
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status


JWT_SECRET = "300528ea6d4acbc36b57cdabb88fb014b1cd3c67e4a4e0bbeae5e1d31032d165"
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return {"access_token": token}


def sign_jwt(email, id):
    payload = {'identifier': {'email': email, 'id': id}, 'exp': time.time() + 600}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decode_jwt(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except:
        return {}


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        payload = decode_jwt(credentials.credentials)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        return payload