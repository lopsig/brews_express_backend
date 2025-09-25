from typing import BinaryIO
from azure.storage.blob import BlobServiceClient
from responses.response_json import response_json
from dotenv import load_dotenv
from pathlib import Path

import uuid
import os
load_dotenv()

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_name = os.getenv("AZURE_CONTAINER_NAME")

def upload_blob(filename: str, data: BinaryIO):
  try:
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    blob_client.upload_blob(data)

    file_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{filename}"
    print(file_url)


    return response_json(message= "File uploaded successfully")

  except Exception as e:
    return response_json(message= e.message, status=500)


async def upload_blob_images(logo):
    file_name= str(uuid.uuid4()) + logo.filename
    path_name = Path(os.getenv('IMAGES_PATH_BREWERIES', 'images/images_breweries'))

    direction = path_name / file_name

    data = await logo.read()
    upload_blob(file_name, data)

    return f"{os.getenv('IMAGES_URL', 'http://localhost:8000')}/{direction}"