# FiQA RAG Web Interface

A chat interface built with **Streamlit** for the FiQA financial question-answering API. It sends questions to the backend, allows the user to select a prompt catalog, shows answers with the retrieved sources and keeps each conversation isolated by `task_id` and prompt version.

All RAG logic — classification, retrieval, generation, verification and memory — runs in the backend. The interface renders the conversation, manages the selected prompt version and communicates with the REST API.

## Module Structure

The interface is split by responsibility:

*   **`app.py`**: Orchestrates the page. Creates the session state, checks whether the API is online, loads the available prompt versions, manages version changes, renders the components and sends questions to the API.
*   **`components.py`**: Renders the visual blocks: top bar, brand, `task_id`, online status, prompt version selector, "Nova Conversa" button, welcome section, suggestion chips and chat history.
*   **`api_client.py`**: Contains `FinancialApiClient`, the only module that communicates with the backend. It checks the API status, obtains the available prompt versions and sends questions.
*   **`config.py`**: Defines the API address (`API_BASE_URL`), page title and icon.
*   **`styles.py`**: Defines the dark theme CSS and the assistant avatar.

## Session State

Streamlit reruns the complete script on every interaction, so the interface state is stored in `st.session_state`.

The principal state fields are:

| Field | Purpose |
| :-- | :-- |
| `task_id` | UUID that identifies the current conversation |
| `messages` | Questions, answers and sources rendered in the chat |
| `selected_query` | Question selected through a suggestion button |
| `prompt_version` | Prompt catalog used by the current conversation |
| `prompt_version_selector` | Value currently selected by the Streamlit component |
| `available_prompt_versions` | Versions returned by the backend |
| `default_prompt_version` | Default version returned by the backend |

### Conversation Isolation

Every question sends both `task_id` and `prompt_version` to the API. The backend stores memory using the combination of those values, preventing conversations generated with different prompt catalogs from sharing context.

### Changing the Prompt Version

Changing the selector:

1. updates `prompt_version`;
2. creates a new `task_id`;
3. clears the messages shown in the interface;
4. clears any selected suggestion;
5. starts a new conversation with the selected catalog.

Starting a new conversation prevents previous answers produced by another prompt version from influencing the new version.

### New Conversation

The **Nova Conversa** button:

1. creates a new `task_id`;
2. clears messages and suggestions;
3. preserves the selected prompt version.

This allows the user to start another independent conversation without having to select the catalog again.

Reloading the browser page can create a new Streamlit session and, consequently, a new conversation.

## Communication with the API

### API Availability

`check_health()` requests:

```text
GET /api/docs
```

A successful response marks the API as online. The prompt versions are requested only when the API is available.

### Available Prompt Versions

`get_prompt_versions()` requests:

```text
GET /api/v1/financial/prompt-versions
```

Expected response:

```json
{
  "default": "v4.0.0__verified",
  "versions": [
    "v1.0.0__baseline",
    "v2.0.0__zero_shot",
    "v2.1.0__few_shot",
    "v3.0.0__decomposed",
    "v4.0.0__verified"
  ]
}
```

The interface uses `versions` as the selector options and uses `default` when no valid version is currently selected.

If the request fails after versions have already been loaded, the interface keeps the versions stored in the session. If no version has ever been loaded, the selector is replaced by a disabled field indicating that the API default will be used.

### Sending a Question

`ask_analyst()` requests:

```text
POST /api/v1/financial/ask
```

Request:

```json
{
  "query": "How does inflation affect corporate bond yields?",
  "task_id": "3f2c9a1e-...",
  "search_limit": 5,
  "prompt_version": "v4.0.0__verified"
}
```

The selected `prompt_version` is included whenever one is available. If it is omitted, the backend uses its configured default.

Response:

