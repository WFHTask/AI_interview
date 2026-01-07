"""
Job Configuration Service

Manages job configurations created by HR for interview sessions.
Each configuration gets a unique ID that can be used to generate interview links.

Features:
- File locking for concurrent access safety
- Atomic writes to prevent corruption
- Link expiration management
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from config.settings import Settings
from utils.file_lock import file_lock, safe_write_json


# Link expiry days from settings


class JobConfig(BaseModel):
    """Job configuration created by HR"""
    config_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Job details
    job_description: str
    job_title: str = ""  # Optional job title for display

    # Custom greeting for interviewer (optional)
    # If empty, AI will generate a default greeting
    custom_greeting: str = ""

    # S-tier configuration
    s_tier_invitation: str = "请直接添加 CTO 微信进行沟通"
    s_tier_link: str = ""

    # Notification
    feishu_webhook: str = ""

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = "admin"  # For future multi-user support
    is_active: bool = True
    expires_at: Optional[datetime] = None  # Link expiration time

    # Statistics
    interview_count: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        # Set default expiry if not provided
        if self.expires_at is None:
            from datetime import timedelta
            self.expires_at = datetime.now() + timedelta(days=Settings.LINK_EXPIRY_DAYS)

    def is_expired(self) -> bool:
        """Check if the interview link has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_valid(self) -> bool:
        """Check if config is valid (active and not expired)"""
        return self.is_active and not self.is_expired()

    def get_interview_url(self, base_url: str = None) -> str:
        """Generate interview URL for candidates"""
        if base_url is None:
            base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")
        return f"{base_url}/?job={self.config_id}"

    def days_until_expiry(self) -> int:
        """Get days until link expires"""
        if self.expires_at is None:
            return -1
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)


class JobConfigService:
    """
    Service for managing job configurations

    Storage structure:
    data/job_configs/
    ├── abc123.json
    ├── def456.json
    └── ...
    """

    def __init__(self, base_dir: Path = None):
        self.base_dir = Path(base_dir) if base_dir else Path(Settings.BASE_DIR) / "data" / "job_configs"
        self._ensure_dir_exists()

    def _ensure_dir_exists(self) -> None:
        """Create base directory if not exists"""
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_config_path(self, config_id: str) -> Path:
        """Get file path for config"""
        return self.base_dir / f"{config_id}.json"

    def save_config(self, config: JobConfig) -> str:
        """
        Save job configuration with file locking.

        Args:
            config: Job configuration to save

        Returns:
            Config ID
        """
        path = self._get_config_path(config.config_id)

        data = config.model_dump(mode="json")

        # Use safe write with locking
        safe_write_json(str(path), data)

        return config.config_id

    def load_config(self, config_id: str) -> Optional[JobConfig]:
        """
        Load job configuration by ID with file locking.

        Args:
            config_id: Configuration ID

        Returns:
            JobConfig or None if not found
        """
        path = self._get_config_path(config_id)

        if not path.exists():
            return None

        try:
            with file_lock(str(path)):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            return JobConfig(**data)
        except Exception:
            return None

    def update_config(self, config: JobConfig) -> bool:
        """
        Update existing configuration

        Args:
            config: Updated configuration

        Returns:
            True if successful
        """
        path = self._get_config_path(config.config_id)

        if not path.exists():
            return False

        self.save_config(config)
        return True

    def increment_interview_count(self, config_id: str) -> bool:
        """
        Increment interview count for a config

        Args:
            config_id: Configuration ID

        Returns:
            True if successful
        """
        config = self.load_config(config_id)
        if not config:
            return False

        config.interview_count += 1
        self.save_config(config)
        return True

    def list_configs(self, active_only: bool = True) -> List[JobConfig]:
        """
        List all job configurations

        Args:
            active_only: Only return active configs

        Returns:
            List of JobConfig objects
        """
        configs = []

        for file in self.base_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                config = JobConfig(**data)

                if active_only and not config.is_active:
                    continue

                configs.append(config)
            except Exception:
                continue

        # Sort by created_at descending
        configs.sort(key=lambda x: x.created_at, reverse=True)
        return configs

    def delete_config(self, config_id: str) -> bool:
        """
        Delete (deactivate) a configuration

        Args:
            config_id: Configuration ID

        Returns:
            True if successful
        """
        config = self.load_config(config_id)
        if not config:
            return False

        config.is_active = False
        self.save_config(config)
        return True

    def create_config(
        self,
        job_description: str,
        job_title: str = "",
        custom_greeting: str = "",
        s_tier_invitation: str = "",
        s_tier_link: str = "",
        feishu_webhook: str = ""
    ) -> JobConfig:
        """
        Create a new job configuration

        Args:
            job_description: Job description text
            job_title: Optional job title
            custom_greeting: Custom interviewer greeting
            s_tier_invitation: S-tier invitation text
            s_tier_link: S-tier booking link
            feishu_webhook: Feishu webhook URL

        Returns:
            Created JobConfig
        """
        config = JobConfig(
            job_description=job_description,
            job_title=job_title,
            custom_greeting=custom_greeting,
            s_tier_invitation=s_tier_invitation or "请直接添加 CTO 微信进行沟通",
            s_tier_link=s_tier_link,
            feishu_webhook=feishu_webhook
        )

        self.save_config(config)
        return config


# Singleton instance
job_config_service = JobConfigService()


def create_job_config(
    job_description: str,
    job_title: str = "",
    custom_greeting: str = "",
    s_tier_invitation: str = "",
    s_tier_link: str = "",
    feishu_webhook: str = ""
) -> JobConfig:
    """
    Convenience function to create a job configuration

    Returns:
        Created JobConfig with generated ID
    """
    return job_config_service.create_config(
        job_description=job_description,
        job_title=job_title,
        custom_greeting=custom_greeting,
        s_tier_invitation=s_tier_invitation,
        s_tier_link=s_tier_link,
        feishu_webhook=feishu_webhook
    )


def get_job_config(config_id: str) -> Optional[JobConfig]:
    """
    Convenience function to get a job configuration

    Returns:
        JobConfig or None
    """
    return job_config_service.load_config(config_id)
