from fastapi import FastAPI, status, Depends, HTTPException

from typing import Annotated
from sqlalchem.orm import Session
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
