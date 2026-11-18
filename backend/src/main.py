from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.api.v1.router import api_router

app = FastAPI(
    title="TRM Fiscal API",
    description="API de processamento de lotes XML e geração de relatórios fiscais em PDF.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(api_router)