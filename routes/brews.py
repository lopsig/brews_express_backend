from fastapi import APIRouter, Form, UploadFile, File, Depends, Query
from services.brew_services import (create_brew, get_brews, get_single_brew, update_brew, update_brew_logo,
                                    delete_brew, get_my_brews_favourites, get_my_brew_styles, search_my_brews)
from services.auth_services import get_current_user_id
from models.Brew import UpdateBrew
from typing import Optional


router = APIRouter(prefix="/brews", tags=["brews"])

@router.post("/create_brew")
def create_brew_route(
        name: str= Form(...),
        style: str = Form(...),
        abv: float = Form(...),
        srm: float = Form(...),
        ibu: float = Form(...),
        ml : int = Form(...),
        price : float = Form(...),
        description: str = Form(...),
        image: UploadFile = File(...),
        id_user: str = Form(...),
        #images: list[UploadFile] = Form(...),
):
    return create_brew(name, style, abv, srm, ibu, ml, price, description, image, id_user)#, images)

@router.get("/my_brews")
def get_my_brews_route(
        id_user: str = Depends(get_current_user_id),
):
    return get_brews(id_user)



@router.get("/search_my_brews")
def search_my_brews_route(
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    style: Optional[str] = Query(None, description="Filtrar por estilo"),
    min_abv: Optional[float] = Query(None, description="ABV mínimo"),
    max_abv: Optional[float] = Query(None, description="ABV máximo"),
    min_price: Optional[float] = Query(None, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, description="Precio máximo"),
    id_user: str = Depends(get_current_user_id)
):
    return search_my_brews(id_user, search, style, min_abv, max_abv, min_price, max_price)


@router.get("/my_brew_styles")
def get_my_brew_styles_route(
    id_user: str = Depends(get_current_user_id)
):
    return get_my_brew_styles(id_user)



@router.put("/update_brew/{brew_id}")
def update_brew_route(
        brew_id: str,
        update_data: UpdateBrew,
        id_user: str = Depends(get_current_user_id),
):
    return update_brew(id_user, brew_id, update_data)

@router.put("/update_brew_image/{brew_id}")
def update_brew_logo_route(
        brew_id: str,
        image: UploadFile = File(...),
        id_user: str = Depends(get_current_user_id),

):
    return update_brew_logo(id_user, brew_id, image)


@router.delete("/delete_brew/{brew_id}")
def delete_brew_route(
        brew_id: str,
        id_user: str = Depends(get_current_user_id),
):
    return delete_brew(id_user, brew_id)



@router.get("/my_brews_favourites")
def get_my_brews_favourites_route(
        id_user: str = Depends(get_current_user_id),
):
    return get_my_brews_favourites(id_user)



@router.get("/{brew_id}")
def get_single_brew_route(brew_id: str):
    return get_single_brew(brew_id)























