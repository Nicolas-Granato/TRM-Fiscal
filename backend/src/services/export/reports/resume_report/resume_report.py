from typing import Any

from backend.src.services.export.reports.base_report.base_report import BaseReport
from backend.src.database.scripts.reports_queries import RESUME_REPORT_QUERY


class ResumeReport(BaseReport):

    @property
    def template_name(self) -> str:
        return "resume_report/resume_report.html"

    @property
    def report_filename(self) -> str:
        return "Resumo.pdf"

    def fetch_data(self, **filters: Any) -> dict[str, Any]:
        company_cnpj = filters.get("company_cnpj")
        if not company_cnpj:
            raise ValueError("O parâmetro 'company_cnpj' é obrigatório para o ResumeReport.")

        rows = self.session_manager.execute_sql(RESUME_REPORT_QUERY, [company_cnpj])

        notas = []
        geral_v_nf = 0.0

        for row in rows:
            mod = row[0]
            n_nf = row[1]
            d_emi = row[2].strftime("%d/%m/%Y") if row[2] else "-"
            ch_nf = row[3]
            v_nf = (row[4] or 0) / 100.0

            geral_v_nf += v_nf

            nNF = self._strip_leading_zeros(n_nf)

            notas.append({
                "mod": mod,
                "nNF": nNF,
                "dEmi": d_emi,
                "chNF": ch_nf,
                "vNF": v_nf,
            })

        start_date, end_date = self._get_date(self.session_manager.execute_sql, filters)

        return {
            "titulo_relatorio": "Relatório de Resumo de Saídas",
            "cliente_nome": filters.get("cliente_nome", "Não informado"),
            "company_cnpj": company_cnpj,
            "data_inicio": start_date or "-",
            "data_fim": end_date or "-",
            "notas": notas,
            "total_qtd": len(notas),
            "geral_vNF": geral_v_nf,
        }
