from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Clouds-Unihack API")

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