from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

import jwt
import os
load_dotenv()


secret_key = os.getenv("JWT_SECRET_KEY")

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403,
                    detail="Invalid authentication scheme."
                )
            payload = self.decode_token(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid token or expired token."
                )
            return payload
        else:
            raise HTTPException(
                status_code=403,
                detail="Invalid authorization code."
            )

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

