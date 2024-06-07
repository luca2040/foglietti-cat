from langchain.document_loaders.base import BaseBlobParser
from langchain.docstore.document import Document

from io import BytesIO
import tabula
from PyPDF2 import PdfReader


class new_pdf_parser(BaseBlobParser):

    def lazy_parse(self, blob):
        parsed_text, parsed_tables = parse_pdf(blob, "TABELLA")

        yield Document(page_content=parsed_text , metadata={"tables": parsed_tables})


def replace_text(text_to_replace):
    return str(text_to_replace).replace("\n", " ").replace("\r", " ").replace("\t", " ")


def parse_pdf(file_blob, table_name):

    blob_bytes = file_blob.data
    blob_to_read = BytesIO(blob_bytes)

    tables = tabula.read_pdf(blob_to_read, pages="all")

    tables_text = ["" for _ in range(len(tables))]

    for dataIndex, dataframe in enumerate(tables):
        tables_text[dataIndex] = table_name + "{\n"

        columns_parsed = dataframe.columns.to_numpy()

        data_parsed = dataframe.to_numpy()

        data_parsed = [
            [
                single_data if isinstance(single_data, str) else ""
                for single_data in element
            ]
            for element in data_parsed
        ]

        for indexText in columns_parsed:
            text_replaced = replace_text(indexText)
            tables_text[dataIndex] += f"({text_replaced})"
        tables_text[dataIndex] += "]\n"

        for row in data_parsed:
            tables_text[dataIndex] += "["
            for rowText in row:
                text_replaced = replace_text(rowText)
                tables_text[dataIndex] += f"({text_replaced})"
            tables_text[dataIndex] += "]\n"
        tables_text[dataIndex] += "}\n"

    reader = PdfReader(blob_to_read)

    all_text = ""

    for page in reader.pages:
        all_text += page.extract_text()

    # all_text
    # tables_text

    return all_text, tables_text
