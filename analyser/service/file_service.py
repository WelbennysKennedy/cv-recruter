import uuid
from pathlib import Path


def _load_fitz():
    try:
        import fitz
        return fitz
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyMuPDF nao esta instalado. Configure pymupdf no deploy para ler PDFs."
        ) from exc


class FileService:   
    def read(self, file_path):
        fitz = _load_fitz()
        content = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                content += page.get_text()
        return content
    
    def read_all(self, files):
        return [self.read(file) for file in files]

    def save_uploaded_files(self, uploaded_files, destination_folder):
        destination_path = Path(destination_folder)
        destination_path.mkdir(parents=True, exist_ok=True)
        
        saved_file_paths = []
        for uploaded_file in uploaded_files:
            file_path = destination_path / str(uuid.uuid4())
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_file_paths.append(file_path)
        
        return saved_file_paths
