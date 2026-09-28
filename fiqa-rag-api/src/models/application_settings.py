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
    PROMPTS_DIRECTORY: str = os.path.join("config", "prompts")
    ABSTENTION_MESSAGE: str = "I could not find this information in the consulted database."
    OUT_OF_DOMAIN_MESSAGE: str = "This question is outside the scope of this assistant, which answers questions about personal finance, investing, taxes, banking and business."

    @property
    def groq_api_key(self) -> str:
        return os.getenv("GROQ_API_KEY", "")

    @property
    def generation_model_name(self) -> str:
        return os.getenv("GROQ_MODEL_NAME", "qwen/qwen3.8-27b")

    @property
    def model_temperature(self) -> float:
        return float(os.getenv("MODEL_TEMPERATURE", "0.0"))

    @property
    def max_completion_tokens(self) -> int:
        return int(os.getenv("MAX_TOKENS", "300"))

    @property
    def classification_max_tokens(self) -> int:
        return int(os.getenv("CLASSIFICATION_MAX_TOKENS", "150"))

    @property
    def reasoning_effort_level(self) -> str:
        return os.getenv("REASONING_EFFORT", "none")

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
        
    @property
    def prompt_version(self) -> str:
        return os.getenv("PROMPT_VERSION", "v3.0.0__decomposed")

    @property
    def prompt_config_file_path(self) -> str:
        return os.path.join(self.PROMPTS_DIRECTORY, f"{self.prompt_version}.json")

    @property
    def max_history_exchanges(self) -> int:
        return int(os.getenv("MAX_HISTORY_EXCHANGES", "4"))