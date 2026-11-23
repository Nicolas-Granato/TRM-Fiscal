import io
import zipfile
from unittest.mock import MagicMock
import pytest

from backend.src.services.pipelines.fiscal_pipeline import FiscalPipeline
from backend.src.database.scripts.insert_xml_query import INSERT_XML
from backend.src.database.scripts.cancel_xml_query import CANCEL_XML


# =====================================================================
# HELPERS E FIXTURES PARA CRIAÇÃO DE ZIPS E XMLS EM MEMÓRIA
# =====================================================================

KEY_1 = "31261112345678000199550010000001011000001011"
KEY_2 = "31261112345678000199550010000001021000001022"
KEY_3 = "31261112345678000199550010000001031000001033"
KEY_CANC = "31261112345678000199550010000009991000009999"


def make_zip(files: dict[str, bytes]) -> bytes:
    """Cria um arquivo .zip em memória a partir de {caminho_interno: conteudo_bytes}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content)
    return buf.getvalue()


def make_nfe_xml(
    chave: str,
    cstat: str = "100",
    cnpj_emit: str = "12345678000199",
    nome_emit: str = "EMPRESA TESTE LTDA",
    cnpj_dest: str = "98765432000111",
    nome_dest: str = "FORNECEDOR SA",
    v_nf: str = "150.00",
) -> bytes:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
        <NFe>
            <infNFe Id="NFe{chave}" versao="4.00">
                <ide><dhEmi>2026-11-20T10:00:00-03:00</dhEmi></ide>
                <emit>
                    <CNPJ>{cnpj_emit}</CNPJ>
                    <xNome>{nome_emit}</xNome>
                </emit>
                <dest>
                    <CNPJ>{cnpj_dest}</CNPJ>
                    <xNome>{nome_dest}</xNome>
                </dest>
                <det nItem="1"><prod><CFOP>5102</CFOP></prod></det>
                <total>
                    <ICMSTot>
                        <vProd>{v_nf}</vProd>
                        <vNF>{v_nf}</vNF>
                    </ICMSTot>
                </total>
            </infNFe>
        </NFe>
        <protNFe versao="4.00">
            <infProt>
                <cStat>{cstat}</cStat>
                <chNFe>{chave}</chNFe>
            </infProt>
        </protNFe>
    </nfeProc>
    """.encode("utf-8")


# =====================================================================
# 1. TESTES DE EXTRAÇÃO DE EVENTOS DE CANCELAMENTO (_extract_cancel_event_key)
# =====================================================================

class TestExtractCancelEventKey:
    @pytest.mark.parametrize("tp_evento", ["110111", "110112"])
    def test_extrai_chave_evento_sefaz_padrao(self, tp_evento):
        xml = f"""
        <procEventoNFe xmlns="http://www.portalfiscal.inf.br/nfe">
            <evento>
                <infEvento>
                    <chNFe>{KEY_CANC}</chNFe>
                    <tpEvento>{tp_evento}</tpEvento>
                </infEvento>
            </evento>
        </procEventoNFe>
        """.encode("utf-8")

        assert FiscalPipeline._extract_cancel_event_key(xml) == KEY_CANC

    @pytest.mark.parametrize("legacy_tag", ["cancNFe", "retCancNFe", "infCanc"])
    def test_extrai_chave_layouts_legados_cancelamento(self, legacy_tag):
        xml = f"""
        <{legacy_tag}>
            <chNFe>{KEY_CANC}</chNFe>
        </{legacy_tag}>
        """.encode("utf-8")

        assert FiscalPipeline._extract_cancel_event_key(xml) == KEY_CANC

    def test_ignora_outros_eventos_como_carta_correcao(self):
        xml = f"""
        <procEventoNFe>
            <evento>
                <infEvento>
                    <chNFe>{KEY_1}</chNFe>
                    <tpEvento>110110</tpEvento>
                </infEvento>
            </evento>
        </procEventoNFe>
        """.encode("utf-8")

        assert FiscalPipeline._extract_cancel_event_key(xml) is None

    def test_retorna_none_para_chave_invalida_ou_xml_corrompido(self):
        xml_chave_curta = b"<procEventoNFe><tpEvento>110111</tpEvento><chNFe>12345</chNFe></procEventoNFe>"
        assert FiscalPipeline._extract_cancel_event_key(xml_chave_curta) is None
        assert FiscalPipeline._extract_cancel_event_key(b"<xml_quebrado") is None


# =====================================================================
# 2. TESTES DE PROCESSAMENTO DE ZIPS (Recursividade, Múltiplos ZIPs e Empresa)
# =====================================================================

