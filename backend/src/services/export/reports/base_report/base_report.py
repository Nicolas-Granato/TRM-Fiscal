from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class BaseReport(ABC):
    REPORTS_DIR = Path(__file__).resolve().parent.parent

    def __init__(self, session_manager: Any):
        self.session_manager = session_manager
        self.env = Environment(
            loader=FileSystemLoader(str(self.REPORTS_DIR)),
            autoescape=True,
        )
        self.env.filters["brl"] = self._format_brl

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Nome do arquivo HTML dentro de templates/."""
        pass

    @property
    @abstractmethod
    def report_filename(self) -> str:
        """Nome do arquivo PDF gerado dentro do .zip final."""
        pass

    @abstractmethod
    def fetch_data(self, **filters: Any) -> dict[str, Any]:
        """Executa as queries e retorna o contexto para renderização no template Jinja2."""
        pass

    def generate_pdf_bytes(self, **filters: Any) -> bytes:
        """Orquestra a busca de dados, renderização HTML e geração do PDF em RAM."""
        context = self.fetch_data(**filters)
        template = self.env.get_template(self.template_name)
        html_rendered = template.render(**context)

        return HTML(
            string=html_rendered,
            base_url=str(self.REPORTS_DIR),
        ).write_pdf()

    @staticmethod
    def _format_brl(value: float | int | None) -> str:
        """Formata valores monetários para o padrão brasileiro (R$ 1.234,56)."""
        if value is None:
            return "R$ 0,00"
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"