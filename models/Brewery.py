from pydantic import BaseModel, EmailStr
from typing import Optional

class UpdateBrewery(BaseModel):
    name_brewery: Optional[str] = None
    ruc: Optional[int] = None
    name_comercial: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    contact_number: Optional[int] = None
    opening_hours: Optional[str] = None
    description: Optional[str] = None
    # email: Optional[EmailStr] = None
    # password: Optional[str] = None
