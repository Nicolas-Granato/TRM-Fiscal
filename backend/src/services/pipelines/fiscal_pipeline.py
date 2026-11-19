import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Callable, Optional

from backend.src.extractors.xml_parser import XmlParser

from backend.src.database.scripts.insert_xml_query import INSERT_XML
from backend.src.database.scripts.cancel_xml_query import CANCEL_XML


class FiscalPipeline:
    CANCEL_EVENTS = {"canc", "-can", "_can"}
    CANCEL_EVENT_CODES = {"110111", "110112"}

    def __init__(
        self,
        zip_file: bytes,
        zip_file_2: Optional[bytes] = None,
        zip_file_3: Optional[bytes] = None,
    ):
        self.zip_file = zip_file
        self.zip_file_2 = zip_file_2
        self.zip_file_3 = zip_file_3

        self._xml_batch: list[tuple] = []
        self._event_canc: list[tuple] = []

        self._company_name: Optional[str] = None
        self._cnpj: Optional[str] = None

    @classmethod
    def _extract_cancel_event_key(cls, xml_bytes: bytes) -> Optional[str]:
        try:
            root = ET.fromstring(xml_bytes)
        except (ET.ParseError, ValueError, TypeError):
            return None

        tp_evento = XmlParser.get_tag_text(root, "tpEvento")
        if tp_evento in cls.CANCEL_EVENT_CODES:
            ch_nfe = XmlParser.get_tag_text(root, "chNFe")
            if len(ch_nfe) == 44 and ch_nfe.isdigit():
                return ch_nfe

        for tag in ("cancNFe", "retCancNFe", "infCanc"):
            if XmlParser._find_node(root, tag) is not None:
                ch_nfe = XmlParser.get_tag_text(root, "chNFe")
                if len(ch_nfe) == 44 and ch_nfe.isdigit():
                    return ch_nfe

        return None

    def _process_zip_files(self, zip_file: bytes) -> None:
        if not zip_file:
            return

        with zipfile.ZipFile(io.BytesIO(zip_file)) as zf:
            for file_name in zf.namelist():
                if file_name.endswith("/"):
                    continue

                file_name_lower = file_name.lower()

                if file_name_lower.endswith(".zip"):
                    with zf.open(file_name) as nested_zip:
                        self._process_zip_files(nested_zip.read())
                    continue

                if any(event in file_name_lower for event in self.CANCEL_EVENTS):
                    chNFe = re.findall(r"\d{44}", file_name_lower)
                    if chNFe:
                        self._event_canc.append((chNFe[0],))
                        continue

                if file_name_lower.endswith(".xml"):
                    with zf.open(file_name) as xml_file:
                        xml_bytes = xml_file.read()

                        cancel_key = self._extract_cancel_event_key(xml_bytes)
                        if cancel_key:
                            self._event_canc.append((cancel_key,))
                            continue

                        if not self._cnpj or not self._company_name:
                            name, doc = XmlParser.get_company_info(xml_bytes, file_name)
                            if doc:
                                self._company_name = name
                                self._cnpj = doc

                        XmlParser.parse_xml(xml_bytes, self._xml_batch)

                        nfe_canceled_key = XmlParser.extract_canceled_key_from_nfe(xml_bytes)
                        if nfe_canceled_key:
                            self._event_canc.append((nfe_canceled_key,))

    def _process_xmls(self) -> None:
        self._process_zip_files(self.zip_file)

        if self.zip_file_2:
            self._process_zip_files(self.zip_file_2)

        if self.zip_file_3:
            self._process_zip_files(self.zip_file_3)

    @property
    def company_name(self) -> Optional[str]:
        return self._company_name

    @property
    def company_cnpj(self) -> Optional[str]:
        return self._cnpj

    def run_pipeline(self, executemany_sql: Callable) -> None:
        self._process_xmls()

        if len(self._xml_batch):
            dedup_xmls = list({row[0]: row for row in self._xml_batch}.values())
            executemany_sql(
                INSERT_XML,
                dedup_xmls,
            )

        if len(self._event_canc):
            unique_cancels = list(dict.fromkeys(self._event_canc))
            executemany_sql(
                CANCEL_XML,
                unique_cancels,
            )

        self._xml_batch.clear()
        self._event_canc.clear()