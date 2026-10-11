"""Central configuration for the extended AgentCoder benchmark runner."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    value = _env(name, str(default))
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    provider: str = _env("LLM_PROVIDER", _env("MODEL_PROVIDER", "kilo"))
    kilo_base_url: str = _env("OPENAI_BASE_URL", _env("KILO_BASE_URL", "https://api.kilo.ai/api/gateway"))
    kilo_api_key: str = _env("OPENAI_API_KEY", _env("KILO_API_KEY", ""))
    kilo_model: str = _env("OPENAI_MODEL", _env("KILO_MODEL", "liquid/lfm-2.5-2.6b:free"))

    model: str = _env("MODEL", _env("OPENAI_MODEL", _env("KILO_MODEL", "liquid/lfm-2.5-2.6b:free")))
    code_generation_model: str = _env("CODE_GENERATION_MODEL", "")
    formal_spec_model: str = _env("FORMAL_SPEC_MODEL", "")
    unit_test_model: str = _env("UNIT_TEST_MODEL", "")
    property_test_model: str = _env("PROPERTY_TEST_MODEL", "")


    max_iterations: int = _env_int("MAX_ITERATIONS", 1)
    test_timeout_seconds: int = _env_int("TEST_TIMEOUT_SECONDS", 10)

    request_timeout_seconds: float = float(_env("OPENAI_REQUEST_TIMEOUT", "45.0"))
    output_dir: Path = Path(_env("OUTPUT_DIR", "runs"))

    dataset_name: str = _env("DATASET_NAME", "mbpp")
    dataset_split: str = _env("DATASET_SPLIT", "test")
    dataset_level: int = _env_int("DATASET_LEVEL", 1)
    dataset_lib: str = _env("DATASET_LIB", "")
    dataset_local_path: str = _env("DATASET_LOCAL_PATH", "")
    property_strategy: str = _env("PROPERTY_STRATEGY", "hypothesis")
    generation_retries: int = _env_int("GENERATION_RETRIES", 3)
    formal_spec_retries: int = _env_int("FORMAL_SPEC_RETRIES", 3)
    test_generation_retries: int = _env_int("TEST_GENERATION_RETRIES", 3)
    artifact_root_name: str = _env("ARTIFACT_ROOT_NAME", "mbpp")


    def resolve_model(self, stage: str) -> str:
        specific = {
            "code_generation": self.code_generation_model,
            "formal_spec": self.formal_spec_model,
            "unit_test": self.unit_test_model,
            "property_test": self.property_test_model,
        }.get(stage, "")
        if specific:
            return specific
        if self.model:
            return self.model
        if self.kilo_model:
            return self.kilo_model
        raise ValueError(
            "No model configured. Set KILO_MODEL or the stage-specific model env vars, e.g. CODE_GENERATION_MODEL."
        )


CONFIG = AppConfig()
