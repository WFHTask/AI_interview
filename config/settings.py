"""
Configuration management for AI-HR Interview System
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""

    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data" / "interviews"

    # Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL: str = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")

    # Model IDs (Gemini 3.0 - DO NOT CHANGE)
    INTERVIEWER_MODEL: str = os.getenv("INTERVIEWER_MODEL", "gemini-3-flash-preview")
    EVALUATOR_MODEL: str = os.getenv("EVALUATOR_MODEL", "gemini-3-pro-preview")

    # Thinking Levels for Gemini 3.0
    INTERVIEWER_THINKING_LEVEL: str = "MEDIUM"  # Fast interaction
    EVALUATOR_THINKING_LEVEL: str = "HIGH"      # Deep reasoning

    # Feishu Configuration
    FEISHU_WEBHOOK_URL: str = os.getenv("FEISHU_WEBHOOK_URL", "")

    # HR Admin Authentication
    HR_USERNAME: str = os.getenv("HR_USERNAME", "admin")
    HR_PASSWORD: str = os.getenv("HR_PASSWORD", "")  # Must be set in .env

    # Interview Settings
    MAX_INTERVIEW_TURNS: int = int(os.getenv("MAX_INTERVIEW_TURNS", "50"))
    MIN_INTERVIEW_TURNS: int = int(os.getenv("MIN_INTERVIEW_TURNS", "20"))

    # API Timeout (seconds)
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "120"))

    # Evaluation timeout (seconds)
    EVALUATION_TIMEOUT: int = int(os.getenv("EVALUATION_TIMEOUT", "120"))

    # Link expiry (days)
    LINK_EXPIRY_DAYS: int = int(os.getenv("LINK_EXPIRY_DAYS", "30"))

    # Session expiry (hours)
    SESSION_EXPIRY_HOURS: int = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "20"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # Scoring Thresholds
    S_TIER_THRESHOLD: int = int(os.getenv("S_TIER_THRESHOLD", "90"))
    A_TIER_THRESHOLD: int = int(os.getenv("A_TIER_THRESHOLD", "80"))
    B_TIER_THRESHOLD: int = int(os.getenv("B_TIER_THRESHOLD", "60"))

    # Default S-tier notification text (can be overridden in job config)
    S_TIER_DEFAULT_NOTIFICATION: str = os.getenv(
        "S_TIER_DEFAULT_NOTIFICATION",
        "恭喜！您的表现非常出色，完美契合我们的需求。我们希望邀请您直接与 CTO 对话，进一步探讨合作机会！"
    )

    # Default non-S-tier notification text
    DEFAULT_NOTIFICATION: str = os.getenv(
        "DEFAULT_NOTIFICATION",
        "感谢您的时间，我们已记录您的面试信息，HR 将在近期与您联系。"
    )

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file.")
        return True

    @classmethod
    def get_model_url(cls, model_type: str, streaming: bool = True) -> str:
        """
        Build Gemini API URL

        Args:
            model_type: 'interviewer' or 'evaluator'
            streaming: Use streaming endpoint

        Returns:
            Full API URL
        """
        model_id = cls.INTERVIEWER_MODEL if model_type == "interviewer" else cls.EVALUATOR_MODEL
        endpoint = "streamGenerateContent" if streaming else "generateContent"
        params = "?alt=sse" if streaming else ""
        return f"{cls.GEMINI_BASE_URL}/models/{model_id}:{endpoint}{params}"

    @classmethod
    def get_headers(cls) -> dict:
        """Get API request headers"""
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": cls.GEMINI_API_KEY
        }


# Evaluation JSON Schema (for Gemini structured output)
EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_name": {
            "type": "string",
            "description": "Candidate name extracted from conversation"
        },
        "total_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Overall score 0-100"
        },
        "decision_tier": {
            "type": "string",
            "enum": ["S", "A", "B", "C"],
            "description": "Decision tier based on score"
        },
        "is_pass": {
            "type": "boolean",
            "description": "Whether candidate passes initial screening"
        },
        "skill_match_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Technical skill match score"
        },
        "communication_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Communication ability score"
        },
        "remote_readiness_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Remote work adaptability score (self-driven, async communication)"
        },
        "key_strengths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of key strengths"
        },
        "red_flags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of concerns or red flags"
        },
        "summary": {
            "type": "string",
            "description": "Brief evaluation summary"
        },
        "notification_text": {
            "type": "string",
            "description": "Text to display to candidate"
        }
    },
    "required": [
        "candidate_name",
        "total_score",
        "decision_tier",
        "is_pass",
        "key_strengths",
        "summary",
        "notification_text"
    ]
}


# Singleton instance
settings = Settings()
