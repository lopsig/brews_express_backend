from fastapi import APIRouter, Form, UploadFile, File, Depends
from services.auth_services import get_current_user_id
from services.admin_services import (get_all_users,
                                     get_all_breweries,
                                     update_user, get_user_by_id,
                                     delete_user, get_brewery_by_id, update_brewery, delete_brewery, get_brewery_brews
                                     )
from models.User import UpdateUser
from models.Brewery import UpdateBrewery

router = APIRouter(prefix="/be/admin", tags=["be/admin"])

@router.get("/all_users")
def get_all_users_route():
    return get_all_users()

@router.get("/user/{user_id}")
def get_user_by_id_route(user_id: str):
    return get_user_by_id(user_id)

@router.put("/update_user/{user_id}")
def update_user_route(
    user_id: str,
    update_data: UpdateUser
):
    print(f"Ruta PUT /update_user/{user_id} fue llamada")  # Debug
    print(f"Datos recibidos: {update_data}")
    return update_user(user_id, update_data)

@router.delete("/delete_user/{user_id}")
def delete_user_route(user_id: str):
    return delete_user(user_id)

@router.get("/all_breweries")
def get_all_breweries_route():
    return get_all_breweries()

@router.get("/brewery/{brewery_id}")
def get_brewery_by_id_route(brewery_id: str):
    return get_brewery_by_id(brewery_id)

@router.put("/update_brewery/{brewery_id}")
def update_brewery_route(
    brewery_id: str,
    update_data: UpdateBrewery
):
    print(f"Ruta PUT /update_brewery/{brewery_id} fue llamada")
    return update_brewery(brewery_id, update_data)

@router.delete("/delete_brewery/{brewery_id}")
def delete_brewery_route(brewery_id: str):
    return delete_brewery(brewery_id)

@router.get("/brewery_brews/{brewery_id}")
def get_brewery_brews_route(brewery_id: str):
    return get_brewery_brews(brewery_id)