from pydantic import BaseModel
from typing import Optional

class UpdateBrew(BaseModel):
    name: Optional[str] = None
    style: Optional[str] = None
    abv: Optional[float] = None
    srm: Optional[float] = None
    ibu: Optional[float] = None
    ml: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
    #brewery_id: str  # ID of the brewery to which this brew belongs
