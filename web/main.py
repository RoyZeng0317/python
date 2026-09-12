from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# format: folder_name.folder_name.file_name
from api.endpoints import users

app = FastAPI(title="My API Project")
# split the api router to add the main app, 
app.include_router(users.router, prefix="/api/users", tags=["Users"])

app.mount("/", StaticFiles(directory="static", html=True), name="static")