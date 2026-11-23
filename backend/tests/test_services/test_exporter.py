import io
import zipfile
from unittest.mock import MagicMock
import pytest

from backend.src.services.export.exporter import ReportExporter
from backend.src.services.export.reports.resume_report.resume_report import ResumeReport
from backend.src.services.export.reports.purchase_report.purchase_report import PurchaseReport
from backend.src.services.export.reports.cfop_model_report.cfop_model_report import CfopModelReport
from backend.src.services.export.reports.canceled_report.canceled_report import CanceledReport


# =====================================================================
# FIXTURES
# =====================================================================

@pytest.fixture
def mock_session_manager() -> MagicMock:
    return MagicMock()


@pytest.fixture
def exporter_with_mocked_reports(mock_session_manager) -> ReportExporter:
    """Instancia o ReportExporter e substitui apenas generate_pdf_bytes por mocks rápidos."""
    exporter = ReportExporter(session_manager=mock_session_manager)

    for idx, report in enumerate(exporter.reports, start=1):
        report.generate_pdf_bytes = MagicMock(
            return_value=f"%PDF-1.4 mock content {idx}".encode("utf-8")
        )

    return exporter


# =====================================================================
# 1. TESTES DE INICIALIZAÇÃO E ORQUESTRAÇÃO
# =====================================================================

class TestReportExporterInit:
    def test_inicializa_os_quatro_relatorios_na_ordem_esperada(self, mock_session_manager):
        exporter = ReportExporter(session_manager=mock_session_manager)

        assert exporter.session_manager is mock_session_manager
        assert len(exporter.reports) == 4
        assert isinstance(exporter.reports[0], ResumeReport)
        assert isinstance(exporter.reports[1], PurchaseReport)
        assert isinstance(exporter.reports[2], CfopModelReport)
        assert isinstance(exporter.reports[3], CanceledReport)

        for report in exporter.reports:
            assert report.session_manager is mock_session_manager


# =====================================================================
# 2. TESTES DE EXPORTAÇÃO DO ZIP (export_zip_bytes)
# =====================================================================

class TestExportZipBytes:
    def test_gera_zip_valido_com_todos_os_pdfs_e_repassa_filtros(
        self, exporter_with_mocked_reports
    ):
        cnpj = "12345678000199"
        cliente = "TRM Sistemas Ltda"

        zip_bytes, zip_filename = exporter_with_mocked_reports.export_zip_bytes(
            company_cnpj=cnpj,
            cliente_nome=cliente,
        )

        assert zip_filename == "relatorios_fiscais_TRM_Sistemas_Ltda.zip"
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 0

        for report in exporter_with_mocked_reports.reports:
            report.generate_pdf_bytes.assert_called_once_with(
                company_cnpj=cnpj,
                cliente_nome=cliente,
            )

        with zipfile.ZipFile(io.BytesIO(zip_bytes), mode="r") as zf:
            assert zf.testzip() is None
            arquivos_no_zip = zf.namelist()
            assert len(arquivos_no_zip) == 4

            for idx, report in enumerate(exporter_with_mocked_reports.reports, start=1):
                assert report.report_filename in arquivos_no_zip
                conteudo = zf.read(report.report_filename)
                assert conteudo == f"%PDF-1.4 mock content {idx}".encode("utf-8")

    def test_usa_valor_padrao_quando_cliente_nome_nao_e_informado(
        self, exporter_with_mocked_reports
    ):
        cnpj = "12345678000199"

        _, zip_filename = exporter_with_mocked_reports.export_zip_bytes(company_cnpj=cnpj)

        assert zip_filename == "relatorios_fiscais_Não_informado.zip"
        for report in exporter_with_mocked_reports.reports:
            report.generate_pdf_bytes.assert_called_once_with(
                company_cnpj=cnpj,
                cliente_nome="Não informado",
            )


# =====================================================================
# 3. TESTES DE SANITIZAÇÃO DE NOME E EXCEÇÕES
# =====================================================================

class TestZipFilenameSanitizationAndErrors:
    @pytest.mark.parametrize(
        "cliente_nome, expected_filename",
        [
            ("Supermercado João & Maria S/A", "relatorios_fiscais_Supermercado_João___Maria_S_A.zip"),
            ("  ***Empresa Teste***  ", "relatorios_fiscais_Empresa_Teste.zip"),
            ("Empresa-Filial_01", "relatorios_fiscais_Empresa-Filial_01.zip"),
            ("///---///", "relatorios_fiscais_---.zip"),
            ("$$$###@@@", "relatorios_fiscais_12345678000199.zip"),
            ("", "relatorios_fiscais_12345678000199.zip"),
        ],
    )
    def test_sanitiza_nome_do_arquivo_zip_corretamente(
        self, exporter_with_mocked_reports, cliente_nome, expected_filename
    ):
        _, zip_filename = exporter_with_mocked_reports.export_zip_bytes(
            company_cnpj="12345678000199",
            cliente_nome=cliente_nome,
        )
        assert zip_filename == expected_filename

    def test_cliente_nome_none_lanca_type_error_no_regex_atual(
        self, exporter_with_mocked_reports
    ):
        """
        Documenta o comportamento atual caso cliente_nome=None seja passado explicitamente:
        re.sub(r'[^\\w\\-]', '_', None) levanta TypeError.
        """
        with pytest.raises(TypeError):
            exporter_with_mocked_reports.export_zip_bytes(
                company_cnpj="12345678000199",
                cliente_nome=None,
            )

    def test_propaga_excecao_se_um_relatorio_falhar(self, exporter_with_mocked_reports):
        exporter_with_mocked_reports.reports[1].generate_pdf_bytes.side_effect = RuntimeError(
            "Falha ao renderizar PurchaseReport"
        )

        with pytest.raises(RuntimeError, match="Falha ao renderizar PurchaseReport"):
            exporter_with_mocked_reports.export_zip_bytes(
                company_cnpj="12345678000199",
                cliente_nome="Cliente Teste",
            )