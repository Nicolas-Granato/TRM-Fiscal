from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import duckdb
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class BaseReport(ABC):
    REPORTS_DIR = Path(__file__).resolve().parent
    TEMPLATES_DIR = REPORTS_DIR / "templates"

    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con
        self.env = Environment(
            loader=FileSystemLoader(str(self.TEMPLATES_DIR)),
            autoescape=True,
        )
        self.env.filters["brl"] = self._format_brl

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Nome do arquivo HTML dentro da pasta templates/."""
        pass

    @property
    @abstractmethod
    def report_filename(self) -> str:
        """Nome sugerido do arquivo PDF dentro do .zip final."""
        pass

    @abstractmethod
    def fetch_data(self, **filters: Any) -> dict[str, Any]:
        """
        Executa as queries na sessão DuckDB e retorna o dicionário
        de contexto que será injetado no template Jinja2.
        """
        pass

    def generate_pdf_bytes(self, **filters: Any) -> bytes:
        context = self.fetch_data(**filters)
        template = self.env.get_template(self.template_name)
        html_rendered = template.render(**context)

        return HTML(
            string=html_rendered,
            base_url=str(self.REPORTS_DIR),
        ).write_pdf()

    @staticmethod
    def _format_brl(value: float | int | None) -> str:
        if value is None:
            return "R$ 0,00"
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
