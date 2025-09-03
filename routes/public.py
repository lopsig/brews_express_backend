from fastapi import APIRouter, Form, UploadFile, File, Depends, Query
from services.public_services import get_all_brews, search_brews, get_unique_brew_styles
from typing import Optional

router = APIRouter(prefix="/brews_express", tags=["brews_express"])

@router.get("/all_brews")
def get_all_brews_router():
    return get_all_brews()

@router.get("/search_brews")
def search_brews_route(
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    style: Optional[str] = Query(None, description="Filtrar por estilo"),
    min_abv: Optional[float] = Query(None, description="ABV mínimo"),
    max_abv: Optional[float] = Query(None, description="ABV máximo"),
    min_price: Optional[float] = Query(None, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, description="Precio máximo")
):
    return search_brews(search, style, min_abv, max_abv, min_price, max_price)

@router.get("/all_brews_search")
def get_all_brews_router():

    return search_brews()

@router.get("/brew_styles")
def get_brew_styles_route():
    return get_unique_brew_styles()