import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


class XmlParser:
    ACCESS_KEY_LENGTH = 44

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

    @staticmethod
    def _to_cents(value: str) -> int:
        try:
            return int(round(float(value.replace(",", ".")) * 100))
        except (ValueError, AttributeError):
            return 0

    @staticmethod
    def _format_date(date_str: str) -> str:
        date = re.sub(r"T.*", "", date_str)
        return date

    @staticmethod
    def get_company_info(
        xml_bytes: bytes,
        zip_filepath: str,
    ) -> tuple[Optional[str], Optional[str]]:
        try:
            root = ET.fromstring(xml_bytes)
        except (ET.ParseError, ValueError, TypeError):
            return None, None

        infNFe_node = XmlParser._find_node(root, "infNFe")
        if infNFe_node is None:
            return None, None

        folders = "/".join(p.lower() for p in Path(zip_filepath).parts[:-1])

        if "nfce" in folders or "nfe venda" in folders or "nf venda" in folders:
            target_tag = "emit"
        elif "nfe compra" in folders:
            target_tag = "dest"
        else:
            return None, None

        target_node = XmlParser._find_node(infNFe_node, target_tag)
        if target_node is None:
            return None, None

        company_name = XmlParser.get_tag_text(target_node, "xNome") or None
        company_doc = (
            XmlParser.get_tag_text(target_node, "CNPJ")
            or XmlParser.get_tag_text(target_node, "CPF")
            or None
        )

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

            cfop = cls.get_tag_text(ide_node, "CFOP")
            if cfop == "":
                return

            vlrProd = cls.get_tag_text(total_node, "vProd")
            if vlrProd == "":
                return
            vlrProd = cls._to_cents(vlrProd)

            dEmi = cls.get_tag_text(ide_node, "dhEmi")
            if dEmi == "":
                return
            dEmi = cls._format_date(dEmi)

            bcICMS = cls.get_tag_text(total_node, "vBC")
            if bcICMS == "":
                return
            bcICMS = cls._to_cents(bcICMS)

            vlrICMS = cls.get_tag_text(total_node, "vICMS")
            if vlrICMS == "":
                return
            vlrICMS = cls._to_cents(vlrICMS)

            bcST = cls.get_tag_text(total_node, "vBCST")
            if bcST == "":
                return
            bcST = cls._to_cents(bcST)

            vlrST = cls.get_tag_text(total_node, "vST")
            if vlrST == "":
                return
            vlrST = cls._to_cents(vlrST)

            vlrIPI = cls.get_tag_text(total_node, "vIPI")
            if vlrIPI == "":
                return
            vlrIPI = cls._to_cents(vlrIPI)

            outras = cls.get_tag_text(total_node, "vOutro")
            if outras == "":
                return
            outras = cls._to_cents(outras)

            desconto = cls.get_tag_text(total_node, "vDesc")
            if desconto == "":
                return
            desconto = cls._to_cents(desconto)

            xmls_batch.append(
                (
                    chNF,
                    cfop,
                    vlrProd,
                    dEmi,
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