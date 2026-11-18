import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReportFiltersSchema(BaseModel):
    company_cnpj: str = Field(..., min_length=11, max_length=18)
    cliente_nome: str = Field(default="Não informado", min_length=1)
    data_inicio: str = Field(default="-")
    data_fim: str = Field(default="-")

    @field_validator("company_cnpj")
    @classmethod
    def normalize_cnpj(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) not in (11, 14):
            raise ValueError("Documento da empresa deve ter 11 (CPF) ou 14 (CNPJ) dígitos.")
        return digits


class ExportZipResultSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    zip_bytes: bytes
    zip_filename: str
    company_cnpj: str
    cliente_nome: str
    reports_included: list[str] = Field(
        default_factory=lambda: [
            "relatorio_resumo_fiscal.pdf",
            "relatorio_compras.pdf",
            "relatorio_cfop_modelo.pdf",
            "Canceladas.pdf",
        ]
    )
