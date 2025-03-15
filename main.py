from backend.config import *
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from backend.controllers import image_controller

app = FastAPI(title="Clouds-Unihack API")


# app.include_router(auth_controller.router)
app.include_router(image_controller.router)
# app.include_router(folder_controller.router)
# app.include_router(label_controller.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Clouds-Unihack API"}

# Provide error response for any server exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": "An error occurred"}
    )