```json
{
  "query": "How does inflation affect corporate bond yields?",
  "task_id": "3f2c9a1e-...",
  "prompt_version": "v4.0.0__verified",
  "answer": "... [Source 1]\n\nSources: [Source 1]",
  "sources": [
    {
      "doc_id": "18850",
      "content": "..."
    }
  ],
  "classification": {
    "in_domain": true,
    "category": "INVESTING",
    "confidence": "HIGH",
    "contains_instructions": false,
    "reason": "..."
  },
  "verification": {
    "verdict": "SUPPORTED",
    "follows_embedded_instructions": false,
    "unsupported_claims": [],
    "reason": "..."
  },
  "abstention_reason": null,
  "configuration": {
    "prompt_version": "v4.0.0__verified",
    "fixtures_version": "v1.0.0__indirect_injection",
    "include_fixtures": false,
    "model_name": "qwen/qwen3.8-27b",
    "temperature": 0.0
  }
}
```

The interface uses:

*   **`answer`**: rendered as the assistant message;
*   **`sources`**: rendered in the "Fontes Consultadas" expander;
*   **`prompt_version`**: stored with the assistant message for traceability.

The response also contains `classification`, `verification`, `abstention_reason` and `configuration`. These fields are not displayed by the interface, but are available to evaluation and API clients.

The backend returns no sources when it abstains, so the sources expander is hidden in those cases.

## Prompt Version Selector

The selector is rendered in the top bar with the label:

```text
Versão do catálogo de prompts
```

Its options come directly from the backend. No prompt version is hardcoded in the interface.

Selecting another version does not restart the API and does not rebuild the FAISS index. The backend already has all prompt catalogs loaded and applies the selected catalog to the request.

The version selector and the online status are independent:

* when the API is online and versions are available, the selector is enabled;
* when the API is unavailable and no versions are cached, a disabled fallback field is shown;
* when a temporary request failure occurs after versions were loaded, the cached list remains available in the session.

## Answers and Sources

The answer can be:

* a grounded answer with inline `[Source N]` citations;
* the configured insufficient-evidence message;
* an out-of-domain message;
* an error returned by the API client.

Accepted answers can include sources. Each source is displayed with:

* its order in the retrieved results;
* the FiQA document ID;
* the retrieved chunk text.

Abstentions do not return sources.

## Timeouts and Response Time

The interface uses:

| Operation | Timeout |
| :-- | --: |
| API availability check | 2 seconds |
| Prompt version request | 5 seconds |
| Financial question | 60 seconds |

Versions containing classification and verification can make up to three LLM calls for one question. They can therefore take longer than versions containing only generation.

## Configuration

| Variable | Purpose | Default |
| :-- | :-- | :-- |
| `API_BASE_URL` | Address of the FastAPI backend | `http://localhost:8000` |

Inside Docker Compose, the interface must reach the API using the service name:

```text
API_BASE_URL=http://fiqa-rag-api:8000
```

For local execution without Docker, use:

```text
API_BASE_URL=http://localhost:8000
```

## Running

### With Docker Compose

From the project root:

```bash
docker compose up --build -d
docker compose logs -f fiqa-rag-api
```

The interface is available at:

```text
http://localhost:8501
```

Wait until the API log reports that database seeding has completed. The online status turns green after the API starts accepting requests.

### Locally

Start the API first, following `fiqa-rag-api/README.md`.

Then, from the `fiqa-rag-ui/` directory:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The interface is available at:

```text
http://localhost:8501
```

## Troubleshooting

### Status Shows Offline

Possible causes:

* the API is still loading the knowledge base;
* the API failed to start;
* `API_BASE_URL` points to the wrong address;
* the UI container is using `localhost` instead of the API service name.

Inside Docker, `localhost` refers to the interface container itself, not to the API.

### Prompt Selector Is Disabled

The API is unavailable or the request to `/api/v1/financial/prompt-versions` failed before any version was stored in the session.

Check:

```text
http://localhost:8000/api/v1/financial/prompt-versions
```

### Communication Failure

The request could not reach the API. Check the backend logs:

```bash
docker compose logs fiqa-rag-api
```

### API Error 422

The selected prompt version is not recognized by the API. Reload the interface so that it obtains the current list of versions.

### API Error 500

The API received the request but failed during processing. Review the backend traceback:

```bash
docker compose logs fiqa-rag-api
```

### Long Response Time

The selected version may execute classification, generation and verification. Also verify whether the Groq API is responding normally and whether the configured timeout is sufficient.