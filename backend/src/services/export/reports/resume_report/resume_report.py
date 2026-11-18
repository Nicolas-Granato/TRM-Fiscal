from typing import Any

from backend.src.services.export.reports.base_report.base_report import BaseReport
from backend.src.database.scripts.reports_queries import RESUME_REPORT_QUERY


class ResumeReport(BaseReport):
    
    @property
    def template_name(self) -> str:
        return "resume_report/resume_report.html"

    @property
    def report_filename(self) -> str:
        return "relatorio_resumo_fiscal.pdf"

    def fetch_data(self, **filters: Any) -> dict[str, Any]:
        company_cnpj = filters.get("company_cnpj")
        if not company_cnpj:
            raise ValueError("O parâmetro 'company_cnpj' é obrigatório para o ResumeReport.")

        rows = self.session_manager.execute_sql(RESUME_REPORT_QUERY, [company_cnpj])

        resumo_itens = []
        total_qtd = 0
        geral_vlr_prod = 0.0
        geral_v_nf = 0.0
        geral_bc_icms = 0.0
        geral_vlr_icms = 0.0

        for row in rows:
            mod = row[0]
            qtd = row[1] or 0
            vlr_prod = (row[2] or 0) / 100.0
            v_nf = (row[3] or 0) / 100.0
            bc_icms = (row[4] or 0) / 100.0
            vlr_icms = (row[5] or 0) / 100.0

            total_qtd += qtd
            geral_vlr_prod += vlr_prod
            geral_v_nf += v_nf
            geral_bc_icms += bc_icms
            geral_vlr_icms += vlr_icms

            descricao = (
                "NF-e (Nota Fiscal Eletrônica)"
                if mod == "55"
                else ("NFC-e (Consumidor Eletrônica)" if mod == "65" else f"Modelo {mod}")
            )

            resumo_itens.append({
                "mod": mod,
                "descricao": descricao,
                "qtd": qtd,
                "vlrProd": vlr_prod,
                "vNF": v_nf,
                "bcICMS": bc_icms,
                "vlrICMS": vlr_icms,
            })

        return {
            "titulo_relatorio": "Relatório Resumo Fiscal",
            "cliente_nome": filters.get("cliente_nome", "Não informado"),
            "company_cnpj": company_cnpj,
            "data_inicio": filters.get("data_inicio", "-"),
            "data_fim": filters.get("data_fim", "-"),
            "resumo_itens": resumo_itens,
            "total_qtd": total_qtd,
            "geral_vlrProd": geral_vlr_prod,
            "geral_vNF": geral_v_nf,
            "geral_bcICMS": geral_bc_icms,
            "geral_vlrICMS": geral_vlr_icms,
        }
