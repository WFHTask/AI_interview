"""
Input Validators

Validation utilities for user input sanitization and verification.
"""
import re
from typing import Optional, Tuple


def validate_candidate_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate candidate name.

    Args:
        name: Candidate name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "请输入姓名"

    name = name.strip()

    if len(name) < 2:
        return False, "姓名至少需要 2 个字符"

    if len(name) > 50:
        return False, "姓名不能超过 50 个字符"

    # Check for invalid characters (only allow letters, Chinese, spaces, hyphens)
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s\-·]+$', name):
        return False, "姓名只能包含中文、英文、空格和连字符"

    # Check for suspicious patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
        r'SELECT\s+.*\s+FROM',
        r'DROP\s+TABLE',
        r'INSERT\s+INTO',
        r'--',
        r';',
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return False, "输入包含非法字符"

    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "请输入邮箱"

    email = email.strip().lower()

    if len(email) > 254:
        return False, "邮箱地址过长"

    # Basic email format check
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "邮箱格式不正确"

    # Check for common typos
    common_domains = ['gmail.com', 'qq.com', '163.com', 'outlook.com', 'hotmail.com', 'yahoo.com']
    domain = email.split('@')[1] if '@' in email else ''

    # Suggest corrections for common typos
    typo_corrections = {
        'gmial.com': 'gmail.com',
        'gamil.com': 'gmail.com',
        'gmal.com': 'gmail.com',
        'gmali.com': 'gmail.com',
        'outlok.com': 'outlook.com',
        'outloook.com': 'outlook.com',
        'hotmal.com': 'hotmail.com',
        'yaho.com': 'yahoo.com',
    }

    if domain in typo_corrections:
        suggestion = typo_corrections[domain]
        return False, f"您是否要输入 {email.split('@')[0]}@{suggestion}?"

    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number (Chinese format).

    Args:
        phone: Phone number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return True, None  # Phone is optional

    # Remove common separators
    phone = re.sub(r'[\s\-\(\)]', '', phone)

    # Chinese mobile number format
    if re.match(r'^1[3-9]\d{9}$', phone):
        return True, None

    # Chinese landline format (with area code)
    if re.match(r'^0\d{2,3}\d{7,8}$', phone):
        return True, None

    # International format
    if re.match(r'^\+\d{1,3}\d{6,14}$', phone):
        return True, None

    return False, "请输入有效的手机号码"


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Trim whitespace
    text = text.strip()

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    # Remove null bytes
    text = text.replace('\x00', '')

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove control characters (except newline and tab)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text


def validate_interview_message(message: str) -> Tuple[bool, Optional[str]]:
    """
    Validate interview message from candidate.

    Args:
        message: Message to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message:
        return False, "请输入您的回答"

    message = message.strip()

    if len(message) < 2:
        return False, "回答内容过短"

    if len(message) > 5000:
        return False, "回答内容过长，请精简后重试"

    # Check for spam patterns
    spam_patterns = [
        r'(.)\\1{10,}',  # Same character repeated 10+ times
        r'https?://[^\s]+',  # URLs
        r'www\.[^\s]+',  # URLs without protocol
    ]

    for pattern in spam_patterns:
        if re.search(pattern, message):
            return False, "回答内容包含不支持的格式"

    return True, None


def validate_candidate_info(
    name: str,
    email: str,
    phone: str = ""
) -> Tuple[bool, dict]:
    """
    Validate all candidate information.

    Args:
        name: Candidate name
        email: Candidate email
        phone: Candidate phone (optional)

    Returns:
        Tuple of (all_valid, errors_dict)
    """
    errors = {}

    is_valid, error = validate_candidate_name(name)
    if not is_valid:
        errors["name"] = error

    is_valid, error = validate_email(email)
    if not is_valid:
        errors["email"] = error

    if phone:
        is_valid, error = validate_phone(phone)
        if not is_valid:
            errors["phone"] = error

    return len(errors) == 0, errors
