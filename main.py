from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Clouds-Unihack API")

@app.get("/")
def root():
    return {"message": "Welcome to the Clouds-Unihack API"}