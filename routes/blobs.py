from fastapi import APIRouter, Form, File, UploadFile
from azure_blob_functions.blob import uploadBlobToAzure

blobs_routes = APIRouter()

@blobs_routes.post("/upload")
async def upload(file: UploadFile = File(...)):
  data = await file.read()
  filename = file.filename
  return uploadBlobToAzure(filename, data, "images")