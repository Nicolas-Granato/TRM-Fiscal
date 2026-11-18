import io
import re
import zipfile
from typing import Any, Optional

from backend.src.database.session_manager.session_manager import DuckDBSession as SessionManager
from backend.src.services.export.reports.base_report.base_report import BaseReport
from backend.src.services.export.reports.canceled_report.canceled_report import CanceledReport
from backend.src.services.export.reports.cfop_model_report.cfop_model_report import CfopModelReport
from backend.src.services.export.reports.purchase_report.purchase_report import PurchaseReport
from backend.src.services.export.reports.resume_report.resume_report import ResumeReport


class ReportExporter:
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.reports: list[BaseReport] = [
            ResumeReport(session_manager),
            PurchaseReport(session_manager),
            CfopModelReport(session_manager),
            CanceledReport(session_manager),
        ]

    def export_zip_bytes(
        self,
        company_cnpj: str,
        cliente_nome: Optional[str] = "Não informado"
    ) -> tuple[bytes, str]:
        """
        Gera os PDFs em RAM, compacta em um .zip e retorna (zip_bytes, nome_arquivo_zip).
        """
        filters: dict[str, Any] = {
            "company_cnpj": company_cnpj,
            "cliente_nome": cliente_nome
        }

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:
            for report in self.reports:
                pdf_bytes = report.generate_pdf_bytes(**filters)
                zip_file.writestr(report.report_filename, pdf_bytes)

        zip_buffer.seek(0)

        safe_name = re.sub(r"[^\w\-]", "_", cliente_nome).strip("_") or company_cnpj
        zip_filename = f"relatorios_fiscais_{safe_name}.zip"

        return zip_buffer.getvalue(), zip_filename