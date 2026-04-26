"""AI configuration for extraction modules, cross-checks, and training."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AIConfig:
    """Configuration for the modular AI extraction and classification system."""

    ollama_url: str = "http://localhost:11434"
    models_dir: str = "~/.hledger-ai/models"
    feedback_dir: str = "~/.hledger-ai/feedback"

    vlm_model: str = "qwen3-vl:2b"
    text_model: str = "qwen3:0.6b"

    extraction_modules: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "shop_identifier": {"enabled": True},
            "line_items": {"enabled": True},
            "totals": {"enabled": True},
            "date_time": {"enabled": True},
            "category": {"enabled": True},
        }
    )

    cross_checks: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "total_items_consistency": {"enabled": True},
            "shop_address_verifier": {"enabled": True},
            "category_from_shop": {"enabled": True},
            "date_sanity": {"enabled": True},
        }
    )

    training: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "setfit": {
                "enabled": True,
                "base_model": "sentence-transformers/paraphrase-MiniLM-L6-v2",
                "min_examples_per_class": 8,
            },
            "qwen_lora": {
                "enabled": False,
                "base_model": "unsloth/Qwen3-0.6B-unsloth-bnb-4bit",
                "min_examples": 200,
            },
        }
    )

    auto_accept_threshold: float = 0.9
    suggest_threshold: float = 0.5

    def is_module_enabled(self, module_name: str) -> bool:
        """Check if an extraction module is enabled."""
        mod_cfg = self.extraction_modules.get(module_name, {})
        return mod_cfg.get("enabled", True)

    def is_cross_check_enabled(self, check_name: str) -> bool:
        """Check if a cross-check is enabled."""
        chk_cfg = self.cross_checks.get(check_name, {})
        return chk_cfg.get("enabled", True)

    def get_module_model(self, module_name: str) -> Optional[str]:
        """Get the model override for a specific module, or None."""
        mod_cfg = self.extraction_modules.get(module_name, {})
        return mod_cfg.get("model")

    @staticmethod
    def from_dict(ai_dict: Dict[str, Any]) -> "AIConfig":
        """Create AIConfig from a YAML dict (the ``ai:`` section)."""
        defaults = AIConfig()
        kwargs: Dict[str, Any] = {}
        for fld in (
            "ollama_url",
            "models_dir",
            "feedback_dir",
            "vlm_model",
            "text_model",
            "extraction_modules",
            "cross_checks",
            "training",
            "auto_accept_threshold",
            "suggest_threshold",
        ):
            if fld in ai_dict:
                kwargs[fld] = ai_dict[fld]
            else:
                kwargs[fld] = getattr(defaults, fld)
        return AIConfig(**kwargs)
