from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from routes import auth, breweries, brews, public, users, admin

app = FastAPI()
app.mount('/images', StaticFiles(directory='images'), name='images')

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://brewsexpress.netlify.app",
    "https://brews-express-backend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(breweries.router)
app.include_router(brews.router)
app.include_router(public.router)
app.include_router(users.router)
app.include_router(admin.router)