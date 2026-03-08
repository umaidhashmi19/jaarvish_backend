import tempfile
import os
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import (
    PDFReader,
    DocxReader,
    PandasCSVReader,
)


EXTENSION_READER_MAP = {
    ".pdf":  PDFReader(),
    ".docx": DocxReader(),
    ".csv":  PandasCSVReader(),
}


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Write bytes to a temp file, load with LlamaIndex, return raw text.
    Temp file is deleted immediately after reading.
    """
    ext = os.path.splitext(filename)[-1].lower()

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        file_extractor = {ext: EXTENSION_READER_MAP[ext]} if ext in EXTENSION_READER_MAP else {}
        reader = SimpleDirectoryReader(
            input_files=[tmp_path],
            file_extractor=file_extractor
        )
        documents = reader.load_data()
        return "\n\n".join([doc.text for doc in documents])
    finally:
        os.unlink(tmp_path)  # Always delete temp file