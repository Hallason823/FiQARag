# FiQA RAG Web Interface

A chat interface built with **Streamlit** for the FiQA financial question-answering API. It sends questions to the backend, shows the answers with the retrieved sources and keeps each conversation isolated by a `task_id`. All the RAG logic (classification, retrieval, generation, verification and memory) runs in the backend; the interface only renders the conversation and calls the REST API.

## Module Structure

The interface is split by responsibility:

*   **`app.py`**: Orchestrates the page. Creates the session state (`task_id`, messages and the selected suggestion), checks whether the API is online, renders the components and sends the question to the API.
*   **`components.py`**: Renders the visual blocks: the top bar (brand, `task_id`, online status and the "Nova Conversa" button), the welcome section, the suggestion chips and the chat history with the sources of each answer.
*   **`api_client.py`**: `FinancialApiClient`, the only module that talks to the backend. `check_health()` calls `GET /api/docs` to show the online status, and `ask_analyst()` calls `POST /api/v1/financial/ask`. Network and HTTP errors are returned as messages instead of breaking the page.
*   **`config.py`**: API address (`API_BASE_URL`), page title and icon.
*   **`styles.py`**: Dark theme CSS and the assistant avatar.

## Conversation and Task Isolation

Streamlit reruns the whole script on every interaction, so the conversation lives in `st.session_state`:

*   **`task_id`**: A UUID created when the session starts. It is sent with every question, and the backend uses it to keep the history of that conversation.
*   **`messages`**: The questions and answers shown on the screen, with the sources of each answer.
*   **"Nova Conversa"**: Creates a new `task_id` and clears the screen. The backend then starts a new history for the new task.

Reloading the page also starts a new session and, therefore, a new `task_id`.

## Communication with the API

Request sent by `ask_analyst()`:

```json
{"query": "How does inflation affect corporate bond yields?", "task_id": "3f2c9a1e-...", "search_limit": 5}
```

The interface uses two fields of the response:

*   **`answer`**: Shown as the assistant message. It can be a grounded answer with `[Source N]` citations, the abstention message ("I could not find this information in the consulted database.") or the out-of-domain message.
*   **`sources`**: Shown in the "Fontes Consultadas" expander, with the FiQA document ID and the retrieved chunk. The backend returns no sources when it abstains, so the expander is hidden in those cases.

The response also contains `classification`, `verification` and `abstention_reason`. The interface does not display them yet; they are used by the evaluation runs.

Requests have a 60-second timeout. On the API version with classifier and verifier, each question can make up to three LLM calls, so answers take longer than a single generation.

## Configuration

| Variable | Purpose | Default |
| :-- | :-- | :-- |
| `API_BASE_URL` | Address of the FastAPI backend | `http://localhost:8000` |

Inside Docker Compose, the interface must reach the API by its service name, so the project `.env` sets `API_BASE_URL=http://fiqa-rag-api:8000`. For a local run without Docker, keep the default.

## Running

### With Docker Compose (from the project root)

```bash
docker compose up --build -d fiqa-rag-ui
```

The interface is available at `http://localhost:8501`. The online status turns green when the API finishes loading the knowledge base.

### Locally

Start the API first (see `fiqa-rag-api/README.md`), then:

```bash
cd fiqa-rag-ui
pip install -r requirements.txt
streamlit run app.py
```

## Troubleshooting

*   **Status shows "Offline"**: The API is still loading the knowledge base, it failed to start, or `API_BASE_URL` points to the wrong address. Inside Docker, `localhost` refers to the interface container itself, not to the API.
*   **"Falha de comunicacao com o servidor"**: The request could not reach the API. Check `docker compose logs fiqa-rag-api`.
*   **"Erro na API (500)"**: The API received the question but failed while processing it. The traceback is in the API logs.
