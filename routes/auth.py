from fastapi import APIRouter, HTTPException
from services.auth_services import register_user, login #login_user, login_provider
from models.User import UserRegister, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])




@router.post("/register")
def register_user_route(user: UserRegister):
    return register_user(user)

@router.post("/login")
def login_route(user: UserLogin):
    return login(user)














