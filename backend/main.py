from backend.config import *
from backend.middlewares.auth_middleware import AuthMiddleware

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.controllers import (
    image_controller,
    folder_controller,
    label_controller,
    auth_controller,
    recommender_shops_controller,
    recommender_stylist_controller,
)

app = FastAPI(title="Clouds-Unihack API")

# Allow CORS for frontend
origins = [f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"]

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_controller.router)
app.include_router(image_controller.router)
app.include_router(folder_controller.router)
app.include_router(label_controller.router)
app.include_router(recommender_shops_controller.router)
app.include_router(recommender_stylist_controller.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Clouds-Unihack API"}


# Provide error response for any server exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": repr(exc), "error": "An error occurred"},
    )
