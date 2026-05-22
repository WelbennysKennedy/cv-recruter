import fitz
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from analyser.service.llama_client import LlamaClient


INDEX_HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CV Recruter</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #14202b;
      --muted: #516272;
      --line: #d6dde4;
      --paper: #f6f8fa;
      --surface: #ffffff;
      --accent: #087f8c;
      --accent-ink: #ffffff;
      --focus: #f59e0b;
      --success: #146c43;
      --danger: #b42318;
    }
    * { box-sizing: border-box; letter-spacing: 0; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--paper);
      color: var(--ink);
      font: 16px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    header {
      border-bottom: 1px solid var(--line);
      background: var(--surface);
    }
    nav, main {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
    }
    nav {
      min-height: 68px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    .brand {
      margin: 0;
      font-size: 1.35rem;
      font-weight: 700;
    }
    .docs {
      color: var(--ink);
      text-decoration: none;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 13px;
      background: var(--surface);
    }
    main {
      display: grid;
      grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
      gap: 28px;
      align-items: start;
      padding: 42px 0 56px;
    }
    h1, h2 { margin: 0; }
    h1 {
      max-width: 680px;
      font-size: 3rem;
      line-height: 1.08;
    }
    h2 { font-size: 1.05rem; }
    p { margin: 0; }
    .intro {
      grid-column: 1 / -1;
      display: grid;
      gap: 12px;
    }
    .intro p {
      max-width: 720px;
      color: var(--muted);
    }
    form, .results {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    form {
      display: grid;
      gap: 16px;
      padding: 22px;
    }
    label {
      display: grid;
      gap: 8px;
      font-weight: 600;
    }
    input, textarea, button {
      font: inherit;
    }
    input[type="file"], textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--surface);
      color: var(--ink);
    }
    input[type="file"] { padding: 11px; }
    textarea {
      min-height: 260px;
      resize: vertical;
      padding: 12px;
    }
    input:focus, textarea:focus, button:focus, a:focus {
      outline: 3px solid color-mix(in srgb, var(--focus) 55%, transparent);
      outline-offset: 2px;
    }
    button {
      min-height: 46px;
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: var(--accent-ink);
      font-weight: 700;
      cursor: pointer;
    }
    button[disabled] {
      cursor: wait;
      opacity: .72;
    }
    .results {
      min-height: 520px;
      display: grid;
      gap: 0;
      overflow: hidden;
    }
    .result-head {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 20px 22px;
      border-bottom: 1px solid var(--line);
    }
    .score {
      min-width: 78px;
      padding: 8px 12px;
      border-radius: 6px;
      background: #e6f5ef;
      color: var(--success);
      text-align: center;
      font-weight: 700;
    }
    .status {
      padding: 22px;
      color: var(--muted);
    }
    .status.error { color: var(--danger); }
    .output {
      display: grid;
      gap: 0;
    }
    .output section {
      display: grid;
      gap: 10px;
      padding: 20px 22px;
      border-bottom: 1px solid var(--line);
    }
    .output section:last-child { border-bottom: 0; }
    pre {
      margin: 0;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      color: var(--ink);
      font: inherit;
    }
    @media (max-width: 820px) {
      nav, main { width: min(100% - 24px, 680px); }
      main {
        grid-template-columns: 1fr;
        padding-top: 30px;
      }
      h1 { font-size: 2rem; }
      textarea { min-height: 210px; }
      .results { min-height: 360px; }
    }
  </style>
</head>
<body>
  <header>
    <nav>
      <p class="brand">CV Recruter</p>
      <a class="docs" href="/docs">API docs</a>
    </nav>
  </header>
  <main>
    <section class="intro">
      <h1>Analise um curriculo contra uma vaga.</h1>
      <p>Envie um PDF com texto selecionavel e descreva a vaga para gerar resumo, avaliacao e pontuacao.</p>
    </section>
    <form id="analysis-form">
      <label>
        Curriculo PDF
        <input id="cv-file" name="cv_file" type="file" accept="application/pdf,.pdf" required>
      </label>
      <label>
        Descricao da vaga
        <textarea id="job-description" name="job_description" required placeholder="Cole atividades, requisitos e diferenciais da vaga."></textarea>
      </label>
      <button id="submit-button" type="submit">Analisar curriculo</button>
    </form>
    <section class="results" aria-live="polite">
      <div class="result-head">
        <h2>Resultado</h2>
        <p class="score" id="score">--</p>
      </div>
      <p class="status" id="status">A analise aparecera aqui.</p>
      <div class="output" id="output" hidden>
        <section>
          <h2>Resumo</h2>
          <pre id="summary"></pre>
        </section>
        <section>
          <h2>Avaliacao</h2>
          <pre id="opinion"></pre>
        </section>
      </div>
    </section>
  </main>
  <script>
    const form = document.querySelector("#analysis-form");
    const button = document.querySelector("#submit-button");
    const status = document.querySelector("#status");
    const output = document.querySelector("#output");
    const score = document.querySelector("#score");
    const summary = document.querySelector("#summary");
    const opinion = document.querySelector("#opinion");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      button.disabled = true;
      status.hidden = false;
      status.classList.remove("error");
      status.textContent = "Analisando o curriculo...";
      output.hidden = true;
      score.textContent = "--";

      try {
        const response = await fetch("/api/analyze-cv", {
          method: "POST",
          body: new FormData(form),
        });
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Nao foi possivel concluir a analise.");
        }

        score.textContent = Number.isFinite(data.score) ? data.score.toFixed(1) : String(data.score);
        summary.textContent = data.summary || "";
        opinion.textContent = data.opinion || "";
        status.textContent = `${data.filename} processado com ${data.extracted_characters} caracteres extraidos.`;
        output.hidden = false;
      } catch (error) {
        status.classList.add("error");
        status.textContent = error.message;
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


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


@app.get("/", response_class=HTMLResponse)
def root():
    return INDEX_HTML


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
