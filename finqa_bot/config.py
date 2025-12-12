import os
from dataclasses import dataclass

@dataclass
class Config:
    """ Configuration for the Financial QA Bot."""
    
    # LLM Settings (OpenRouter only)
    USE_LLM: bool = True  # toggles OpenRouter usage; falls back to rule-based when False or missing key
    MODEL: str = "mistralai/devstral-2512:free"  # OpenRouter model
    TEMPERATURE: float = 0.3
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")
    
    # File Settings
    DATA_FILE: str = "sample_data.csv"
    OUTPUT_DIR: str = "output"
    CHART_DIR: str = "output/charts"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "output/finqa_bot.log"
    
    # Feature Flags
    GENERATE_CHARTS: bool = True
    CACHE_RESULTS: bool = True
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        return cls(
            USE_LLM=os.getenv("USE_LLM", "true").lower() == "true",
            MODEL=os.getenv("LLM_MODEL", "mistralai/devstral-2512:free"),
            OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY", ""),
            OPENROUTER_MODEL=os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free"),
            DATA_FILE=os.getenv("DATA_FILE", "sample_data.csv"),
            OUTPUT_DIR=os.getenv("OUTPUT_DIR", "output"),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        )
