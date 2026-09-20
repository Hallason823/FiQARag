# FiQA Agentic RAG API Backend

An advanced, production-grade financial document analysis backend built with **FastAPI** and orchestrated using **LangGraph**. The system ingests the scientific **FiQA financial dataset** from Hugging Face, slices it into overlapping text chunks via a custom sliding window processor, indexes it into a high-performance semantic vector store utilizing **Meta's FAISS**, and dispatches contextual queries to the **Groq API (llm)** using an agentic workflow state engine.

## Layered Software Architecture

The project adheres strictly to the **Controller-Service-Repository** pattern and the **Single Responsibility Principle (SRP)**, completely decoupling business rules from external infrastructure gateways and APIs:

*   **`src/controllers/`**: Manages HTTP web entries, schema data validations (Pydantic), and REST endpoint definitions.
*   **`src/services/`**: Houses core business workflow logic, state transitions, conditional routing algorithms, and compiles the agent graph architecture via LangGraph.
*   **`src/repositories/`**: Gateway layer handling outbound data connection integrations, such as database storage execution (FAISS) and external text generation network APIs (Groq).
*   **`src/processors/`**: Reusable standalone infrastructure utilities, including dynamic cross-cutting log injectors and text chunk splitters.
*   **`src/models/`**: Centralized object models defining dynamic configuration settings and the agent runtime data storage contracts.

## LangGraph Workflow Execution Pipeline

Rather than executing a standard linear sequential query, this application abstracts the RAG pipeline into an isolated stateful graph execution runtime. Every phase operates inside an independent state node:

```text
                       +--> build_context_node --> generate_answer_node --> END
                       |
START --> retrieve --> decision (Score >= 0.50?)
                       |
                       +--> handle_abstention_node ------------------------> END
```

1.  **`retrieve_knowledge_node`**: Fetches semantic content vectors from the local FAISS memory cache.
2.  **`evaluate_evidence_routing`**: A conditional routing gate checking if the highest retrieval match satisfies the minimum threshold parameter (`0.50`).
3.  **`build_context_node` / `handle_abstention_node`**: Routes toward dynamic contextual string building if evidence exists, or fast-tracks directly to an explicit failure response, saving unnecessary API token costs.
4.  **`generate_answer_node`**: Transmits the structured payload matrix to the Groq/Qwen endpoint using isolated JSON prompt rules.

## Centralized PromptOps & Configuration

*   **Centralized Properties (`ApplicationSettings`)**: All system constants, math parameters, and connection metrics are consolidated into a single object model. Hardcoded values are eliminated.
*   **Dynamic Configurations (`.env`)**: Fine-tuning variables like chunk size, overlap ratios, top_k limits, temperature, or routing thresholds can be modified live without modifying code files.
*   **Decoupled Prompts (`config/market_analyst_prompts.json`)**: System instructions and context formatting templates are isolated into an external structured schema file to facilitate easy updates.


## Getting Started

### 1. Configure the Environment Variables

Create a `.env` file in the root directory and map the parameters according to your specific environment structure:

```text
GROQ_API_KEY=your_secret_groq_api_key
GROQ_MODEL_NAME=qwen/qwen3.8-27b
MODEL_TEMPERATURE=0.0
MAX_TOKENS=300
REASONING_EFFORT=none
DEFAULT_CHUNK_SIZE=55
DEFAULT_CHUNK_OVERLAP=12
DEFAULT_TOP_K=3
DEFAULT_SEARCH_LIMIT=3
EVIDENCE_THRESHOLD_SCORE=0.5
```

### 2. Local Setup and Execution

Install the dependencies into your environment:

```bash
pip install -r requirements.txt
```

Launch the unified entrypoint script to execute the bulk database seeder task manager and lift the API server online:

```bash
python src/main.py
```

### 3. Containerized Setup via Docker

Build the lightweight container image locally:

```bash
docker build -t fiqa-rag-backend-api .
```

Run the container instance while injecting your environment configurations:

```bash
docker run -d --name fiqa-backend-service -p 8000:8000 --env-file .env fiqa-rag-backend-api
```

Once the logging prints that the FAISS index is successfully populated, the Uvicorn web engine will activate the server on port `8000`.

### 4. Test the REST Interface
Access the native interactive API interface in the web browser:
*   **Swagger Documentation Link**: `http://localhost:8000/api/docs`
*   **API Target REST Endpoint**: `POST http://localhost:8000/api/v1/financial/ask`
