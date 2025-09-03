from database.mongo import db
from models.Brewery import BreweryCreate
from models.Brew import BrewCreate
from fastapi import HTTPException
from bson import ObjectId

brewery_db = db["breweries"]
brews_db = db["brews"]

def create_brewery(brewery: BreweryCreate, user_id: str):
    data_brewery = brewery.model_dump()
    existing_brewery = brewery_db.find_one({"name_brewery": data_brewery["name_brewery"]})
    if existing_brewery:
        raise HTTPException(status_code=400, detail="Brewery already exists")

    data_brewery["user_id"] = user_id

    try:
        result = brewery_db.insert_one(data_brewery)
        data_brewery["_id"] = str(result.inserted_id)
        #brewery_db.insert_one(data_brewery)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating brewery: {str(e)}")
    return {"message": "Brewery created successfully",
            "brewery": data_brewery}


def get_brewery(user_id: str):
    breweries_cursor = brewery_db.find({"user_id": user_id})

    breweries_list = []


    for brewery in breweries_cursor:
        brewery["_id"] = str(brewery["_id"])  # Convert ObjectId to string
        breweries_list.append(brewery)

    if not breweries_list:
        raise HTTPException(status_code=404, detail="No breweries found for this user")

    return {
        "message": "Breweries retrieved successfully",
        "breweries": breweries_list
    }




def create_brew(brew: BrewCreate, user_id: str):
    try:
        existing_brewery = brewery_db.find_one({
            "_id": ObjectId(brew.brewery_id), "user_id": user_id
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Brewery ID or error: {str(e)}")

    if not existing_brewery:
        raise HTTPException(status_code=404, detail="Brewery not found")

    existing_brew = brews_db.find_one({
        "name_brew": brew.name_brew,
        "brewery_id": brew.brewery_id
    })

    if existing_brew:
        raise HTTPException(status_code=400, detail="Brew already exists")



    return_brewery_data = dict(existing_brewery)
    return_brewery_data["_id"] = str(return_brewery_data["_id"])

    data_brew = brew.model_dump()
    data_brew["user_id"] = user_id

    try:
        result = brews_db.insert_one(data_brew)
        data_brew["_id"] = str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating brew: {str(e)}")
    return {
        "message": "Brew created successfully",
        "brew": data_brew,
    }


def get_brews(user_id: str, brewery_id: str = None):
    query_filter = {"user_id": user_id}

    if brewery_id:
        try:
            existing_brewery = brewery_db.find_one({
                "_id": ObjectId(brewery_id),
                "user_id": user_id
            })
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Brewery ID")

        if not existing_brewery:
            raise HTTPException(status_code=404, detail="Brewery not found")
        query_filter["brewery_id"] = brewery_id

    brews_cursor = brews_db.find(query_filter)
    brews_list = []
    for brew in brews_cursor:
        brew["_id"] = str(brew["_id"])  # Convert ObjectId to string
        brews_list.append(brew)

    if not brews_list:
        if brewery_id:
            raise HTTPException(status_code=404, detail="No brews found for this brewery")
        else:
            raise HTTPException(status_code=404, detail="No brews found for this user")
    return {
        "message": "Brews retrieved successfully",
        "brews": brews_list
    }




##########REVISAR""""""""""
# def get_brewery_by_id(brewery_id: str, user_id: str):
#     """
#     Retrieves a single brewery by its ID, ensuring it belongs to the specified user.
#     """
#     try:
#         # Find the brewery by its _id and ensure it belongs to the current user
#         brewery = brewery_db.find_one({"_id": ObjectId(brewery_id), "user_id": user_id})
#         if not brewery:
#             raise HTTPException(status_code=404, detail="Brewery not found, don't have permission to view it.")
#
#         brewery["_id"] = str(brewery["_id"])
#         return {
#             "message": "Brewery retrieved successfully",
#             "brewery": brewery
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Invalid Brewery ID or error: {str(e)}")
