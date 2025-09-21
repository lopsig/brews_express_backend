from fastapi import APIRouter, Form, UploadFile, File, Depends
from services.brewery_services import create_brewery, get_brewery, update_brewery, update_brewery_logo #get_brewery, create_brew, get_brews
from models.Brewery import UpdateBrewery
# from middleware.jwt_middleware import JWTBearer
from services.auth_services import get_current_user_id


router = APIRouter(prefix="/breweries", tags=["breweries"])

@router.post("/register_brewery")
def create_brewery_route(
        name_brewery: str = Form(...),
        ruc: int = Form(...),
        name_comercial: str = Form(...),
        city: str = Form(...),
        address: str = Form(...),
        contact_number: str = Form(...),
        opening_hours: str = Form(...),
        description: str = Form(...),
        logo: UploadFile = File(...),
        email: str = Form(...),
        password: str = Form(...),
        ):
    return create_brewery(name_brewery, ruc, name_comercial, city, address, contact_number, opening_hours, description, logo, email, password)


@router.get("/brewery")
def get_brewery_router(
        id_user : str = Depends(get_current_user_id),
):
    return get_brewery(id_user)


@router.put("/update_brewery")
def update_brewery_route(
        update_data: UpdateBrewery,
        id_user: str = Depends(get_current_user_id)
):
    return update_brewery(id_user, update_data)


@router.put("/update_brewery_logo")
def update_brewery_logo_route(
    logo: UploadFile = File(...),
    id_user: str = Depends(get_current_user_id)
):
    return update_brewery_logo(id_user, logo)

