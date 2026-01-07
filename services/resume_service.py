"""
Resume Processing Service

Handles resume uploads (PDF/Image/Text) and extracts structured information
using Gemini 3.0 multimodal capabilities.

Supported formats:
- PDF files (application/pdf)
- Images (image/png, image/jpeg, image/webp)
- Plain text
"""
import base64
import json
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from services.gemini_service import GeminiService, GeminiAPIError
from config.settings import Settings


# Supported MIME types
SUPPORTED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
SUPPORTED_PDF_TYPES = ["application/pdf"]
SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES + SUPPORTED_PDF_TYPES

# Max file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Resume extraction prompt
RESUME_EXTRACTION_PROMPT = """请分析这份简历，提取以下关键信息并以 JSON 格式返回：

{
    "name": "候选人姓名",
    "email": "邮箱地址（如有）",
    "phone": "电话号码（如有）",
    "education": "最高学历和学校",
    "years_of_experience": "工作年限（数字）",
    "current_position": "当前/最近职位",
    "current_company": "当前/最近公司",
    "skills": ["技术技能列表"],
    "highlights": ["3-5个核心亮点/成就"],
    "summary": "100字以内的简历摘要，突出技术能力和项目经验"
}

注意：
1. 如果某项信息不存在，填写 null
2. skills 列表只包含技术技能，不要包含软技能
3. highlights 要具体，包含数字或成果
4. summary 要简洁，便于面试官快速了解候选人"""


