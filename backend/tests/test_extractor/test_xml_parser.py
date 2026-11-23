import xml.etree.ElementTree as ET
import pytest
from backend.src.extractors.xml_parser import XmlParser


# =====================================================================
# FIXTURES DE XML (Exemplos realistas de NF-e, NFC-e e Cancelamentos)
# =====================================================================

VALID_KEY = "31261112345678000199550010000001231000001234"


@pytest.fixture
def nfe_completa_xml() -> bytes:
    """XML padrão de NF-e (modelo 55) com namespace SEFAZ e todos os impostos."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
        <NFe>
            <infNFe Id="NFe{VALID_KEY}" versao="4.00">
                <ide>
                    <dhEmi>2026-11-17T14:30:00-03:00</dhEmi>
                </ide>
                <emit>
                    <CNPJ>12.345.678/0001-99</CNPJ>
                    <xNome>TRM SISTEMAS LTDA</xNome>
                </emit>
                <dest>
                    <CNPJ>98.765.432/0001-11</CNPJ>
                    <xNome>CLIENTE EXEMPLO SA</xNome>
                </dest>
                <det nItem="1">
                    <prod>
                        <CFOP>5102</CFOP>
                    </prod>
                </det>
                <total>
                    <ICMSTot>
                        <vBC>100.50</vBC>
                        <vICMS>18.09</vICMS>
                        <vBCST>50.00</vBCST>
                        <vST>9.00</vST>
                        <vProd>100.50</vProd>
                        <vDesc>5.50</vDesc>
                        <vIPI>10.00</vIPI>
                        <vOutro>2.00</vOutro>
                        <vNF>116.00</vNF>
                    </ICMSTot>
                </total>
            </infNFe>
        </NFe>
        <protNFe versao="4.00">
            <infProt>
                <cStat>100</cStat>
                <chNFe>{VALID_KEY}</chNFe>
            </infProt>
        </protNFe>
    </nfeProc>
    """.encode("utf-8")


@pytest.fixture
def nfce_minima_xml() -> bytes:
    """NFC-e (modelo 65) sem protocolo, sem tags opcionais (IPI/ST/Desc) e com CPF no dest."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <NFe xmlns="http://www.portalfiscal.inf.br/nfe">
        <infNFe Id="NFe{VALID_KEY}" versao="4.00">
            <ide>
                <dEmi>2026-11-18</dEmi>
            </ide>
            <emit>
                <CNPJ>12345678000199</CNPJ>
                <xNome>LOJA VAREJO NFC-E</xNome>
            </emit>
            <dest>
                <CPF>123.456.789-01</CPF>
                <xNome>CONSUMIDOR FINAL</xNome>
            </dest>
            <det nItem="1">
                <prod>
                    <CFOP>5405</CFOP>
                </prod>
            </det>
            <total>
                <ICMSTot>
                    <vProd>49.90</vProd>
                    <vNF>49.90</vNF>
                </ICMSTot>
            </total>
        </infNFe>
    </NFe>
    """.encode("utf-8")


# =====================================================================
# 1. TESTES DE MÉTODOS UTILITÁRIOS (_to_cents, _format_date, get_tag_text)
# =====================================================================

class TestXmlParserHelpers:
    @pytest.mark.parametrize(
        "raw_value, expected_cents",
        [
            ("100.50", 10050),
            ("100,50", 10050),
            ("0", 0),
            ("0.00", 0),
            ("19.999", 2000),      # Arredondamento correto
            ("1.15", 115),         # Evita imprecisão de ponto flutuante (1.15 * 100 = 114.9999...)
            ("invalido", 0),
            ("", 0),
            (None, 0),
        ],
    )
    def test_to_cents(self, raw_value, expected_cents):
        assert XmlParser._to_cents(raw_value) == expected_cents

    @pytest.mark.parametrize(
        "raw_date, expected_date",
        [
            ("2026-11-17T14:30:00-03:00", "2026-11-17"),
            ("2026-11-17T00:00:00Z", "2026-11-17"),
            ("2026-11-17", "2026-11-17"),
            ("", ""),
        ],
    )
    def test_format_date(self, raw_date, expected_date):
        assert XmlParser._format_date(raw_date) == expected_date

    def test_get_tag_text_com_e_sem_namespace(self):
        xml = ET.fromstring('<root xmlns="http://teste.com"><filho>  Valor Limpo  </filho></root>')
        assert XmlParser.get_tag_text(xml, "filho") == "Valor Limpo"
        assert XmlParser.get_tag_text(xml, "inexistente", default="PADRAO") == "PADRAO"
        assert XmlParser.get_tag_text(None, "filho", default="NULO") == "NULO"


