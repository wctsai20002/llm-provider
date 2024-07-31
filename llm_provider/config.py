import yaml
import os
from typing import Dict, Any
from importlib import resources

def _load_default_config() -> Dict[str, Any]:
    try:
        with resources.open_text("llm_provider", "default_config.yaml") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading default config: {str(e)}")
        return {}

def load_user_config(config_path: str) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        print(f"User config file not found: {config_path}")
        return {}
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading user config from {config_path}: {str(e)}")
        return {}

def _merge_configs(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    merged = default.copy()
    for key, value in user.items():
        if isinstance(value, dict) and key in merged:
            merged[key] = _merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged

# Initialize with default config
CONFIG = _load_default_config()

def update_config(user_config_path: str):
    global CONFIG
    user_config = load_user_config(user_config_path)
    CONFIG = _merge_configs(CONFIG, user_config)

# Helper functions
def get_browser_config(browser: str) -> Dict[str, Any]:
    return CONFIG.get(browser, {})

def get_provider_config(provider: str) -> Dict[str, Any]:
    return CONFIG.get(provider, {})