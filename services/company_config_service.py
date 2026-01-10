"""
Company Configuration Service

Manages global company information that is used across all interviews.
Stores data in a single JSON file: data/company_config.json

Features:
- File locking for concurrent access safety
- Atomic writes to prevent corruption
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import Settings
from models.schemas import CompanyConfig
from utils.file_lock import file_lock, safe_write_json


class CompanyConfigService:
    """
    Service for managing company configuration

    Storage: data/company_config.json (single file)
    """

    def __init__(self, base_dir: Path = None):
        """
        Initialize company config service

        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = Path(base_dir) if base_dir else Path(Settings.BASE_DIR) / "data"
        self._ensure_dir_exists()
        self.config_path = self.base_dir / "company_config.json"

    def _ensure_dir_exists(self) -> None:
        """Create base directory if not exists"""
        os.makedirs(self.base_dir, exist_ok=True)

    def get_config(self) -> CompanyConfig:
        """
        Get company configuration

        Returns:
            CompanyConfig object (empty config if not exists)
        """
        if not self.config_path.exists():
            return CompanyConfig()

        try:
            with file_lock(str(self.config_path)):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            return CompanyConfig(**data)
        except Exception:
            return CompanyConfig()

    def save_config(self, config: CompanyConfig) -> bool:
        """
        Save company configuration with file locking

        Args:
            config: Company configuration to save

        Returns:
            True if saved successfully
        """
        try:
            # Update timestamp
            config.updated_at = datetime.now()

            # Convert to dict
            data = config.model_dump(mode="json")

            # Use safe write with locking
            safe_write_json(str(self.config_path), data)

            return True
        except Exception as e:
            import logging
            logging.error(f"Failed to save company config: {e}")
            return False

    def update_background(self, company_background: str) -> bool:
        """
        Update company background (convenience method)

        Args:
            company_background: New company background text

        Returns:
            True if saved successfully
        """
        config = self.get_config()
        config.company_background = company_background
        return self.save_config(config)

    def has_config(self) -> bool:
        """
        Check if company config has been set

        Returns:
            True if company_background is not empty
        """
        config = self.get_config()
        return bool(config.company_background and config.company_background.strip())


# Singleton instance
company_config_service = CompanyConfigService()


def get_company_config() -> CompanyConfig:
    """
    Convenience function to get company configuration

    Returns:
        CompanyConfig object
    """
    return company_config_service.get_config()


def save_company_config(config: CompanyConfig) -> bool:
    """
    Convenience function to save company configuration

    Args:
        config: Company configuration

    Returns:
        True if saved successfully
    """
    return company_config_service.save_config(config)


def get_company_background() -> str:
    """
    Convenience function to get company background text

    Returns:
        Company background string (empty if not set)
    """
    config = company_config_service.get_config()
    return config.company_background or ""
