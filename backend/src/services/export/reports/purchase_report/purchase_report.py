from typing import Any

from src.services.export.reports.base_report.base_report import BaseReport
from src.database.scripts.reports_queries import PURCHASE_REPORT_QUERY


class PurchaseReport(BaseReport):
    """
    Gera o Relatório de Notas Fiscais de Compras / Entradas
    utilizando a query definida em database/scripts/reports_queries.py.
    """

    @property
    def template_name(self) -> str:
        return "purchase_report.html"

    @property
    def report_filename(self) -> str:
        return "relatorio_compras.pdf"

    def fetch_data(self, **filters: Any) -> dict[str, Any]:
        company_cnpj = filters.get("company_cnpj")
        if not company_cnpj:
            raise ValueError("O parâmetro 'company_cnpj' é obrigatório para o PurchaseReport.")

        rows = self.session_manager.execute_sql(PURCHASE_REPORT_QUERY, [company_cnpj])

        notas = []
        total_vlr_prod = 0.0
        total_v_nf = 0.0

        for row in rows:
            vlr_prod = (row[5] or 0) / 100.0
            v_nf = (row[6] or 0) / 100.0

            total_vlr_prod += vlr_prod
            total_v_nf += v_nf

            notas.append({
                "mod": row[0],
                "serie": row[1],
                "nNF": row[2],
                "dEmi": row[3].strftime("%d/%m/%Y") if hasattr(row[3], "strftime") else (row[3] or "-"),
                "chNF": row[4],
                "vlrProd": vlr_prod,
                "vNF": v_nf,
            })

        return {
            "titulo_relatorio": "Relatório de Notas Fiscais de Compras",
            "cliente_nome": filters.get("cliente_nome", "Não informado"),
            "company_cnpj": company_cnpj,
            "data_inicio": filters.get("data_inicio", "-"),
            "data_fim": filters.get("data_fim", "-"),
            "notas": notas,
            "qtd_notas": len(notas),
            "total_vlrProd": total_vlr_prod,
            "total_vNF": total_v_nf,
        }
