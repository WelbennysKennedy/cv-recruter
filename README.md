# CV Recruter — Analisador de Currículos com IA

Compara currículos em PDF com uma vaga usando IA. Para cada candidato, o projeto gera um resumo, uma nota de 0 a 10 e um relatório crítico, e mostra tudo em um painel feito com Streamlit.

![Painel com a classificação dos candidatos por nota e a tabela de resultados](imagens/cv%20analise.png)

## Funcionalidades

- Leitura de currículos em PDF, em lote
- Resumo de cada currículo em Markdown
- Nota do candidato em relação à vaga
- Relatório com pontos de alinhamento, desalinhamento e atenção
- Gráfico e tabela com a classificação dos candidatos
- Comparação de candidatos lado a lado e download do PDF original
- Importação de currículos do Google Drive (opcional)

## O que instalar

Você só precisa instalar o [uv](https://docs.astral.sh/uv/), o gerenciador de pacotes do projeto.

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

O `uv sync` cuida do resto: baixa o Python 3.10, se necessário, e instala as dependências abaixo em um ambiente virtual `.venv`.

| Pacote | Para que serve |
|---|---|
| `streamlit`, `streamlit-aggrid`, `pandas` | Painel, tabela e gráfico |
| `langchain-groq` | Comunicação com a IA da Groq |
| `pymupdf` | Leitura dos PDFs |
| `tinydb` | Banco de dados local (`db.json`) |
| `pydantic` | Validação dos dados |
| `python-dotenv` | Leitura do arquivo `.env` |
| `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` | Google Drive (opcional) |

## Chave de API

O projeto precisa de uma chave da [Groq](https://console.groq.com/keys).

1. Crie a chave em https://console.groq.com/keys.
2. Crie o arquivo `.env` na raiz do projeto a partir do modelo:

   ```bash
   cp .env.example .env
   ```

3. Coloque a sua chave no `.env`:

   ```env
   GROQ_API_KEY=sua_chave_aqui
   ```

> **Nunca publique o arquivo `.env`.** Ele já está no `.gitignore`.

## Como rodar

Rode todos os comandos na raiz do projeto.

**1. Baixe o projeto e instale as dependências**

```bash
git clone https://github.com/WelbennysKennedy/cv-recruter.git
cd cv-recruter
uv sync
```

**2. Configure a chave de API**, como explicado na seção anterior.

**3. Crie a pasta `curriculos` e coloque nela os PDFs que serão analisados**

```bash
mkdir curriculos
```

**4. Crie a vaga** (rode só uma vez, pois cada execução cadastra a vaga de novo)

```bash
uv run python analyze/create_job.py
```

**5. Analise os currículos**

```bash
uv run python analyze/import_cv.py
```

**6. Abra o painel**

```bash
uv run python -m streamlit run analyze/app.py
```

Acesse http://localhost:8501 e selecione a vaga no topo da página.

## Usar outra vaga

1. Altere o nome e a descrição da vaga em `analyze/create_job.py`.
2. Use o mesmo nome na busca da vaga em `analyze/import_cv.py`.
3. Rode novamente os passos 4 e 5.

## Cuidados

- **O botão "Limpar Análise" apaga os PDFs da pasta `curriculos/`**, além das análises da vaga. Guarde uma cópia dos arquivos.
- **Rodar `import_cv.py` de novo duplica os candidatos**, porque o script analisa todos os PDFs da pasta a cada execução.
- **Os currículos são enviados para a API da Groq** durante a análise. Tenha autorização para processar esses dados.
- **As notas e os relatórios são gerados por IA** e podem variar ou conter erros. Use o resultado como apoio, não como decisão final.

## Como a nota é calculada

A IA avalia o currículo em relação à vaga usando estes critérios:

| Critério | Peso |
|---|---|
| Experiência | 30% |
| Habilidades técnicas | 25% |
| Pontos fortes | 15% |
| Educação | 10% |
| Idiomas | 10% |
| Pontos fracos | Desconto de até 10% |

## Google Drive (opcional)

Use estes passos apenas se quiser baixar os currículos de uma pasta do Google Drive.

1. Salve as credenciais OAuth2 do Google Cloud como `credentials.json` na raiz do projeto.
2. Gere o `token.json`:

   ```bash
   uv run python analyze/drive/authenticate.py
   ```

3. Em `analyze/drive/download_cv.py`, troque o valor de `folder_id` pelo ID da sua pasta.
4. Baixe os arquivos para `curriculos/`:

   ```bash
   uv run python analyze/drive/download_cv.py
   ```

## Testes

O teste faz uma chamada real à Groq, então precisa de uma chave válida.

```bash
uv run pytest tests/test_ai.py
```

O workflow `.github/workflows/run_test.yml` roda esse teste todo mês. Para usá-lo, crie o secret `GROQ_API_KEY` no ambiente `production` do repositório no GitHub.

## Estrutura do projeto

```text
analyze/
├── app.py          # Painel Streamlit
├── ai.py           # Prompts e chamadas à Groq
├── import_cv.py    # Análise dos currículos
├── create_job.py   # Cadastro da vaga
├── database.py     # Acesso ao banco TinyDB
├── helper.py       # Leitura de PDF e extração dos dados
├── models/         # Modelos de dados
└── drive/          # Integração com o Google Drive
tests/              # Teste da integração com a Groq
imagens/            # Imagem deste README
```

## Contato

Para contato, acesse [wekdev.com](https://wekdev.com).
