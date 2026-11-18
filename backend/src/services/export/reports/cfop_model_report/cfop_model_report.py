from collections import defaultdict
from typing import Any

from src.services.export.reports.base_report.base_report import BaseReport
from src.database.scripts.reports_queries import CFOP_MODEL_REPORT_QUERY


class CfopModelReport(BaseReport):
    """
    Gera o Relatório de Apuração de Saídas por CFOP e Modelo (NF-e / NFC-e).
    """

    @property
    def template_name(self) -> str:
        return "cfop_model_report.html"

    @property
    def report_filename(self) -> str:
        return "relatorio_cfop_modelo.pdf"

    def fetch_data(self, **filters: Any) -> dict[str, Any]:
        company_cnpj = filters.get("company_cnpj")
        if not company_cnpj:
            raise ValueError("O parâmetro 'company_cnpj' é obrigatório para o CfopModelReport.")

        rows = self.session_manager.execute_sql(CFOP_MODEL_REPORT_QUERY, [company_cnpj])

        grupos_por_modelo: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "itens": [],
                "subtotal_vNF": 0.0,
                "subtotal_bcICMS": 0.0,
                "subtotal_vlrICMS": 0.0,
            }
        )

        geral_vNF = 0.0
        geral_bcICMS = 0.0
        geral_vlrICMS = 0.0

        for row in rows:
            mod = row[0]
            cfop = row[1]
            v_nf = (row[2] or 0) / 100.0
            bc_icms = (row[3] or 0) / 100.0
            vlr_icms = (row[4] or 0) / 100.0

            grupo = grupos_por_modelo[mod]
            grupo["itens"].append({
                "cfop": cfop,
                "vNF": v_nf,
                "bcICMS": bc_icms,
                "vlrICMS": vlr_icms,
            })
            grupo["subtotal_vNF"] += v_nf
            grupo["subtotal_bcICMS"] += bc_icms
            grupo["subtotal_vlrICMS"] += vlr_icms

            geral_vNF += v_nf
            geral_bcICMS += bc_icms
            geral_vlrICMS += vlr_icms

        modelos_lista = [
            {
                "mod": mod,
                "descricao": "NF-e" if mod == "55" else ("NFC-e" if mod == "65" else f"Modelo {mod}"),
                **dados,
            }
            for mod, dados in sorted(grupos_por_modelo.items())
        ]

        return {
            "titulo_relatorio": "Relatório de Saídas por CFOP e Modelo",
            "cliente_nome": filters.get("cliente_nome", "Não informado"),
            "company_cnpj": company_cnpj,
            "data_inicio": filters.get("data_inicio", "-"),
            "data_fim": filters.get("data_fim", "-"),
            "modelos": modelos_lista,
            "geral_vNF": geral_vNF,
            "geral_bcICMS": geral_bcICMS,
            "geral_vlrICMS": geral_vlrICMS,
        }
