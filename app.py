import fitz
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from analyser.service.llama_client import LlamaClient


app = FastAPI(
    title="CV Recruter API",
    version="0.1.0",
    description="FastAPI entrypoint for CV analysis deployments.",
)


def _extract_pdf_text(file_content: bytes) -> str:
    try:
        with fitz.open(stream=file_content, filetype="pdf") as document:
            return "\n".join(page.get_text() for page in document).strip()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Nao foi possivel ler o PDF.") from exc


@app.get("/")
def root():
    return {
        "service": "CV Recruter API",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze-cv")
async def analyze_cv(
    cv_file: UploadFile = File(...),
    job_description: str = Form(...),
):
    if not cv_file.filename or not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um curriculo em PDF.")

    file_content = await cv_file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="O PDF enviado esta vazio.")

    cv_text = _extract_pdf_text(file_content)
    if not cv_text:
        raise HTTPException(status_code=400, detail="O PDF nao contem texto extraivel.")

    try:
        ai = LlamaClient()
        summary = ai.resume_cv(cv_text)
        opinion = ai.generate_opnion(cv_text, job_description)
        score = ai.generate_score(cv_text, job_description)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Falha ao analisar o curriculo.") from exc

    return {
        "filename": cv_file.filename,
        "extracted_characters": len(cv_text),
        "summary": summary,
        "opinion": opinion,
        "score": score,
    }
