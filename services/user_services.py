from database.mongo import db
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from typing import Optional

brews_db = db["brews"]
user_db = db["users"]
favourite_db = db["favourites"]


def get_all_brews ():
    all_brews_cursor = brews_db.find({})

    brews_list = []
    for brew in all_brews_cursor:
        brew["_id"] = str(brew["_id"])
        brews_list.append(brew)


    return{
        "brews": brews_list,
    }


def search_brews_user(search: Optional[str] = None, style: Optional[str] = None,
                      min_abv: Optional[float] = None, max_abv: Optional[float] = None,
                      min_price: Optional[float] = None, max_price: Optional[float] = None):
    """Busca y filtra cervezas para usuarios con parámetros opcionales"""
    try:
        print(f"=== DEBUG SEARCH BREWS USER ===")
        print(
            f"Parámetros: search={search}, style={style}, min_abv={min_abv}, max_abv={max_abv}, min_price={min_price}, max_price={max_price}")

        # Construir query dinámicamente
        query = {}

        # Filtro de búsqueda por texto (nombre o descripción)
        if search and search.strip():
            query["$or"] = [
                {"name": {"$regex": search.strip(), "$options": "i"}},
                {"description": {"$regex": search.strip(), "$options": "i"}}
            ]

        # Filtro por estilo
        if style and style.strip():
            query["style"] = {"$regex": style.strip(), "$options": "i"}

        # Filtros por ABV
        if min_abv is not None or max_abv is not None:
            query["abv"] = {}
            if min_abv is not None:
                query["abv"]["$gte"] = min_abv
            if max_abv is not None:
                query["abv"]["$lte"] = max_abv

        # Filtros por precio
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price

        print(f"Query construida: {query}")

        # Ejecutar búsqueda
        brews_cursor = brews_db.find(query).sort("name", 1)
        brews_list = []

        for brew in brews_cursor:
            brew["_id"] = str(brew["_id"])
            if "id_user" in brew:
                brew["id_user"] = str(brew["id_user"]) if brew["id_user"] else None
            brews_list.append(brew)

        print(f"Cervezas encontradas: {len(brews_list)}")

        return {
            "message": "Brews retrieved successfully",
            "brews": brews_list,
            "total_results": len(brews_list),
            "filters_applied": {
                "search": search,
                "style": style,
                "abv_range": f"{min_abv}-{max_abv}" if min_abv or max_abv else None,
                "price_range": f"{min_price}-{max_price}" if min_price or max_price else None
            }
        }

    except Exception as e:
        print(f"Error en search_brews_user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def get_unique_brew_styles():
    """Obtiene todos los estilos únicos de cerveza"""
    try:
        unique_styles = brews_db.distinct("style")
        unique_styles = [style for style in unique_styles if style and style.strip()]
        unique_styles.sort()

        print(f"Estilos únicos encontrados: {len(unique_styles)}")

        return {
            "message": "Unique styles retrieved successfully",
            "styles": unique_styles,
            "total_styles": len(unique_styles)
        }

    except Exception as e:
        print(f"Error en get_unique_brew_styles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")




def get_my_profile(id_user:str):
    existing_user = user_db.find_one({"_id": ObjectId(id_user)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_user["_id"] = str(existing_user["_id"])

    return {
        "message": "User found",
        "user": existing_user,
    }

def update_user_profile(id_user: str, update_data):
    existing_user = user_db.find_one({"_id": ObjectId(id_user)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_fields = update_data.model_dump(exclude_unset=True)
    update_query = {"$set": update_fields}
    result = user_db.update_one({"_id": ObjectId(id_user)}, update_query)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes were made")

    return {"message": "User profile updated successfully"}

def add_favourite(id_user: str, brew_id: str):
    existing_user = user_db.find_one({"_id": ObjectId(id_user)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_brew = brews_db.find_one({"_id": ObjectId(brew_id)})
    if not existing_brew:
        raise HTTPException(status_code=404, detail="Brew not found")

    existing_favourite = favourite_db.find_one({
        "user_id": ObjectId(id_user),
        "brew_id": ObjectId(brew_id)
    })
    if existing_favourite:
        raise HTTPException(status_code=400, detail="Brew is already in favourites")

    favourite_data = {
        "user_id": ObjectId(id_user),
        "brew_id": ObjectId(brew_id),
        "created_at": datetime.utcnow()
    }

    result = favourite_db.insert_one(favourite_data)

    if result.inserted_id:
        return {"message": "Brew added to favourites successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add brew to favourites")


def remove_from_favourites(id_user: str, brew_id: str):
    # Verificar que el usuario existe
    existing_user = user_db.find_one({"_id": ObjectId(id_user)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Eliminar de favoritos
    result = favourite_db.delete_one({
        "user_id": ObjectId(id_user),
        "brew_id": ObjectId(brew_id)
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favourite not found")

    return {"message": "Brew removed from favourites successfully"}


def get_my_favourites(id_user: str):
    # Verificar que el usuario existe
    existing_user = user_db.find_one({"_id": ObjectId(id_user)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Obtener favoritos del usuario con información completa de las cervezas
    pipeline = [
        {"$match": {"user_id": ObjectId(id_user)}},
        {"$lookup": {
            "from": "brews",
            "localField": "brew_id",
            "foreignField": "_id",
            "as": "brew_info"
        }},
        {"$unwind": "$brew_info"},
        {"$project": {
            "_id": {"$toString": "$_id"},
            "user_id": {"$toString": "$user_id"},
            "brew_id": {"$toString": "$brew_id"},
            "created_at": "$created_at",
            "brew_info._id": {"$toString": "$brew_info._id"},
            "brew_info.name": 1,
            "brew_info.style": 1,
            "brew_info.abv": 1,
            "brew_info.srm": 1,
            "brew_info.ibu": 1,
            "brew_info.ml": 1,
            "brew_info.price": 1,
            "brew_info.description": 1,
            "brew_info.image": 1
        }}
    ]

    favourites_cursor = favourite_db.aggregate(pipeline)
    favourites_list = list(favourites_cursor)

    return {
        "message": "Favourites retrieved successfully",
        "favourites": favourites_list
    }
