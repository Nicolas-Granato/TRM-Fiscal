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
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(api_router)