# =====================================================================
# 2. TESTES DE EXTRAÇÃO DE CHAVE E CANCELAMENTO
# =====================================================================

class TestAccessKeyAndCancelation:
    def test_extract_access_key_via_chnfe(self, nfe_completa_xml):
        root = ET.fromstring(nfe_completa_xml)
        assert XmlParser._extract_access_key(root) == VALID_KEY

    def test_extract_access_key_fallback_atributo_id(self, nfce_minima_xml):
        # NFC-e sem <protNFe>/<chNFe> deve extrair do atributo Id="NFe..." de <infNFe>
        root = ET.fromstring(nfce_minima_xml)
        assert XmlParser._extract_access_key(root) == VALID_KEY

    def test_extract_access_key_invalida_retorna_vazio(self):
        xml = ET.fromstring('<NFe><infNFe Id="NFe12345"><chNFe>999</chNFe></infNFe></NFe>')
        assert XmlParser._extract_access_key(xml) == ""

    @pytest.mark.parametrize("cstat", ["101", "135", "151"])
    def test_extract_canceled_key_from_nfe_cancelada(self, cstat):
        xml_cancelado = f"""
        <nfeProc>
            <NFe><infNFe Id="NFe{VALID_KEY}"></infNFe></NFe>
            <protNFe>
                <infProt>
                    <cStat>{cstat}</cStat>
                    <chNFe>{VALID_KEY}</chNFe>
                </infProt>
            </protNFe>
        </nfeProc>
        """.encode("utf-8")

        assert XmlParser.extract_canceled_key_from_nfe(xml_cancelado) == VALID_KEY

    def test_extract_canceled_key_from_nfe_autorizada_retorna_none(self, nfe_completa_xml):
        # cStat 100 (Autorizada) não deve ser considerada cancelada
        assert XmlParser.extract_canceled_key_from_nfe(nfe_completa_xml) is None

    def test_extract_canceled_key_xml_corrompido_retorna_none(self):
        assert XmlParser.extract_canceled_key_from_nfe(b"<xml_quebrado>") is None


# =====================================================================
# 3. TESTES DE IDENTIFICAÇÃO DA EMPRESA (get_company_info)
# =====================================================================

class TestGetCompanyInfo:
    def test_identifica_emitente_em_pasta_padrao(self, nfe_completa_xml):
        nome, doc = XmlParser.get_company_info(
            nfe_completa_xml,
            zip_filepath="Lote_Novembro/NFe Saida/nota_01.xml",
        )
        assert nome == "TRM SISTEMAS LTDA"
        assert doc == "12345678000199"

    def test_identifica_destinatario_em_pasta_nfe_compra(self, nfe_completa_xml):
        # Case-insensitive para "NFe Compra" no caminho dentro do ZIP
        nome, doc = XmlParser.get_company_info(
            nfe_completa_xml,
            zip_filepath="Cliente_X/2026/NFE COMPRA/nota_entrada.xml",
        )
        assert nome == "CLIENTE EXEMPLO SA"
        assert doc == "98765432000111"

    def test_aceita_et_element_diretamente(self, nfce_minima_xml):
        root = ET.fromstring(nfce_minima_xml)
        nome, doc = XmlParser.get_company_info(root, zip_filepath="nfe compra/cupom.xml")
        assert nome == "CONSUMIDOR FINAL"
        assert doc == "12345678901"

    def test_retorna_none_para_xml_invalido_ou_sem_infnfe(self):
        assert XmlParser.get_company_info(b"invalido", "pasta/a.xml") == (None, None)
        assert XmlParser.get_company_info(b"<outroXml></outroXml>", "pasta/a.xml") == (None, None)


