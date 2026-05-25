def open(*args, **kwargs):
    raise RuntimeError(
        "PyMuPDF nao esta instalado neste ambiente. Configure pymupdf no deploy para ler PDFs."
    )
