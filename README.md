# FiQA RAG - Analista de Mercado Financeiro

Sistema de Recuperacao Aumentada por Geracao (RAG) especializado em financas corporativas, investimentos e contabilidade, desenvolvido com FastAPI, LangGraph, FAISS, Groq (Llama-3) e Streamlit, com empacotamento completo em Docker.

![Interface do Sistema FiQA RAG](tela.png)

---

## Integrantes da Equipe

- Vinícius de Almeida Silva
- Hallason Matias
- Arthur
- Dayvson

---

## Como Executar o Projeto (Guia Rapido)

### 1.Configuracao de Variaveis
Crie o arquivo `.env` na raiz a partir do modelo e configure sua chave da Groq:
```bash
cp .env.example .env
# Defina GROQ_API_KEY=gsk_... dentro do .env

### 2. Execucao via Docker Compose
docker compose up --build -d
docker compose logs -f fiqa-rag-api

## Matriz de Conformidade com os Requisitos da Atividade

| Requisito Solicitado | Implementacao no Projeto | Status |
| :--- | :--- | :--- |
| **Trabalho em Equipe e Entrega** | Repositorio estruturado para submissao da atividade. | Conforme |
| **Motor do Chatbot** | Utilizacao da API da Groq com o modelo Llama-3 (sem uso de ChatGPT nativo). | Conforme |
| **Memoria Gerenciada pelo Backend** | Modulo `TaskMemoryService` centralizado no backend, controlando historico e turnos sem delegar persistencia ao modelo. | Conforme |
| **Isolamento de Contextos por Tasks** | Cada interacao esta associada a um `task_id`. Usuarios com identificadores distintos nao compartilham contexto de conversa. | Conforme |
| **Base de Dados Especializada** | Uso do dataset `FiQA (Financial Opinion QA)` do benchmark BeIR, armazenado localmente para o pipeline de RAG. | Conforme |
| **Tecnologias do Backend** | Python 3.11, FastAPI, orquestracao via LangGraph e indexacao vetorial com FAISS CPU. | Conforme |
| **Frontend Livre e Amigavel** | Interface web modularizada construida em Streamlit com suporte a selecao de perguntas, exibicao de fontes e gestao de sessao. | Conforme |
| **Execucao e Reproducibilidade** | `docker-compose.yml` completo orquestrando backend e frontend em contentores isolados. | Conforme |
| **Documentacao e Dependencias** | `README.md` explicativo, ficheiros de configuracao (`requirements.txt`, Dockerfiles) e modelo de variaveis (`.env.example`). | Conforme |

---

## Arquitetura e Engenharia do Projeto

O sistema opera sob uma arquitetura desacoplada em duas camadas principais (API e UI), orquestradas via rede interna do Docker.

### 1. Ingestao e Indexacao Vetorial (FAISS)
- **Fonte de Dados:** Coleta dos documentos e passagens do dataset financeiro FiQA.
- **Divisao de Texto (Chunking):** O processador divide os textos em blocos semanticos delimitados para assegurar alta precisao de busca.
- **Geracao de Embeddings:** O modelo `SentenceTransformer` mapeia o significado financeiro de cada fragmento em vetores densos.
- **Armazenamento:** O FAISS (Facebook AI Similarity Search) indexa e recupera por similaridade de cosseno/L2 os fragmentos mais relevantes com baixa latencia.

### 2. Gerenciamento de Memoria por Tasks no Backend
- **Regra de Isolamento:** O estado de conversacao nao e mantido no navegador e nem depende da inferencia da IA para existir.
- **TaskMemoryService:** Singleton em memoria no backend que armazena as interacoes anteriores organizadas pela chave `task_id`.
- **Injecao de Contexto:** Ao receber uma nova pergunta com um determinado `task_id`, o backend recupera os ultimos turnos associados a essa tarefa e concatena o historico ao contexto dos documentos antes da chamada ao modelo.

### 3. Orquestracao do Agente com LangGraph
O fluxo cognitivo e estruturado como uma maquina de estados direcionada (`StateGraph`), composta pelas seguintes etapas:
- **retrieve_knowledge_node:** Consulta o indice FAISS e retorna os fragmentos com maior pontuacao semantica.
- **evaluate_evidence_routing:** Avalia o limiar de confianca (`evidence_threshold_score`). Se o score for insuficiente, o agente desvia para abstencao em vez de alucinar.
- **build_context_node:** Estrutura os chunks documentais e adiciona o historico previo da `task_id`.
- **generate_answer_node:** Submete o prompt sintetizado ao Llama-3 via Groq.
- **handle_abstention_node:** Retorna resposta padrao de ausencia de informacao caso a base nao contenha subsidios suficientes.

### 4. Interface Web Modularizada (Streamlit)
- **config.py:** Centralizacao de constantes, rotas base e configuracoes da aplicacao.
- **api_client.py:** Isolamento das chamadas HTTP e comunicacao direta com a API FastAPI.
- **styles.py:** Definicoes de CSS escuro responsivo e graficos vetoriais do assistente.
- **components.py:** Renderizacao desacoplada da barra superior, hero, chips de consulta e fontes.
- **app.py:** Orquestracao do ciclo de vida da sessao, mensagens e estado do utilizador.

---

## Estrutura de Diretorios

```text
.
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── fiqa-rag-api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config/
│   ├── data/
│   └── src/
│       ├── main.py
│       ├── controllers/
│       │   └── financial_analyst_controller.py
│       ├── services/
│       │   ├── agent_workflow_builder.py
│       │   ├── market_expert_service.py
│       │   └── task_memory_service.py
│       ├── models/
│       │   ├── analysis_request.py
│       │   ├── financial_analyst_state.py
│       │   └── application_settings.py
│       ├── repositories/
│       │   ├── market_knowledge_repository.py
│       │   ├── language_model_repository.py
│       │   └── source_dataset_repository.py
│       └── processors/
│           ├── database_seeder_processor.py
│           ├── text_splitter_processor.py
│           └── logger_mix_in.py
└── fiqa-rag-ui/
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py
    ├── api_client.py
    ├── components.py
    ├── config.py
    └── styles.py