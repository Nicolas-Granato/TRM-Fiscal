import io
import re
import zipfile
import duckdb
from typing import Callable, Optional

from backend.src.extractors.xml_parser import XmlParser
from backend.src.database.session_manager.session_manager import DuckDBSession

from backend.src.database.scripts.insert_xml_query import INSERT_XML
from backend.src.database.scripts.cancel_xml_query import CANCEL_XML

class FiscalPipeline:
    
    CANCEL_EVENTS = {"canc"}

    def __init__(
            self, 
            zip_file: bytes, 
            zip_file_2: Optional[bytes] = None,
            zip_file_3: Optional[bytes] = None
            ):
        self.zip_file = zip_file
        self.zip_file_2 = zip_file_2
        self.zip_file_3 = zip_file_3

        self._xml_batch: list[tuple] = []
        self._event_canc: list[tuple] = []

        self._company_name: Optional[str] = None
        self._cnpj: Optional[str] = None

    def _process_zip_file(self, zip_file: bytes) -> None:
        if not zip_file:
            return
        
        with zipfile.ZipFile(io.BytesIO(zip_file)) as zf:
            for file_name in zf.namelist():
                file_name = file_name.lower()

                if any(event in file_name for event in self.CANCEL_EVENTS):
                    chNFe = re.findall(r"\d{44}", file_name)
                    if chNFe:
                        self._event_canc.append((chNFe[0],))
                    continue

                if file_name.endswith(".xml"):
                    with zf.open(file_name) as xml_file:
                        xml_bytes = xml_file.read()
                        XmlParser.parse_xml(xml_bytes, self._xml_batch)

    def _process_xmls(self) -> None:
        self._process_zip_file(self.zip_file)

        if self.zip_file_2:
            self._process_zip_file(self.zip_file_2)

        if self.zip_file_3:
            self._process_zip_file(self.zip_file_3)

    def run_pipeline(self) -> None:
        self._process_xmls()

        with DuckDBSession() as session:
            if len(self._xml_batch):
                session.executemany_sql(
                    INSERT_XML,
                    self._xml_batch
                )

            if len(self._event_canc):
                session.executemany_sql(
                    CANCEL_XML,
                    self._event_canc
                )

        self._xml_batch.clear()
        self._event_canc.clear()
