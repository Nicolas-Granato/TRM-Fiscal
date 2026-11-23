from typing import Any

from backend.src.services.export.reports.base_report.base_report import BaseReport
from backend.src.database.scripts.reports_queries import CANCELED_REPORT_QUERY


class CanceledReport(BaseReport):
    @property
    def template_name(self) -> str:
        return "canceled_report/canceled_report.html"

    @property
    def report_filename(self) -> str:
        return "Canceladas.pdf"

    def fetch_data(self, **filters: Any) -> dict[str, Any]:
        rows = self.session_manager.execute_sql(CANCELED_REPORT_QUERY)

        notas = []
        total_vlr_prod = 0.0
        total_vlr_total = 0.0

        for row in rows:
            vlr_prod = (row[3] or 0) / 100.0
            vlr_total = (row[4] or 0) / 100.0

            total_vlr_prod += vlr_prod
            total_vlr_total += vlr_total

            nNF = self._strip_leading_zeros(row[2])

            notas.append({
                "mod": row[0],
                "serie": row[1],
                "nNF": nNF,
                "vlrProd": vlr_prod,
                "vlrTotal": vlr_total,
            })

        start_date, end_date = self._get_date(self.session_manager.execute_sql, filters)

        return {
            "titulo_relatorio": "Relatório de Notas Fiscais Canceladas",
            "cliente_nome": filters.get("cliente_nome", "Não informado"),
            "data_inicio": start_date or "-",
            "data_fim": end_date or "-",
            "notas": notas,
            "qtd_notas": len(notas),
            "total_vlrProd": total_vlr_prod,
            "total_vlrTotal": total_vlr_total,
        }
