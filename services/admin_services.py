from database.mongo import db
from bson import ObjectId
from fastapi import HTTPException


user_db = db["users"]
brewery_db = db["breweries"]
brews_db = db['brews']
# favourite_db = db["favourites"]


def get_all_users():
    all_users_cursor = user_db.find({})

    users_list = []
    for user in all_users_cursor:
        user["_id"] = str(user["_id"])
        users_list.append(user)

    return {
        "users": users_list

    }


def get_user_by_id (user_id: str):
    try:
        existing_user = user_db.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_user["_id"] = str(existing_user["_id"])

        return {
            "message": "User found",
            "user": existing_user
        }
    except Exception as e:
        if "Invalid ObjectId" in str(e):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        raise HTTPException(status_code=500, detail="Internal server error")




def update_user(user_id: str, update_data):

    try:
        existing_user = user_db.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        update_fields = update_data.model_dump(exclude={"_id"})

        # Remover campos que no deberían ser actualizados si están vacíos
        filtered_fields = {k: v for k, v in update_fields.items() if v is not None and v != ""}

        if not filtered_fields:
            raise HTTPException(status_code=404, detail="No valid fields to update")

        update_query = {"$set": filtered_fields}
        result = user_db.update_one({"_id": ObjectId(user_id)}, update_query)

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        if result.modified_count == 0:
            return {"message": "No changes were made - data is identical"}

        updated_user = user_db.find_one({"_id": ObjectId(user_id)})
        updated_user["_id"] = str(updated_user["_id"])

        return {
            "message": "User updated successfully",
            "user": updated_user
        }

    except Exception as e:
        if "Invalid ObjectId" in str(e):
            raise HTTPException(status_code=404, detail="Invalid user ID format")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=404, detail="Internal server error")



def delete_user(user_id:str):
    try:
        existing_user = user_db.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        if existing_user.get("role") == "admin":
            raise HTTPException(status_code=404, detail="Cannot delete admin user")

        result = user_db.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found or cannot be deleted")

        return {"message": "User deleted successfully"}

    except Exception as e:
        if "Invalid ObjectId" in str(e):
            raise HTTPException(status_code=404, detail="Invalid user ID format")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=404, detail="Internal server error")






def get_all_breweries():
    all_breweries_cursor = brewery_db.find({})

    breweries_list = []
    for brewery in all_breweries_cursor:
        brewery["_id"] = str(brewery["_id"])
        breweries_list.append(brewery)

    return {
        "breweries": breweries_list
    }


def get_brewery_by_id(brewery_id: str):
    try:
        print(f"=== DEBUG GET BREWERY BY ID ===")
        print(f"Buscando cervecería con ID: {brewery_id}")

        if not ObjectId.is_valid(brewery_id):
            raise HTTPException(status_code=400, detail="Invalid brewery ID format")

        existing_brewery = brewery_db.find_one({"_id": ObjectId(brewery_id)})
        if not existing_brewery:
            print(f"Cervecería no encontrada con ID: {brewery_id}")
            raise HTTPException(status_code=404, detail="Brewery not found")

        existing_brewery["_id"] = str(existing_brewery["_id"])
        print(f"Cervecería encontrada: {existing_brewery.get('name_brewery', 'N/A')}")

        return {"message": "Brewery found", "brewery": existing_brewery}

    except Exception as e:
        print(f"Error en get_brewery_by_id: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")


def update_brewery(brewery_id: str, update_data):
    try:
        print(f"=== DEBUG UPDATE BREWERY ===")
        print(f"Intentando actualizar cervecería con ID: {brewery_id}")

        if not ObjectId.is_valid(brewery_id):
            raise HTTPException(status_code=400, detail="Invalid brewery ID format")

        existing_brewery = brewery_db.find_one({"_id": ObjectId(brewery_id)})
        if not existing_brewery:
            print(f"Cervecería no encontrada con ID: {brewery_id}")
            raise HTTPException(status_code=404, detail="Brewery not found")

        print(f"Cervecería encontrada: {existing_brewery.get('name_brewery', 'N/A')}")

        update_fields = update_data.model_dump(exclude_unset=True)
        filtered_fields = {k: v for k, v in update_fields.items() if v is not None and v != ""}

        if not filtered_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        print(f"Campos a actualizar: {filtered_fields}")

        update_query = {"$set": filtered_fields}
        result = brewery_db.update_one({"_id": ObjectId(brewery_id)}, update_query)

        if result.modified_count == 0:
            return {"message": "No changes were made - data is identical"}

        print(f"Cervecería actualizada exitosamente. Campos modificados: {result.modified_count}")

        updated_brewery = brewery_db.find_one({"_id": ObjectId(brewery_id)})
        updated_brewery["_id"] = str(updated_brewery["_id"])

        return {"message": "Brewery updated successfully", "brewery": updated_brewery}

    except Exception as e:
        print(f"Error en update_brewery: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")


def delete_brewery(brewery_id: str):
    try:
        print(f"=== DEBUG DELETE BREWERY ===")
        print(f"Intentando eliminar cervecería con ID: {brewery_id}")

        if not ObjectId.is_valid(brewery_id):
            raise HTTPException(status_code=400, detail="Invalid brewery ID format")

        existing_brewery = brewery_db.find_one({"_id": ObjectId(brewery_id)})
        if not existing_brewery:
            print(f"Cervecería no encontrada con ID: {brewery_id}")
            raise HTTPException(status_code=404, detail="Brewery not found")

        print(f"Cervecería encontrada: {existing_brewery.get('name_brewery', 'N/A')}")

        # Verificar si la cervecería tiene cervezas asociadas
        associated_brews = brews_db.count_documents({"brewery_id": ObjectId(brewery_id)})
        if associated_brews > 0:
            print(f"Cervecería tiene {associated_brews} cervezas asociadas")
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete brewery. It has {associated_brews} associated brews. Delete brews first."
            )

        # Eliminar la cervecería
        print(f"Procediendo a eliminar cervecería...")
        result = brewery_db.delete_one({"_id": ObjectId(brewery_id)})
        print(f"Resultado de eliminación - deleted_count: {result.deleted_count}")

        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Brewery could not be deleted")

        print(f"Cervecería eliminada exitosamente")

        return {"message": "Brewery deleted successfully", "deleted_brewery_id": brewery_id}

    except Exception as e:
        print(f"Error en delete_brewery: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")


def get_brewery_brews(brewery_id: str):
    """Obtiene todas las cervezas de una cervecería específica"""
    try:
        print(f"=== DEBUG GET BREWERY BREWS ===")
        print(f"Obteniendo cervezas de cervecería ID: {brewery_id}")

        if not ObjectId.is_valid(brewery_id):
            raise HTTPException(status_code=400, detail="Invalid brewery ID format")

        # Verificar que la cervecería existe
        existing_brewery = brewery_db.find_one({"_id": ObjectId(brewery_id)})
        if not existing_brewery:
            raise HTTPException(status_code=404, detail="Brewery not found")

        # Obtener cervezas de la cervecería
        brewery_brews_cursor = brews_db.find({"brewery_id": ObjectId(brewery_id)})
        brews_list = []

        for brew in brewery_brews_cursor:
            brew["_id"] = str(brew["_id"])
            brew["brewery_id"] = str(brew["brewery_id"])
            brews_list.append(brew)

        print(f"Cervezas encontradas: {len(brews_list)}")

        return {
            "message": "Brewery brews retrieved successfully",
            "brewery_name": existing_brewery.get("name_brewery"),
            "brews": brews_list,
            "total_brews": len(brews_list)
        }

    except Exception as e:
        print(f"Error en get_brewery_brews: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error")












