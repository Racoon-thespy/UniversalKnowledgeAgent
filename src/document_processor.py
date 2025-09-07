import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List


class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(reader.pages):
                    text += f"\n--- Page {page_num + 1} ---\n"
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def process_document(self, file_path: str, filename: str) -> List[Document]:
        """Process document and return chunks"""
        text = self.extract_text_from_pdf(file_path)
        chunks = self.text_splitter.split_text(text)

        return [
            Document(
                page_content=chunk,
                metadata={
                    "filename": filename,
                    "chunk_id": i,
                    "source": file_path,
                },
            )
            for i, chunk in enumerate(chunks)
        ]
