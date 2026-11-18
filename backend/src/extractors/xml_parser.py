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
        return re.sub(r"T.*", "", date_str).strip()

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

        if "nfe compra" in folders or "compra" in folders:
            target_tag = "dest"
        else:
            target_tag = "emit"

        target_node = XmlParser._find_node(infNFe_node, target_tag)
        if target_node is None:
            return None, None

        company_name = XmlParser.get_tag_text(target_node, "xNome") or None
        raw_doc = (
            XmlParser.get_tag_text(target_node, "CNPJ")
            or XmlParser.get_tag_text(target_node, "CPF")
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

            prod_node = cls._find_node(root, "prod")
            cfop = cls.get_tag_text(prod_node, "CFOP") or cls.get_tag_text(root, "CFOP")
            if cfop == "":
                return

            vlrProd = cls._to_cents(cls.get_tag_text(total_node, "vProd", "0"))

            vNF_raw = cls.get_tag_text(total_node, "vNF")
            if vNF_raw == "":
                return
            vNF = cls._to_cents(vNF_raw)

            dEmi_raw = cls.get_tag_text(ide_node, "dhEmi") or cls.get_tag_text(ide_node, "dEmi")
            if dEmi_raw == "":
                return
            dEmi = cls._format_date(dEmi_raw)

            emit_node = cls._find_node(root, "emit")
            cnpjEmit = re.sub(
                r"\D",
                "",
                cls.get_tag_text(emit_node, "CNPJ") or cls.get_tag_text(emit_node, "CPF"),
            )
            if cnpjEmit == "":
                return

            dest_node = cls._find_node(root, "dest")
            cnpjDest = re.sub(
                r"\D",
                "",
                cls.get_tag_text(dest_node, "CNPJ") or cls.get_tag_text(dest_node, "CPF"),
            )
            if chNF[20:22] == "65" and cnpjDest == "":
                cnpjDest = "--Consumidor--"

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
                    cnpjEmit,
                    cnpjDest,
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