# =====================================================================
# 4. TESTES DO PARSER PRINCIPAL (parse_xml - RN-001 / RN-002)
# =====================================================================

class TestParseXml:
    def test_parse_xml_nfe_completa_sucesso(self, nfe_completa_xml):
        batch = []
        XmlParser.parse_xml(nfe_completa_xml, batch)

        assert len(batch) == 1
        registro = batch[0]

        assert registro == (
            VALID_KEY,          # chNF
            "5102",             # cfop
            "2026-11-17",       # dEmi formatada
            "12345678000199",   # cnpj_emit sanitizado
            "98765432000111",   # cnpj_dest sanitizado
            10050,              # vlrProd (100.50)
            11600,              # vNF (116.00)
            10050,              # bcICMS (100.50)
            1809,               # vlrICMS (18.09)
            5000,               # bcST (50.00)
            900,                # vlrST (9.00)
            1000,               # vlrIPI (10.00)
            200,                # outras (2.00)
            550,                # desconto (5.50)
        )

    def test_parse_xml_nfce_tags_opcionais_ausentes_assumem_zero(self, nfce_minima_xml):
        batch = []
        XmlParser.parse_xml(nfce_minima_xml, batch)

        assert len(batch) == 1
        registro = batch[0]

        assert registro == (
            VALID_KEY,          # chNF
            "5405",             # cfop
            "2026-11-18",       # dEmi (tag antiga <dEmi>)
            "12345678000199",   # cnpj_emit
            "12345678901",      # cnpj_dest (CPF sanitizado)
            4990,               # vlrProd
            4990,               # vNF
            0,                  # bcICMS default
            0,                  # vlrICMS default
            0,                  # bcST default
            0,                  # vlrST default
            0,                  # vlrIPI default
            0,                  # outras default
            0,                  # desconto default
        )

    def test_parse_xml_sem_cfop_usa_default_0000(self):
        xml = f"""
        <NFe>
            <infNFe Id="NFe{VALID_KEY}">
                <ide><dhEmi>2026-11-17T10:00:00-03:00</dhEmi></ide>
                <emit><CNPJ>12345678000199</CNPJ></emit>
                <total><ICMSTot><vProd>10.00</vProd><vNF>10.00</vNF></ICMSTot></total>
            </infNFe>
        </NFe>
        """.encode("utf-8")

        batch = []
        XmlParser.parse_xml(xml, batch)

        assert len(batch) == 1
        assert batch[0][1] == "0000"

    @pytest.mark.parametrize(
        "xml_invalido",
        [
            b"nao e um xml",
            b"<procEventoNFe><infEvento><tpEvento>110111</tpEvento></infEvento></procEventoNFe>",  # Sem <ide> e <total>
            f'<NFe><infNFe Id="NFe123"><ide><dhEmi>2026-11-17</dhEmi></ide><total></total></infNFe></NFe>'.encode(),  # Chave inválida
            f'<NFe><infNFe Id="NFe{VALID_KEY}"><ide></ide><total></total></infNFe></NFe>'.encode(),  # Sem data de emissão
            f'<NFe><infNFe Id="NFe{VALID_KEY}"><ide><dhEmi>2026-11-17</dhEmi></ide></infNFe></NFe>'.encode(),  # Sem <total>
        ],
    )
    def test_parse_xml_descarta_silenciosamente_xmls_invalidos_ou_eventos(self, xml_invalido):
        batch = []
        XmlParser.parse_xml(xml_invalido, batch)
        assert batch == []