class TestZipProcessingAndCompanyInfo:
    def test_leitura_recursiva_de_zip_aninhado_e_multiplos_zips(self):
        nested_zip = make_zip({
            "subpasta/nota_aninhada.xml": make_nfe_xml(KEY_2),
        })
        zip_1 = make_zip({
            "pasta_vazia/": b"",
            "nota_raiz.xml": make_nfe_xml(KEY_1),
            "pacote_interno.zip": nested_zip,
            "arquivo_ignorado.txt": b"texto qualquer",
        })
        zip_2 = make_zip({
            "nota_zip2.xml": make_nfe_xml(KEY_3),
        })

        pipeline = FiscalPipeline(zip_file=zip_1, zip_file_2=zip_2)
        mock_sql = MagicMock()
        pipeline.run_pipeline(mock_sql)

        assert mock_sql.call_count == 1
        query, rows = mock_sql.call_args[0]
        assert query == INSERT_XML
        chaves_inseridas = {row[0] for row in rows}
        assert chaves_inseridas == {KEY_1, KEY_2, KEY_3}

    def test_identifica_empresa_pela_pasta_nfe_compra(self):
        zip_bytes = make_zip({
            "2026-11/NFe Compra/nota_fornecedor.xml": make_nfe_xml(
                KEY_1,
                cnpj_emit="11111111000111",
                nome_emit="FORNECEDOR EXTERNO",
                cnpj_dest="22222222000122",
                nome_dest="MINHA EMPRESA COMPRADORA",
            )
        })

        pipeline = FiscalPipeline(zip_file=zip_bytes)
        pipeline.run_pipeline(MagicMock())

        assert pipeline.company_name == "MINHA EMPRESA COMPRADORA"
        assert pipeline.company_cnpj == "22222222000122"

    def test_identifica_empresa_emitente_quando_nao_e_compra(self):
        zip_bytes = make_zip({
            "2026-11/NFe Venda/nota_saida.xml": make_nfe_xml(
                KEY_1,
                cnpj_emit="33333333000133",
                nome_emit="MINHA EMPRESA VENDEDORA",
            )
        })

        pipeline = FiscalPipeline(zip_file=zip_bytes)
        pipeline.run_pipeline(MagicMock())

        assert pipeline.company_name == "MINHA EMPRESA VENDEDORA"
        assert pipeline.company_cnpj == "33333333000133"


# =====================================================================
# 3. TESTES DE DETECÇÃO DE CANCELAMENTOS NO PIPELINE
# =====================================================================

class TestPipelineCancelations:
    @pytest.mark.parametrize(
        "filename",
        [
            f"eventos/{KEY_CANC}-procEventoCanc.xml",
            f"eventos/{KEY_CANC}-can.xml",
            f"eventos/evento_{KEY_CANC}_can.xml",
        ],
    )
    def test_detecta_cancelamento_pelo_nome_do_arquivo_sem_parsear_como_nfe(self, filename):
        zip_bytes = make_zip({
            filename: b"<conteudo_qualquer/>",
        })

        pipeline = FiscalPipeline(zip_file=zip_bytes)
        mock_sql = MagicMock()
        pipeline.run_pipeline(mock_sql)

        assert mock_sql.call_count == 1
        query, rows = mock_sql.call_args[0]
        assert query == CANCEL_XML
        assert rows == [(KEY_CANC,)]

    def test_detecta_cancelamento_tanto_por_evento_xml_quanto_por_cstat_na_nfe(self):
        evento_xml = f"""
        <procEventoNFe>
            <evento><infEvento><chNFe>{KEY_1}</chNFe><tpEvento>110111</tpEvento></infEvento></evento>
        </procEventoNFe>
        """.encode("utf-8")

        nfe_cstat_101 = make_nfe_xml(KEY_2, cstat="101")

        zip_bytes = make_zip({
            "evento_1.xml": evento_xml,
            "nota_2.xml": nfe_cstat_101,
        })

        pipeline = FiscalPipeline(zip_file=zip_bytes)
        mock_sql = MagicMock()
        pipeline.run_pipeline(mock_sql)

        assert mock_sql.call_count == 2
        assert mock_sql.call_args_list[0][0][0] == INSERT_XML
        assert len(mock_sql.call_args_list[0][0][1]) == 1

        cancel_query, cancel_rows = mock_sql.call_args_list[1][0]
        assert cancel_query == CANCEL_XML
        assert cancel_rows == [(KEY_1,), (KEY_2,)]


# =====================================================================
# 4. TESTES DE DEDUPLICAÇÃO, RESILIÊNCIA E LIMPEZA DE ESTADO (RN-002)
# =====================================================================

class TestDeduplicationAndResilience:
    def test_deduplica_xmls_e_cancelamentos_repetidos_nos_lotes(self):
        xml_v1 = make_nfe_xml(KEY_1, v_nf="100.00")
        xml_v2 = make_nfe_xml(KEY_1, v_nf="200.00")

        zip_1 = make_zip({
            "nota1.xml": xml_v1,
            f"canc_{KEY_1}.xml": b"<dummy/>",
        })
        zip_2 = make_zip({
            "nota1_duplicada.xml": xml_v2,
            f"{KEY_1}-can.xml": b"<dummy/>",
        })

        pipeline = FiscalPipeline(zip_file=zip_1, zip_file_2=zip_2)
        mock_sql = MagicMock()
        pipeline.run_pipeline(mock_sql)

        assert mock_sql.call_count == 2

        insert_rows = mock_sql.call_args_list[0][0][1]
        assert len(insert_rows) == 1
        assert insert_rows[0][0] == KEY_1
        assert insert_rows[0][6] == 20000

        cancel_rows = mock_sql.call_args_list[1][0][1]
        assert cancel_rows == [(KEY_1,)]

    def test_ignora_xmls_corrompidos_e_limpa_buffers_apos_execucao(self):
        zip_bytes = make_zip({
            "corrompido.xml": b"<<<XML INVALIDO>>>",
            "valida.xml": make_nfe_xml(KEY_1),
        })

        pipeline = FiscalPipeline(zip_file=zip_bytes)
        mock_sql = MagicMock()
        pipeline.run_pipeline(mock_sql)

        assert mock_sql.call_count == 1
        assert len(mock_sql.call_args[0][1]) == 1

        assert pipeline._xml_batch == []
        assert pipeline._event_canc == []

    def test_lote_vazio_ou_sem_xmls_validos_nao_chama_banco(self):
        zip_vazio = make_zip({"leiame.txt": b"sem xmls aqui"})

        pipeline = FiscalPipeline(zip_file=zip_vazio)
        mock_sql = MagicMock()
        pipeline.run_pipeline(mock_sql)

        mock_sql.assert_not_called()
        assert pipeline.company_name is None
        assert pipeline.company_cnpj is None