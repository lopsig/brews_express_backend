from fastapi import APIRouter, Depends
from services.brewery_services import create_brewery, get_brewery, create_brew, get_brews
from models.Brewery import BreweryCreate
from models.Brew import BrewCreate
from middleware.jwt_middleware import JWTBearer
from services.auth_services import get_current_user_id


router = APIRouter(prefix="/breweries", tags=["breweries"])

@router.post("/create_brewery")
def create_brewery_route(
        brewery: BreweryCreate,
        user_id: str = Depends(get_current_user_id)
        ):
    return create_brewery(brewery, user_id)

@router.get("/my_brewery")
def get_brewery_router(
        user_id: str = Depends(get_current_user_id)
):
    return get_brewery(user_id)

@router.post("/create_brew")
def create_brew_route(
        brew: BrewCreate,
        user_id: str = Depends(get_current_user_id)
):
    return create_brew(brew, user_id)


@router.get("/my_brews")
def get_my_brews_route(
        user_id: str = Depends(get_current_user_id),
        brewery_id: str = None  # Optional parameter to filter by brewery_id
):

    return get_brews(user_id, brewery_id)



##########REVISAR""""""""""
# @router.get("/{brewery_id}")
# def get_single_brewery_route(
#     brewery_id: str,
#     user_id: str = Depends(get_current_user_id) # Inject the user_id from the token
# ):
#     """
#     Endpoint to retrieve a specific brewery by its ID, ensuring it belongs to the authenticated user.
#     Requires a valid JWT token in the Authorization header.
#     """
#     return get_brewery_by_id(brewery_id, user_id)

