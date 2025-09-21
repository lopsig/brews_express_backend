from pydantic import BaseModel

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    dni: int
    birth_date: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UpdateUser(BaseModel):
    first_name: str
    last_name: str
    #email: str
    phone_number: str
    birth_date: str
    #dni: int