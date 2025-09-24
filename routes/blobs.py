from fastapi import APIRouter, Form, File, UploadFile
from azure_blob_functions.blob import upload_blob

blobs_routes = APIRouter()

@blobs_routes.post("/upload")
async def upload(file: UploadFile = File(...)):
  data = await file.read()
  filename = file.filename
  return upload_blob(filename, data)