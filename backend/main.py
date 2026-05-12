# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat, documents, scrape, stats

app = FastAPI(title="Molly IA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(scrape.router)
app.include_router(stats.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "Molly IA Backend"}
