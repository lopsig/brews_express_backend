import datetime

from database.mongo import db
from models.User import UserRegister, UserLogin
from dotenv import load_dotenv
import os
import bcrypt
import jwt
from fastapi import HTTPException, Request
load_dotenv()

user_db = db["users"]
brewery_db = db["breweries"]

salt = bcrypt.gensalt()

def register_user(user: UserRegister):
    data_user = user.model_dump()
    existing_user = user_db.find_one({"email": data_user["email"]})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hashpw(
        data_user["password"].encode('utf-8'),
        salt
    ).decode('utf-8')

    data_user["password"] = hashed_password
    data_user['role'] = 'user'
    data_user['status'] = 'active'
    user_db.insert_one(data_user)

    return {"message": "User registered successfully"}



def login(user: UserLogin):
    user_data = user.model_dump()
    email = user_data["email"]
    password = user_data["password"]

    existing_user = user_db.find_one({"email": email})
    if not existing_user:
        existing_user = brewery_db.find_one({"email": email})

    if not existing_user:
        raise HTTPException(status_code=404, detail="User does not exist")

    check_password = bcrypt.checkpw(
        password.encode('utf-8'),
        existing_user["password"].encode('utf-8')
    )

    if not check_password:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    payload = {
        "id": str(existing_user["_id"]),
        "email": existing_user["email"],
        "role": existing_user.get("role"),
        # "exp": datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    if payload["role"] == "provider":
        payload["contact_number"] = existing_user.get("contact_number", None)
        payload["ruc"] = existing_user.get("ruc", None)
    elif payload["role"] == "user":
        payload["phone_number"] = existing_user.get("phone_number", None)
        payload["dni"] = existing_user.get("dni", None)

    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise HTTPException(status_code=500, detail="JWT secret key not configured")

    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return {
        "message": "Login successful",
        "token": token,
        "role": payload["role"],
        "id_user": payload["id"],
    }





def decode_token(token: str):
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise HTTPException(status_code=500, detail="JWT secret key not configured")

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_id(request: Request):
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer"):
        token = authorization.split(" ")[1]

        try:
            payload = decode_token(token)
            user_id = payload["id"]
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token: User ID not found")
            return user_id
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    return None




