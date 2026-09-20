import os

class ApplicationSettings:

    CORPUS_DATASET_REGISTRY: str = "BeIR/fiqa"
    MAPPING_DATASET_REGISTRY: str = "BeIR/fiqa-qrels"
    CORPUS_SPLIT_KEY: str = "corpus"
    QUERIES_SPLIT_KEY: str = "queries"
    DEFAULT_CONFIG_KEY: str = "default"
    TEST_PARTITION_KEY: str = "test"
    EMBEDDING_MODEL_REGISTRY: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    INITIAL_SCORE_VALUE: float = 0.0
    PROMPT_CONFIG_FILE_PATH: str = os.path.join("config", "market_analyst_prompts.json")

    @property
    def groq_api_key(self) -> str:
        return os.getenv("GROQ_API_KEY", "")

    @property
    def generation_model_name(self) -> str:
        return os.getenv("GROQ_MODEL_NAME", "qwen/qwen3.8-27b")

    @property
    def model_temperature(self) -> float:
        return float(os.getenv("GROQ_MODEL_TEMPERATURE", "0.0"))

    @property
    def max_completion_tokens(self) -> int:
        return int(os.getenv("GROQ_MAX_TOKENS", "300"))

    @property
    def reasoning_effort_level(self) -> str:
        return os.getenv("GROQ_REASONING_EFFORT", "none")

    @property
    def default_chunk_size(self) -> int:
        return int(os.getenv("DEFAULT_CHUNK_SIZE", "55"))

    @property
    def default_chunk_overlap(self) -> int:
        return int(os.getenv("DEFAULT_CHUNK_OVERLAP", "12"))

    @property
    def default_top_k(self) -> int:
        return int(os.getenv("DEFAULT_TOP_K", "3"))

    @property
    def default_search_limit(self) -> int:
        return int(os.getenv("DEFAULT_SEARCH_LIMIT", "3"))

    @property
    def evidence_threshold_score(self) -> float:
        return float(os.getenv("EVIDENCE_THRESHOLD_SCORE", "0.5"))