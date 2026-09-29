# FiQA Agentic RAG API Backend

A financial question-answering backend built with **FastAPI** and orchestrated with **LangGraph**. The system ingests the **FiQA financial dataset** from Hugging Face, splits it into overlapping chunks with a sliding window processor, indexes them in a **FAISS** vector store, and answers questions through a chain of specialized prompts sent to the **Groq API**: question classification, answer generation and answer verification.

## Layered Software Architecture

The project follows the **Controller-Service-Repository** pattern and the **Single Responsibility Principle (SRP)**:

*   **`src/controllers/`**: HTTP entry points, request validation (Pydantic) and REST endpoint definitions.
*   **`src/services/`**: Business workflow, conditional routing and the LangGraph agent graph.
*   **`src/repositories/`**: Gateways to external resources: the FAISS index, the Hugging Face dataset and the Groq API, including the loading of the versioned prompt catalog.
*   **`src/processors/`**: Reusable utilities: logging mixin, text splitter, database seeder and the structured output (JSON) parser.
*   **`src/models/`**: Settings, the graph state contract and the Pydantic models that validate the classifier and verifier outputs.

## LangGraph Workflow Execution Pipeline

```text
START → classify ─┬─ out of domain → handle_out_of_domain → END
                  └─ in domain → retrieve ─┬─ low score → handle_abstention → END
                                           └─ score ok → build_context → generate
                                                  ├─ LLM abstained → END
                                                  └─ answer generated → verify
                                                         ├─ accepted → END
                                                         └─ rejected → handle_rejected_answer → END
```

1.  **`classify_question_node`**: Sends the question and the task history to the `classification` prompt. The JSON output is validated with `QuestionClassification`.
2.  **`evaluate_domain_routing`**: Routes out-of-domain questions (medium or high confidence) to a dedicated answer without retrieval or generation.
3.  **`retrieve_knowledge_node`**: Fetches the most similar chunks from the FAISS index.
4.  **`evaluate_evidence_routing`**: Abstains without calling the LLM when the best score is below `EVIDENCE_THRESHOLD_SCORE`.
5.  **`build_context_node`**: Formats each chunk with the `document_template` of the loaded prompt version.
6.  **`generate_answer_node`**: Sends the history, documents and question, each in its own delimited region, to the `generation` prompt. Flags the answer as `INSUFFICIENT_EVIDENCE` when the LLM abstains.
7.  **`verify_answer_node`**: Sends the documents, question and answer to the `verification` prompt. The JSON output is validated with `AnswerVerification`.
8.  **`evaluate_verification_routing`**: Replaces answers that are `NOT_SUPPORTED` or that followed instructions embedded in the documents with the abstention message.

The classification and verification nodes only run when the loaded prompt version contains the corresponding prompt, so the same code runs every prompt version.

## Versioned Prompt Catalog

Prompts live in `config/prompts/`, one JSON file per version, selected with `PROMPT_VERSION`. Each file maps a responsibility (`classification`, `generation`, `verification`) to its `system` prompt, `user_template` and optional templates:

| Version | Prompts | Change from the previous version |
| :-- | :-- | :-- |
| `v1.0.0__baseline` | `generation` | Original prompt, kept as the comparison baseline |
| `v2.0.0__zero_shot` | `generation` | Role, task, numbered rules, security section, abstention criteria, output format and XML delimiters |
| `v2.1.0__few_shot` | `generation` | Same as v2.0.0 plus four examples built from real FiQA excerpts |
| `v3.0.0__decomposed` | `classification`, `generation` | Adds the question classifier |
| `v4.0.0__verified` | `classification`, `generation`, `verification` | Adds the answer verifier |

Versioning rule: **MAJOR** for structural changes that require code (new regions or prompts), **MINOR** for new rules or examples, **PATCH** for wording fixes.

## Centralized Configuration

*   **`ApplicationSettings`**: Centralizes constants (abstention and out-of-domain messages, dataset names, embedding model) and environment-driven properties.
*   **`.env`**: Chunk size, overlap, top_k, temperature, token limits, evidence threshold and prompt version can be changed without modifying code.

## API Contract

`POST /api/v1/financial/ask`

Request:

```json
{"query": "How does inflation affect corporate bond yields?", "task_id": "a1b2c3d4", "search_limit": 5}
```

Response:

```json
{
  "query": "How does inflation affect corporate bond yields?",
  "task_id": "a1b2c3d4",
  "answer": "... [Source 1]\n\nSources: [Source 1]",
  "sources": [{"doc_id": "18850", "content": "..."}],
  "classification": {"in_domain": true, "category": "INVESTING", "confidence": "HIGH", "contains_instructions": false, "reason": "..."},
  "verification": {"verdict": "SUPPORTED", "follows_embedded_instructions": false, "unsupported_claims": [], "reason": "..."},
  "abstention_reason": null
}
```

`abstention_reason` is one of `OUT_OF_DOMAIN`, `LOW_RETRIEVAL_SCORE`, `INSUFFICIENT_EVIDENCE`, `UNSUPPORTED_ANSWER`, `EMBEDDED_INSTRUCTIONS_FOLLOWED`, or `null` when the question was answered. Abstentions return no sources and are not saved to the task history. `classification` and `verification` are `null` when the prompt version has no classifier or verifier.

Other endpoints:

*   `GET /api/v1/financial/tasks/{task_id}/history`: Returns the stored exchanges of a task.
*   `DELETE /api/v1/financial/tasks/{task_id}`: Clears the memory of a task.

## Getting Started

### 1. Configure the Environment Variables

Create a `.env` file in the project root:

```text
GROQ_API_KEY=<secret_groq_api_key>
GROQ_MODEL_NAME=qwen/qwen3.8-27b
MODEL_TEMPERATURE=0.0
MAX_TOKENS=300
CLASSIFICATION_MAX_TOKENS=150
VERIFICATION_MAX_TOKENS=200
REASONING_EFFORT=none
DEFAULT_CHUNK_SIZE=55
DEFAULT_CHUNK_OVERLAP=12
DEFAULT_TOP_K=3
DEFAULT_SEARCH_LIMIT=3
EVIDENCE_THRESHOLD_SCORE=0.5
MAX_HISTORY_EXCHANGES=4
PROMPT_VERSION=v4.0.0__verified
INCLUDE_FIXTURES=true
FIXTURES_VERSION=v1.0.0__indirect_injection
```

### 2. Local Setup and Execution

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the API from the `fiqa-rag-api/` directory, so the relative path to `config/prompts/` resolves correctly:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The database seeding (download, chunking and embedding) runs before the server starts accepting requests.

### 3. Containerized Setup via Docker

From the project root:

```bash
docker compose up --build -d fiqa-rag-api
docker compose logs -f fiqa-rag-api
```

The API is ready when the log prints `Database seeding execution completed successfully`. After changing `PROMPT_VERSION` or any source file, rebuild and recreate the container:

```bash
docker compose up -d --force-recreate --build fiqa-rag-api
```

### 4. Test the REST Interface

*   **Swagger documentation**: `http://localhost:8000/api/docs`
*   **Question endpoint**: `POST http://localhost:8000/api/v1/financial/ask`
