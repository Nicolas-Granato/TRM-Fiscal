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

            notas.append({
                "mod": mod,
                "nNF": n_nf,
                "dEmi": d_emi,
                "chNF": ch_nf,
                "vNF": v_nf,
            })

        return {
            "titulo_relatorio": "Relatório de Resumo de Saídas",
            "cliente_nome": filters.get("cliente_nome", "Não informado"),
            "company_cnpj": company_cnpj,
            "data_inicio": filters.get("data_inicio", "-"),
            "data_fim": filters.get("data_fim", "-"),
            "notas": notas,
            "total_qtd": len(notas),
            "geral_vNF": geral_v_nf,
        }
