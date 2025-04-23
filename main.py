from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello World"}

