from pydantic import BaseModel, Field


class ErrorResponseSchema(BaseModel):
    """Resposta padrão para erros de validação (400) ou processamento (422)."""

    detail: str = Field(..., examples=["Nenhum documento fiscal válido encontrado nos arquivos .zip."])


class HealthResponseSchema(BaseModel):
    """Resposta do endpoint de verificação de saúde da API."""

    status: str = Field(default="ok")
    database: str = Field(default="duckdb-in-memory")
