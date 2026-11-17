import re
import xml.etree.ElementTree as ET
from typing import Optional


class XmlParser:
    ACCESS_KEY_LENGTH = 44
    OPERATION_TYPE_OUTGOING = "1"

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

    @classmethod
    def parse_xml(
        cls,
        xml_bytes: bytes,
        xmls_batch: list,
    ) -> None:
        try:
            xmls_batch.append(
                (
                )
            )

        except (ET.ParseError, ValueError, TypeError, AttributeError):
            return