class ResumeService:
    """
    Resume processing service using Gemini multimodal API
    """

    def __init__(self, api_key: str = None):
        """
        Initialize resume service

        Args:
            api_key: Optional Gemini API key
        """
        self.gemini_service = GeminiService(api_key=api_key)

    def _validate_file(self, file_data: bytes, mime_type: str) -> Tuple[bool, str]:
        """
        Validate uploaded file

        Args:
            file_data: File bytes
            mime_type: File MIME type

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check MIME type
        if mime_type not in SUPPORTED_TYPES:
            return False, f"不支持的文件格式: {mime_type}。支持的格式: PDF, PNG, JPG, WEBP"

        # Check file size
        if len(file_data) > MAX_FILE_SIZE:
            size_mb = len(file_data) / (1024 * 1024)
            return False, f"文件过大 ({size_mb:.1f}MB)。最大支持 10MB"

        return True, ""

    def _build_multimodal_content(
        self,
        file_data: bytes,
        mime_type: str,
        prompt: str
    ) -> list:
        """
        Build multimodal content for Gemini API

        Args:
            file_data: File bytes
            mime_type: File MIME type
            prompt: Text prompt

        Returns:
            Contents list for API
        """
        # Encode file to base64
        base64_data = base64.b64encode(file_data).decode("utf-8")

        # Build parts with inline_data for file
        parts = [
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64_data
                }
            },
            {
                "text": prompt
            }
        ]

        return [{"role": "user", "parts": parts}]

    def extract_from_file(
        self,
        file_data: bytes,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Extract resume information from PDF or image file

        Args:
            file_data: File bytes
            mime_type: File MIME type

        Returns:
            Extracted resume data dict
        """
        # Validate file
        is_valid, error_msg = self._validate_file(file_data, mime_type)
        if not is_valid:
            raise ValueError(error_msg)

        # Build multimodal content
        contents = self._build_multimodal_content(
            file_data,
            mime_type,
            RESUME_EXTRACTION_PROMPT
        )

        # Call Gemini API (use evaluator model for better reasoning)
        try:
            result = self.gemini_service.generate(
                model_type="evaluator",  # Use Pro model for better extraction
                contents=contents,
                thinking_level="MEDIUM",
                response_mime_type="application/json"
            )

            # Parse JSON response
            try:
                data = json.loads(result["text"])
                return self._normalize_resume_data(data)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                data = self._extract_json_from_text(result["text"])
                if data:
                    return self._normalize_resume_data(data)
                raise ValueError("无法解析简历信息，请检查文件格式")

        except GeminiAPIError as e:
            raise ValueError(f"简历解析失败: {str(e)}")

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract resume information from plain text

        Args:
            text: Resume text content

        Returns:
            Extracted resume data dict
        """
        if not text or len(text.strip()) < 50:
            raise ValueError("简历内容过短，请提供更完整的信息")

        # Build text-only content
        contents = [{
            "role": "user",
            "parts": [{
                "text": f"{RESUME_EXTRACTION_PROMPT}\n\n【简历内容】\n{text}"
            }]
        }]

        try:
            result = self.gemini_service.generate(
                model_type="evaluator",
                contents=contents,
                thinking_level="MEDIUM",
                response_mime_type="application/json"
            )

            data = json.loads(result["text"])
            return self._normalize_resume_data(data)

        except json.JSONDecodeError:
            data = self._extract_json_from_text(result["text"])
            if data:
                return self._normalize_resume_data(data)
            raise ValueError("无法解析简历信息")

        except GeminiAPIError as e:
            raise ValueError(f"简历解析失败: {str(e)}")

    def _normalize_resume_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate extracted resume data

        Args:
            data: Raw extracted data

        Returns:
            Normalized data dict
        """
        # Ensure required fields exist
        normalized = {
            "name": data.get("name") or "Unknown",
            "email": data.get("email") or "",
            "phone": data.get("phone") or "",
            "education": data.get("education") or "",
            "years_of_experience": data.get("years_of_experience"),
            "current_position": data.get("current_position") or "",
            "current_company": data.get("current_company") or "",
            "skills": data.get("skills") or [],
            "highlights": data.get("highlights") or [],
            "summary": data.get("summary") or ""
        }

        # Ensure skills and highlights are lists
        if isinstance(normalized["skills"], str):
            normalized["skills"] = [s.strip() for s in normalized["skills"].split(",")]
        if isinstance(normalized["highlights"], str):
            normalized["highlights"] = [normalized["highlights"]]

        # Limit lists
        normalized["skills"] = normalized["skills"][:15]
        normalized["highlights"] = normalized["highlights"][:5]

        return normalized

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """
        Try to extract JSON from text response

        Args:
            text: Raw text response

        Returns:
            Parsed dict or None
        """
        import re

        # Try to find JSON block
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if match.lastindex else match.group(0)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

        return None

    def format_resume_summary(self, data: Dict[str, Any]) -> str:
        """
        Format resume data into a summary string for interview prompt

        Args:
            data: Normalized resume data

        Returns:
            Formatted summary string
        """
        parts = []

        if data.get("current_position") or data.get("current_company"):
            position = data.get("current_position", "")
            company = data.get("current_company", "")
            if position and company:
                parts.append(f"当前职位: {position} @ {company}")
            elif position:
                parts.append(f"当前职位: {position}")
            elif company:
                parts.append(f"当前公司: {company}")

        if data.get("years_of_experience"):
            parts.append(f"工作年限: {data['years_of_experience']}年")

        if data.get("education"):
            parts.append(f"学历: {data['education']}")

        if data.get("skills"):
            skills_str = ", ".join(data["skills"][:8])
            parts.append(f"技术技能: {skills_str}")

        if data.get("highlights"):
            parts.append("核心亮点:")
            for h in data["highlights"][:3]:
                parts.append(f"  - {h}")

        if data.get("summary"):
            parts.append(f"\n简历摘要: {data['summary']}")

        return "\n".join(parts)


# Singleton instance
resume_service = ResumeService()


def parse_resume(
    file_data: bytes = None,
    mime_type: str = None,
    text: str = None
) -> Dict[str, Any]:
    """
    Convenience function to parse resume from file or text

    Args:
        file_data: File bytes (for PDF/image)
        mime_type: File MIME type
        text: Plain text content

    Returns:
        Extracted resume data dict
    """
    if file_data and mime_type:
        return resume_service.extract_from_file(file_data, mime_type)
    elif text:
        return resume_service.extract_from_text(text)
    else:
        raise ValueError("请提供文件或文本内容")


def get_resume_summary(data: Dict[str, Any]) -> str:
    """
    Get formatted resume summary for interview

    Args:
        data: Resume data dict

    Returns:
        Formatted summary string
    """
    return resume_service.format_resume_summary(data)
