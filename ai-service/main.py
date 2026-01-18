from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from gemini import call_gemini
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Sample API", version="1.0.0")

class Prompt(BaseModel):
    prompt: str

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Sample FastAPI Server"}

# POST endpoint
@app.post("/analyze")
def create_item(prompt: Prompt):
    return {
        "message": call_gemini(prompt.prompt)
    }

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
