"""
document_loader.py
Enterprise AI Knowledge Assistant

Supports:
- PDF
- DOCX
- TXT
"""

from pathlib import Path

from pypdf import PdfReader
from docx import Document

from config import SUPPORTED_FILES


class DocumentLoader:

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Load PDF
    # ---------------------------------------------------------

    def load_pdf(self, filepath):

        text = ""

        reader = PdfReader(filepath)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text.strip()

    # ---------------------------------------------------------
    # Load DOCX
    # ---------------------------------------------------------

    def load_docx(self, filepath):

        doc = Document(filepath)

        text = "\n".join(

            para.text

            for para in doc.paragraphs

            if para.text.strip()

        )

        return text.strip()

    # ---------------------------------------------------------
    # Load TXT
    # ---------------------------------------------------------

    def load_txt(self, filepath):

        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            return f.read().strip()

    # ---------------------------------------------------------
    # Load Single Document
    # ---------------------------------------------------------

    def load_document(self, filepath):

        filepath = Path(filepath)

        extension = filepath.suffix.lower()

        if extension == ".pdf":
            return self.load_pdf(filepath)

        elif extension == ".docx":
            return self.load_docx(filepath)

        elif extension == ".txt":
            return self.load_txt(filepath)

        else:
            raise ValueError(
                f"Unsupported file: {extension}"
            )

    # ---------------------------------------------------------
    # Load Directory
    # ---------------------------------------------------------

    def load_directory(self, directory):

        directory = Path(directory)

        documents = []

        if not directory.exists():

            return documents

        for file in directory.iterdir():

            if (
                file.is_file()
                and file.suffix.lower() in SUPPORTED_FILES
            ):

                try:

                    text = self.load_document(file)

                    if not text.strip():
                        continue

                    documents.append(
                        {
                            "filename": file.name,
                            "filepath": str(file),
                            "text": text,
                            "characters": len(text)
                        }
                    )

                except Exception as e:

                    print(
                        f"❌ Failed to load {file.name}: {e}"
                    )

        return documents

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def stats(self, directory):

        docs = self.load_directory(directory)

        return {

            "documents": len(docs),

            "characters": sum(
                doc["characters"]
                for doc in docs
            )
        }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    from config import UPLOAD_DIR

    loader = DocumentLoader()

    docs = loader.load_directory(UPLOAD_DIR)

    print()

    print("Loaded Documents:", len(docs))

    print()

    for doc in docs:

        print(doc["filename"])

        print(doc["characters"], "characters")

        print("-" * 40)