"""Configuration Management for Financial QA Bot"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Production configuration for the Financial QA Bot."""
    
    # LLM Settings
    USE_LLM: bool = True
    MODEL: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.3
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
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
            MODEL=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            API_KEY=os.getenv("OPENAI_API_KEY", ""),
            DATA_FILE=os.getenv("DATA_FILE", "sample_data.csv"),
            OUTPUT_DIR=os.getenv("OUTPUT_DIR", "output"),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        )
