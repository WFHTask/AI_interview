"""
Utility helper functions for AI-HR Interview System
"""
import re
import json
from datetime import datetime
from typing import Optional, Dict, Any


def sanitize_text(text: str) -> str:
    """
    Sanitize text input to prevent injection attacks

    Args:
        text: Raw input text

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove potential prompt injection patterns
    patterns_to_remove = [
        r'ignore\s+(all\s+)?(previous|above)\s+instructions?',
        r'disregard\s+(all\s+)?(previous|above)\s+instructions?',
        r'forget\s+(all\s+)?(previous|above)\s+instructions?',
        r'you\s+are\s+now\s+in\s+\w+\s+mode',
        r'system\s*:\s*',
        r'assistant\s*:\s*',
        r'\[INST\]',
        r'\[/INST\]',
    ]

    sanitized = text
    for pattern in patterns_to_remove:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text that may contain other content

    Args:
        text: Text potentially containing JSON

    Returns:
        Parsed JSON dict or None
    """
    if not text:
        return None

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in markdown
    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1)
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                continue

    return None


def format_timestamp(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string

    Args:
        dt: Datetime object (default: now)
        format_str: Format string

    Returns:
        Formatted string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to max length

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def calculate_token_estimate(text: str) -> int:
    """
    Estimate token count for text (rough approximation)

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    # Rough estimation: ~4 characters per token for English
    # ~2 characters per token for Chinese
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    other_chars = len(text) - chinese_chars

    return (chinese_chars // 2) + (other_chars // 4)


def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive data in text for logging

    Args:
        text: Input text

    Returns:
        Text with sensitive data masked
    """
    # Mask API keys
    text = re.sub(
        r'(api[_-]?key|apikey|key)["\']?\s*[:=]\s*["\']?[\w-]{20,}',
        r'\1: ***MASKED***',
        text,
        flags=re.IGNORECASE
    )

    # Mask webhook URLs
    text = re.sub(
        r'(webhook|hook)["\']?\s*[:=]\s*["\']?https?://[^\s"\']+',
        r'\1: ***MASKED_URL***',
        text,
        flags=re.IGNORECASE
    )

    return text


def is_valid_webhook_url(url: str) -> bool:
    """
    Validate Feishu webhook URL format

    Args:
        url: URL to validate

    Returns:
        True if valid
    """
    if not url:
        return False

    pattern = r'^https://open\.feishu\.cn/open-apis/bot/v2/hook/[\w-]+$'
    return bool(re.match(pattern, url))


def parse_score_to_tier(score: int) -> str:
    """
    Convert score to tier label

    Args:
        score: Score 0-100

    Returns:
        Tier string (S/A/B/C)
    """
    from config.settings import Settings

    if score >= Settings.S_TIER_THRESHOLD:
        return "S"
    elif score >= Settings.A_TIER_THRESHOLD:
        return "A"
    elif score >= Settings.B_TIER_THRESHOLD:
        return "B"
    else:
        return "C"
