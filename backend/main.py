from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model.generate import generate_slogan

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SloganRequest(BaseModel):
    text: str

class SloganResponse(BaseModel):
    output: str

@app.post("/generate-slogan", response_model=SloganResponse)
async def generate_slogan_endpoint(request: SloganRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    slogan = generate_slogan(request.text.strip())
    return SloganResponse(output=slogan)

@app.get("/health")
async def health():
    return {"status": "ok"}