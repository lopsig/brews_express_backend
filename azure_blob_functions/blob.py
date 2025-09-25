from typing import BinaryIO
from azure.storage.blob import BlobServiceClient
from responses.response_json import response_json
from dotenv import load_dotenv
from pathlib import Path

import uuid
import os
load_dotenv()

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_images = os.getenv("AZURE_CONTAINER_IMAGES")
container_brews = os.getenv("AZURE_CONTAINER_BREWS")
container_breweries = os.getenv("AZURE_CONTAINER_BREWERIES")


def uploadBlobToAzure(filename: str, data: BinaryIO, container_name:str):
  try:
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    blob_client.upload_blob(data)

    file_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{filename}"
    print(file_url)


    return response_json(message= "File uploaded successfully")

  except Exception as e:
    return response_json(message= e.message, status=500)


async def upload_blob_images(logo, typeLogo:str):
    container="images"
    if typeLogo=="brews":
      container = container_brews
    else:
      container = container_breweries

    file_name= str(uuid.uuid4()) + logo.filename

    direction = container / file_name

    data = await logo.read()
    uploadBlobToAzure(file_name, data, container)

    return f"{os.getenv('IMAGES_URL', 'http://localhost:8000')}/{direction}"