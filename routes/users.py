from fastapi import APIRouter, Form, UploadFile, File, Depends, Query
from services.user_services import (get_all_brews, get_my_profile,
                                    update_user_profile,
                                    add_favourite,
                                    remove_from_favourites,
                                    get_my_favourites,
                                    search_brews_user,
                                    get_unique_brew_styles)

from services.auth_services import get_current_user_id
from models.User import UpdateUser
from typing import Optional


router = APIRouter(prefix="/be", tags=["be"])

@router.get("/all_brews")
def get_all_brews_router():
    return get_all_brews()

@router.get("/search_brews")
def search_brews_router(
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    style: Optional[str] = Query(None, description="Filtrar por estilo"),
    min_abv: Optional[float] = Query(None, description="ABV mínimo"),
    max_abv: Optional[float] = Query(None, description="ABV máximo"),
    min_price: Optional[float] = Query(None, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, description="Precio máximo")
):
    return search_brews_user(search, style, min_abv, max_abv, min_price, max_price)

@router.get("/brew_styles")
def get_brew_styles_router():
    return get_unique_brew_styles()




@router.get("/my_profile")
def get_my_profile_router(id_user : str = Depends(get_current_user_id),):
    return get_my_profile(id_user)

@router.put("/update_user_profile")
def update_user_profile_route(
        update_data: UpdateUser,
        id_user: str = Depends(get_current_user_id)
):
    return update_user_profile(id_user, update_data)


@router.post("/add_favourite/{brew_id}")
def add_favourite_route(
        brew_id: str,
        id_user: str = Depends(get_current_user_id)
):
    return add_favourite(id_user, brew_id)

@router.delete("/remove_favourite/{brew_id}")
def remove_favourite_route(
    brew_id: str,
    id_user: str = Depends(get_current_user_id)
):
    return remove_from_favourites(id_user, brew_id)

@router.get("/my_favourites")
def get_my_favourites_route(
    id_user: str = Depends(get_current_user_id)
):
    return get_my_favourites(id_user)