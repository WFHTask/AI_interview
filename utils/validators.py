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


# Maximum allowed input length for interview messages
MAX_INPUT_LENGTH = 5000


def validate_user_input(text: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate and sanitize user input for interview.
    This function performs security checks and content validation.

    Args:
        text: User input text

    Returns:
        Tuple of (is_valid, sanitized_text, error_message)
        - is_valid: True if input passes all checks
        - sanitized_text: Cleaned input text (only valid if is_valid is True)
        - error_message: Error description if validation fails, None otherwise
    """
    if not text:
        return False, "", "请输入您的回答"

    # Basic sanitization
    text = text.strip()

    # Length check
    if len(text) > MAX_INPUT_LENGTH:
        return False, "", f"输入过长，请控制在 {MAX_INPUT_LENGTH} 字符以内（当前: {len(text)} 字符）"

    if len(text) < 1:
        return False, "", "请输入有效内容"

    # Check for excessive repetition (potential DoS or spam)
    if re.search(r'(.)\1{20,}', text):
        return False, "", "输入内容格式异常，请检查后重试"

    # Check for excessive whitespace or newlines
    if re.search(r'\n{5,}', text) or re.search(r' {20,}', text):
        return False, "", "输入内容格式异常，请检查后重试"

    # Sanitize the text
    sanitized = sanitize_input(text, max_length=MAX_INPUT_LENGTH)

    return True, sanitized, None


def check_input_length(text: str) -> Tuple[bool, Optional[str]]:
    """
    Quick check for input length without full sanitization.
    Use this for real-time validation as user types.

    Args:
        text: User input text

    Returns:
        Tuple of (is_within_limit, error_message)
    """
    if not text:
        return True, None

    length = len(text)
    if length > MAX_INPUT_LENGTH:
        return False, f"输入过长（{length}/{MAX_INPUT_LENGTH}）"

    # Warning at 80% of limit
    if length > MAX_INPUT_LENGTH * 0.8:
        remaining = MAX_INPUT_LENGTH - length
        return True, f"还可输入 {remaining} 字符"

    return True, None
