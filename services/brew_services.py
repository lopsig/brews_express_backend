import uuid
from pathlib import Path
import shutil
from database.mongo import db
from fastapi import HTTPException, UploadFile
from models.Brew import UpdateBrew
from bson import ObjectId
import os
from azure_blob_functions.blob import upload_blob_images

brews_db = db['brews']
favourite_db = db["favourites"]
# brewery_db = db["breweries"]

async def create_brew(name, style, abv, srm, ibu, ml,price, description, image, id_user): #, images):

    existing_brew = brews_db.find_one({
        "name": name,
        "id_user": id_user,
    })
    if existing_brew:
        raise HTTPException(status_code=400, detail="Brew already exists")

    url = await upload_blob_images(image)

    brews_db.insert_one({
        "name": name,
        "style": style,
        "abv": abv,
        "srm": srm,
        "ibu": ibu,
        "ml": ml,
        "price": price,
        "description": description,
        "image": url,
        "id_user":  id_user,
        #"images": [f"http://localhost:8000/{Path('images') / img.filename}" for img in images]
    })
    return {"message": "brew created successfully"}


def get_brews(id_user: str):
    query_filter = {"id_user": id_user}

    brews_cursor = brews_db.find(query_filter)
    brews_list = []
    for brew in brews_cursor:
        brew["_id"] = str(brew["_id"])  # Convert ObjectId to string
        brews_list.append(brew)

    if not brews_list:
        raise HTTPException(status_code=404, detail="No brews found for this brewery")


    return {
        "message": "Brews retrieved successfully",
        "brews": brews_list
    }


