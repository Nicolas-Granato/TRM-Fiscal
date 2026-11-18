from datetime import date
import re
from pydantic import BaseModel, Field, field_validator


class XmlRecordSchema(BaseModel):
    chNF: str = Field(..., min_length=44, max_length=44)
    CFOP: str = Field(..., min_length=4, max_length=4)
    dEmi: date
    cnpjEmit: str = Field(..., min_length=11, max_length=14)
    cnpjDest: str = Field(default="", max_length=14)
    vlrProd: int = Field(..., ge=0)
    vNF: int = Field(..., ge=0)
    bcICMS: int = Field(default=0, ge=0)
    vlrICMS: int = Field(default=0, ge=0)
    bcST: int = Field(default=0, ge=0)
    vlrST: int = Field(default=0, ge=0)
    vlrIPI: int = Field(default=0, ge=0)
    Outras: int = Field(default=0, ge=0)
    Desconto: int = Field(default=0, ge=0)

    @field_validator("chNF", "CFOP")
    @classmethod
    def must_be_digits(cls, value: str) -> str:
        clean = value.strip()
        if not clean.isdigit():
            raise ValueError("Campo deve conter apenas dígitos numéricos.")
        return clean

    @field_validator("cnpjEmit")
    @classmethod
    def sanitize_cnpj_emit(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) not in (11, 14):
            raise ValueError("cnpjEmit deve conter 11 ou 14 dígitos.")
        return digits

    @field_validator("cnpjDest")
    @classmethod
    def sanitize_cnpj_dest(cls, value: str) -> str:
        if value == "--Consumidor--":
            return value
        return re.sub(r"\D", "", value)

    def to_db_tuple(self) -> tuple:
        """Retorna a tupla na ordem exata esperada pelo INSERT_XML no DuckDB."""
        return (
            self.chNF,
            self.CFOP,
            self.dEmi,
            self.cnpjEmit,
            self.cnpjDest,
            self.vlrProd,
            self.vNF,
            self.bcICMS,
            self.vlrICMS,
            self.bcST,
            self.vlrST,
            self.vlrIPI,
            self.Outras,
            self.Desconto,
        )
