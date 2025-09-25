from database.mongo import db
from models.Brewery import UpdateBrewery
from fastapi import HTTPException, UploadFile
from bson import ObjectId
from pathlib import Path
from dotenv import load_dotenv
from azure_blob_functions.blob import upload_blob_images


import uuid
import shutil
import bcrypt
import os

load_dotenv()

brewery_db = db["breweries"]
salt =  bcrypt.gensalt()

async def create_brewery(name_brewery, ruc, name_comercial, city, address,
                   contact_number, opening_hours, description, logo,
                   email, password):

    existing_brewery = brewery_db.find_one({"name_brewery": name_brewery})
    if existing_brewery:
        raise HTTPException(status_code=400, detail="Brewery already exists")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    url = await upload_blob_images(logo)

    brewery_db.insert_one(

        {
            'name_brewery': name_brewery,
            'ruc': ruc,
            'name_comercial': name_comercial,
            'city': city,
            'address': address,
            'contact_number': contact_number,
            'opening_hours': opening_hours,
            'description': description,
            'logo': url,
            'email': email,
            'password': hashed_password,
            'role': 'provider',
            'status': 'active'
        }
    )

    return {"message": "Brewery created successfully"}


def get_brewery(id_user:str):
    existing_brewery = brewery_db.find_one({"_id": ObjectId(id_user)})
    if not existing_brewery:
        raise HTTPException(status_code=404, detail="Brewery not found")

    existing_brewery["_id"] = str(existing_brewery["_id"])



    return {
        "message": "Brewery found",
        "brewery": existing_brewery,
    }



def update_brewery (id_user: str, update_data: UpdateBrewery):
    query_filter = {"_id":  ObjectId(id_user)}
    update_fields = update_data.model_dump(exclude_unset=True)
    update_query = {"$set": update_fields}
    result = brewery_db.update_one(query_filter, update_query)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brewery not found or no changes were made")

    return {"message": "Brewery updated successfully"}




async def update_brewery_logo(id_user: str, logo: UploadFile):

    url = await upload_blob_images(logo)

    result = brewery_db.update_one(
        {"_id": ObjectId(id_user)},
        {"$set": {"logo": url}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brewery not found or no changes were made")

    return {"message": "Brewery logo updated successfully", "logo_url": url}