def get_single_brew(brew_id: str):
    try:
        object_id = ObjectId(brew_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Brew not found")

    brew = brews_db.find_one({"_id": object_id})

    if not brew:
        raise HTTPException(status_code=404, detail="Brew not found")

    brew["_id"] = str(brew["_id"])

    return {"brew": brew}




def update_brew(id_user: str, brew_id: str, update_data: UpdateBrew):
    brew = brews_db.find_one({"_id": ObjectId(brew_id), "id_user": id_user})
    if not brew:
        raise HTTPException(status_code=404, detail="Brew not found")

    update_fields = update_data.model_dump(exclude_unset=True)
    update_query = {"$set": update_fields}
    result = brews_db.update_one({"_id": ObjectId(brew_id)}, update_query)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brew not found")

    return {"message": "Brew updated successfully"}


async def update_brew_logo(id_user: str, brew_id: str, image: UploadFile):
    brew = brews_db.find_one({"_id": ObjectId(brew_id), "id_user": id_user})
    if not brew:
        raise HTTPException(status_code=404, detail="Brew not found")

    url = await upload_blob_images(image)

    result = brews_db.update_one(
        {"_id": ObjectId(brew_id)},
        {"$set": {"image": url}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brew not found")

    return {"message": "Brew updated successfully"}


# Agregar esta función al final de tu archivo brew_services.py

def delete_brew(id_user: str, brew_id: str):
    """Elimina una cerveza específica (solo si pertenece al proveedor)"""
    try:
        print(f"=== DEBUG DELETE BREW ===")
        print(f"Eliminando cerveza ID: {brew_id} para usuario: {id_user}")

        # Verificar que el brew_id sea válido
        if not ObjectId.is_valid(brew_id):
            raise HTTPException(status_code=400, detail="Invalid brew ID format")

        # Verificar que la cerveza existe y pertenece al proveedor
        existing_brew = brews_db.find_one({
            "_id": ObjectId(brew_id),
            "id_user": id_user  # Usando tu campo id_user como string
        })

        if not existing_brew:
            print(f"Cerveza no encontrada o sin permisos")
            print(f"Buscando con _id: {brew_id} y id_user: {id_user}")

            # Debug: buscar la cerveza solo por ID para ver si existe
            brew_exists = brews_db.find_one({"_id": ObjectId(brew_id)})
            if brew_exists:
                print(f"La cerveza existe pero id_user no coincide. Cerveza id_user: {brew_exists.get('id_user')}")
            else:
                print(f"La cerveza no existe en la base de datos")

            raise HTTPException(status_code=404, detail="Brew not found or you don't have permission")

        print(f"Cerveza encontrada: {existing_brew.get('name', 'N/A')}")

        # Eliminar imagen si existe
        if existing_brew.get('image'):
            try:
                # Tu estructura: "http://localhost:8000/images/images_brews/filename"
                image_url = existing_brew['image']
                print(f"URL de imagen: {image_url}")

                # Extraer el path relativo
                if image_url.startswith('http://localhost:8000/'):
                    image_path = image_url.replace('http://localhost:8000/', '')
                    print(f"Path de imagen: {image_path}")

                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print(f"Imagen eliminada: {image_path}")
                    else:
                        print(f"Imagen no encontrada en: {image_path}")

            except Exception as img_error:
                print(f"Error eliminando imagen: {img_error}")
                # No fallar si hay error con la imagen

        # Eliminar favoritos relacionados con esta cerveza
        try:
            favourite_db = db["favourites"]
            favourites_deleted = favourite_db.delete_many({"brew_id": ObjectId(brew_id)})
            print(f"Favoritos eliminados: {favourites_deleted.deleted_count}")
        except Exception as fav_error:
            print(f"Error eliminando favoritos: {fav_error}")
            # No fallar si hay error con favoritos

        # Eliminar la cerveza
        print(f"Procediendo a eliminar cerveza...")
        result = brews_db.delete_one({"_id": ObjectId(brew_id)})
        print(f"Resultado de eliminación - deleted_count: {result.deleted_count}")

        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Brew could not be deleted")

        print(f"Cerveza eliminada exitosamente")

        return {
            "message": "Brew deleted successfully",
            "deleted_brew_id": brew_id
        }

    except Exception as e:
        print(f"Error en delete_brew: {str(e)}")
        print(f"Tipo de error: {type(e)}")

        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")




def get_my_brews_favourites(id_user: str):
    """Obtiene todas las cervezas del proveedor que han sido marcadas como favoritas por usuarios"""
    try:
        print(f"=== DEBUG GET MY BREWS FAVOURITES ===")
        print(f"Obteniendo favoritos de cervezas del proveedor: {id_user}")

        # Pipeline de agregación para obtener favoritos de mis cervezas
        pipeline = [
            # 1. Buscar todas mis cervezas
            {"$match": {"id_user": id_user}},

            # 2. Hacer lookup con la tabla de favoritos
            {"$lookup": {
                "from": "favourites",
                "localField": "_id",
                "foreignField": "brew_id",
                "as": "favourites_info"
            }},

            # 3. Filtrar solo las cervezas que tienen favoritos
            {"$match": {"favourites_info": {"$ne": []}}},

            # 4. Hacer lookup para obtener info de los usuarios que dieron favorito
            {"$lookup": {
                "from": "users",
                "localField": "favourites_info.user_id",
                "foreignField": "_id",
                "as": "users_who_favourited"
            }},

            # 5. Proyectar los campos que queremos
            {"$project": {
                "_id": {"$toString": "$_id"},
                "name": 1,
                "style": 1,
                "abv": 1,
                "srm": 1,
                "ibu": 1,
                "ml": 1,
                "price": 1,
                "description": 1,
                "image": 1,
                "total_favourites": {"$size": "$favourites_info"},
                "favourites_info": {
                    "$map": {
                        "input": "$favourites_info",
                        "as": "fav",
                        "in": {
                            "_id": {"$toString": "$$fav._id"},
                            "user_id": {"$toString": "$$fav.user_id"},
                            "created_at": "$$fav.created_at"
                        }
                    }
                },
                "users_who_favourited": {
                    "$map": {
                        "input": "$users_who_favourited",
                        "as": "user",
                        "in": {
                            "_id": {"$toString": "$$user._id"},
                            "first_name": "$$user.first_name",
                            "last_name": "$$user.last_name",
                            "email": "$$user.email"
                        }
                    }
                }
            }},

            # 6. Ordenar por cantidad de favoritos (descendente)
            {"$sort": {"total_favourites": -1}}
        ]

        favourited_brews_cursor = brews_db.aggregate(pipeline)
        favourited_brews_list = list(favourited_brews_cursor)

        print(f"Cervezas con favoritos encontradas: {len(favourited_brews_list)}")

        # Calcular estadísticas
        total_favourites = sum(brew.get("total_favourites", 0) for brew in favourited_brews_list)
        most_popular_brew = favourited_brews_list[0] if favourited_brews_list else None

        return {
            "message": "Favourited brews retrieved successfully",
            "favourited_brews": favourited_brews_list,
            "statistics": {
                "total_brews_with_favourites": len(favourited_brews_list),
                "total_favourites_count": total_favourites,
                "most_popular_brew": {
                    "name": most_popular_brew.get("name") if most_popular_brew else None,
                    "favourites_count": most_popular_brew.get("total_favourites") if most_popular_brew else 0
                }
            }
        }

    except Exception as e:
        print(f"Error en get_my_brews_favourites: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")




def search_my_brews(id_user: str, search: str = None, style: str = None,
                    min_abv: float = None, max_abv: float = None,
                    min_price: float = None, max_price: float = None):
    """Busca y filtra las cervezas del proveedor específico"""
    try:
        print(f"=== DEBUG SEARCH MY BREWS ===")
        print(f"Usuario: {id_user}")
        print(
            f"Parámetros: search={search}, style={style}, min_abv={min_abv}, max_abv={max_abv}, min_price={min_price}, max_price={max_price}")

        # Query base: solo cervezas del usuario actual
        query = {"id_user": id_user}

        # Agregar filtros adicionales
        if search and search.strip():
            query["$and"] = query.get("$and", [])
            query["$and"].append({
                "$or": [
                    {"name": {"$regex": search.strip(), "$options": "i"}},
                    {"description": {"$regex": search.strip(), "$options": "i"}}
                ]
            })

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
            brews_list.append(brew)

        if not brews_list and not any([search, style, min_abv, max_abv, min_price, max_price]):
            # Si no hay filtros y no hay resultados, es porque no tiene cervezas
            return {
                "message": "No brews found for this brewery",
                "brews": [],
                "total_results": 0,
                "filters_applied": {}
            }

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
        print(f"Error en search_my_brews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def get_my_brew_styles(id_user: str):
    """Obtiene los estilos únicos de las cervezas del proveedor"""
    try:
        # Obtener estilos únicos solo de las cervezas de este proveedor
        unique_styles = brews_db.distinct("style", {"id_user": id_user})
        unique_styles = [style for style in unique_styles if style and style.strip()]
        unique_styles.sort()

        print(f"Estilos únicos del proveedor {id_user}: {len(unique_styles)}")

        return {
            "message": "Unique styles retrieved successfully",
            "styles": unique_styles,
            "total_styles": len(unique_styles)
        }

    except Exception as e:
        print(f"Error en get_my_brew_styles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")