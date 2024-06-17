from langchain.document_loaders.base import BaseBlobParser
from langchain.docstore.document import Document

from img2table.ocr import TesseractOCR
from img2table.document import PDF

from io import BytesIO
import pytesseract


class new_pdf_parser(BaseBlobParser):

    def lazy_parse(self, blob):
        blob_bytes = blob.data
        blob_to_read = BytesIO(blob_bytes)

        ocr = TesseractOCR(n_threads=2, lang="ita")
        pdf = PDF(blob_to_read, detect_rotation=True, pdf_text_extraction=False)

        extracted_tables = list(
            pdf.extract_tables(
                ocr=ocr, implicit_rows=True, borderless_tables=True, min_confidence=50
            ).values()
        )

        total_tables = []

        for table_group in extracted_tables:
            for table in table_group:
                table_text = table.html
                if table.title:
                    table_text = table_text.replace(
                        "<table>", f"<table title={table.title}>"
                    )

                total_tables.append(table_text)

        parsed_text = extract_text_from_blob(blob_to_read)

        yield Document(page_content=parsed_text, metadata={"tables": total_tables})


def extract_text_from_blob(blob : BytesIO) -> str:
    pdf = PDF(blob, 
        detect_rotation=True,
        pdf_text_extraction=True)

    pages = pdf.images
    text_data = ""
    for page in pages:
        text = pytesseract.image_to_string(page)
        text_data += text + "\n"

    return text_data