import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


class XmlParser:
    ACCESS_KEY_LENGTH = 44
    CANCELED_CSTAT_CODES = {"101", "135", "151"}
    company_name: Optional[str] = None
    company_cnpj: Optional[str] = None

    @staticmethod
    def _find_node(
        parent: ET.Element,
        tag_name: str,
    ) -> Optional[ET.Element]:
        for elem in parent.iter():
            if elem.tag.endswith(tag_name):
                return elem
        return None

    @staticmethod
    def get_tag_text(
        parent: Optional[ET.Element],
        tag_name: str,
        default: str = "",
    ) -> str:
        if parent is None:
            return default

        for elem in parent.iter():
            if elem.tag.endswith(tag_name) and elem.text:
                return elem.text.strip()

        return default

    @classmethod
    def _extract_access_key(cls, root: ET.Element) -> str:
        key = cls.get_tag_text(root, "chNFe")

        if len(key) == cls.ACCESS_KEY_LENGTH and key.isdigit():
            return key

        for elem in root.iter():
            if elem.tag.endswith("infNFe"):
                key = elem.attrib.get("Id", "").replace("NFe", "").strip()
                if len(key) == cls.ACCESS_KEY_LENGTH and key.isdigit():
                    return key

        return ""

    @classmethod
    def extract_canceled_key_from_nfe(cls, xml_bytes: bytes) -> Optional[str]:
        """Retorna a chNF se o próprio XML da NF-e/NFC-e estiver com cStat de cancelamento (101, 135, 151)."""
        try:
            root = ET.fromstring(xml_bytes)
        except (ET.ParseError, ValueError, TypeError):
            return None

        prot_node = cls._find_node(root, "infProt")
        if prot_node is not None:
            cstat = cls.get_tag_text(prot_node, "cStat")
            if cstat in cls.CANCELED_CSTAT_CODES:
                key = cls._extract_access_key(root)
                if len(key) == cls.ACCESS_KEY_LENGTH and key.isdigit():
                    return key

        return None

    @staticmethod
    def _to_cents(value: str) -> int:
        try:
            return int(round(float(value.replace(",", ".")) * 100))
        except (ValueError, AttributeError):
            return 0

    @staticmethod
    def _format_date(date_str: str) -> str:
        return re.sub(r"T.*", "", date_str)

    @classmethod
    def get_company_info(
        cls,
        xml_bytes: bytes | ET.Element,
        zip_filepath: str,
    ) -> tuple[Optional[str], Optional[str]]:
        try:
            root = (
                xml_bytes
                if isinstance(xml_bytes, ET.Element)
                else ET.fromstring(xml_bytes)
            )
        except (ET.ParseError, ValueError, TypeError):
            return None, None

        infNFe_node = cls._find_node(root, "infNFe")
        if infNFe_node is None:
            return None, None

        folders = "/".join(p.lower() for p in Path(zip_filepath).parts[:-1])

        if "nfe compra" in folders:
            target_tag = "dest"
        else:
            target_tag = "emit"

        target_node = cls._find_node(infNFe_node, target_tag)
        if target_node is None:
            return None, None

        company_name = cls.get_tag_text(target_node, "xNome") or None
        raw_doc = (
            cls.get_tag_text(target_node, "CNPJ")
            or cls.get_tag_text(target_node, "CPF")
            or ""
        )
        company_doc = re.sub(r"\D", "", raw_doc) or None

        return company_name, company_doc

    @classmethod
    def parse_xml(
        cls,
        xml_bytes: bytes,
        xmls_batch: list,
    ) -> None:
        try:
            root = ET.fromstring(xml_bytes)

            ide_node = cls._find_node(root, "ide")
            if ide_node is None:
                return

            total_node = cls._find_node(root, "total")
            if total_node is None:
                return

            chNF = cls._extract_access_key(root)
            if chNF == "":
                return

            cfop = cls.get_tag_text(root, "CFOP") or "0000"

            dEmi = cls.get_tag_text(ide_node, "dhEmi") or cls.get_tag_text(ide_node, "dEmi")
            if dEmi == "":
                return
            dEmi = cls._format_date(dEmi)

            emit_node = cls._find_node(root, "emit")
            dest_node = cls._find_node(root, "dest")

            cnpj_emit = re.sub(
                r"\D",
                "",
                cls.get_tag_text(emit_node, "CNPJ") or cls.get_tag_text(emit_node, "CPF"),
            )
            cnpj_dest = re.sub(
                r"\D",
                "",
                cls.get_tag_text(dest_node, "CNPJ") or cls.get_tag_text(dest_node, "CPF"),
            )

            vlrProd = cls._to_cents(cls.get_tag_text(total_node, "vProd", "0"))
            vNF = cls._to_cents(cls.get_tag_text(total_node, "vNF", "0"))
            bcICMS = cls._to_cents(cls.get_tag_text(total_node, "vBC", "0"))
            vlrICMS = cls._to_cents(cls.get_tag_text(total_node, "vICMS", "0"))
            bcST = cls._to_cents(cls.get_tag_text(total_node, "vBCST", "0"))
            vlrST = cls._to_cents(cls.get_tag_text(total_node, "vST", "0"))
            vlrIPI = cls._to_cents(cls.get_tag_text(total_node, "vIPI", "0"))
            outras = cls._to_cents(cls.get_tag_text(total_node, "vOutro", "0"))
            desconto = cls._to_cents(cls.get_tag_text(total_node, "vDesc", "0"))

            xmls_batch.append(
                (
                    chNF,
                    cfop,
                    dEmi,
                    cnpj_emit,
                    cnpj_dest,
                    vlrProd,
                    vNF,
                    bcICMS,
                    vlrICMS,
                    bcST,
                    vlrST,
                    vlrIPI,
                    outras,
                    desconto,
                )
            )
        except (ET.ParseError, ValueError, TypeError, AttributeError):
            return