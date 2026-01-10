"""
Gemini 3.0 REST API Service (No SDK, Pure REST API)

Features:
- Streaming response (default)
- Thought Signature handling for multi-turn conversations
- Thinking Level configuration
- JSON Schema enforcement for structured output
"""
import json
import time
import requests
from typing import Generator, Optional, List, Dict, Any, Tuple

from config.settings import Settings, EVALUATION_SCHEMA


class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class GeminiService:
    """
    Gemini 3.0 REST API Service

    Models:
    - Interviewer: gemini-3-flash-preview (fast, low latency)
    - Evaluator: gemini-3-pro-preview (deep reasoning, stable JSON)
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or Settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")

        self.headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0  # seconds

    def _build_url(self, model_type: str, streaming: bool = True) -> str:
        """
        Build Gemini API URL

        Args:
            model_type: 'interviewer' or 'evaluator'
            streaming: Use streaming endpoint (default True)

        Returns:
            Full API URL
        """
        model_id = (
            Settings.INTERVIEWER_MODEL
            if model_type == "interviewer"
            else Settings.EVALUATOR_MODEL
        )
        endpoint = "streamGenerateContent" if streaming else "generateContent"
        params = "?alt=sse" if streaming else ""
        return f"{Settings.GEMINI_BASE_URL}/models/{model_id}:{endpoint}{params}"

    def _build_payload(
        self,
        contents: List[Dict],
        system_instruction: Optional[str] = None,
        thinking_level: str = "MEDIUM",
        thought_signature: Optional[str] = None,
        response_mime_type: Optional[str] = None,
        response_schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Build request payload for Gemini API

        Args:
            contents: Conversation history in Gemini format
            system_instruction: System prompt
            thinking_level: MINIMAL/LOW/MEDIUM/HIGH
            thought_signature: Previous thought signature (for multi-turn)
            response_mime_type: Force response format (e.g., application/json)
            response_schema: JSON Schema for structured output

        Returns:
            Request payload dict
        """
        payload = {
            "contents": contents,
            "generationConfig": {
                "thinkingConfig": {
                    "thinkingLevel": thinking_level,
                    "includeThoughts": False  # Don't return thinking process
                }
            }
        }

        # System instruction
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Multi-turn: pass back thought signature
        if thought_signature:
            payload["generationConfig"]["thoughtSignature"] = thought_signature

        # Force JSON output
        if response_mime_type:
            payload["generationConfig"]["responseMimeType"] = response_mime_type

        if response_schema:
            payload["generationConfig"]["responseSchema"] = response_schema

        return payload

    def _request_with_retry(
        self,
        url: str,
        payload: Dict,
        stream: bool = False,
        timeout: int = 120
    ) -> requests.Response:
        """
        Make request with exponential backoff retry

        Args:
            url: Request URL
            payload: Request body
            stream: Enable streaming
            timeout: Request timeout in seconds

        Returns:
            Response object
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    stream=stream,
                    timeout=timeout
                )
                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                last_exception = e
                status_code = e.response.status_code if e.response else None

                # Don't retry on client errors (except 429)
                if status_code and 400 <= status_code < 500 and status_code != 429:
                    # Safely try to parse response JSON
                    response_data = None
                    try:
                        if e.response is not None:
                            response_data = e.response.json()
                    except (ValueError, json.JSONDecodeError):
                        pass

                    raise GeminiAPIError(
                        f"API request failed: {str(e)}",
                        status_code=status_code,
                        response=response_data
                    )

                # Exponential backoff
                delay = self.base_delay * (2 ** attempt)
                time.sleep(delay)

            except requests.exceptions.RequestException as e:
                last_exception = e
                delay = self.base_delay * (2 ** attempt)
                time.sleep(delay)

        raise GeminiAPIError(f"Max retries exceeded: {str(last_exception)}")

    def stream_generate(
        self,
        model_type: str,
        contents: List[Dict],
        system_instruction: Optional[str] = None,
        thinking_level: str = "MEDIUM",
        thought_signature: Optional[str] = None
    ) -> Generator[Tuple[str, Optional[str]], None, None]:
        """
        Stream generate content from Gemini API

        Args:
            model_type: 'interviewer' or 'evaluator'
            contents: Conversation history
            system_instruction: System prompt
            thinking_level: Thinking depth level
            thought_signature: Previous thought signature

        Yields:
            Tuple of (text_chunk, new_thought_signature)
            - text_chunk: Generated text piece
            - new_thought_signature: Updated signature (only in last yield)
        """
        url = self._build_url(model_type, streaming=True)
        payload = self._build_payload(
            contents=contents,
            system_instruction=system_instruction,
            thinking_level=thinking_level,
            thought_signature=thought_signature
        )

        response = self._request_with_retry(url, payload, stream=True)

        new_thought_signature = None
        buffer = ""

        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode('utf-8')

            # SSE format: "data: {...}"
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])

                    candidates = data.get('candidates', [])
                    if not candidates:
                        continue

                    candidate = candidates[0]

                    # Check for safety blocks
                    finish_reason = candidate.get('finishReason', '')
                    if finish_reason in ('SAFETY', 'BLOCKED'):
                        yield ("[内容被安全过滤器阻止]", None)
                        continue

                    # Extract text content
                    content = candidate.get('content')
                    if content:
                        parts = content.get('parts', [])
                        for part in parts:
                            if not part:
                                continue
                            # Skip thinking parts
                            if part.get('thought'):
                                continue
                            if 'text' in part:
                                text = part['text']
                                buffer += text
                                yield (text, None)

                    # Extract new thought signature
                    if 'thoughtSignature' in candidate:
                        new_thought_signature = candidate['thoughtSignature']

                except json.JSONDecodeError as e:
                    # Log malformed SSE data for debugging
                    import logging
                    logging.debug(f"Malformed SSE JSON chunk: {line[:100]}... Error: {e}")
                    continue

        # Final yield with thought signature
        if new_thought_signature:
            yield ("", new_thought_signature)

    def generate(
        self,
        model_type: str,
        contents: List[Dict],
        system_instruction: Optional[str] = None,
        thinking_level: str = "HIGH",
        response_mime_type: Optional[str] = None,
        response_schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Non-streaming generate (for evaluation with structured JSON output)

        Args:
            model_type: 'interviewer' or 'evaluator'
            contents: Conversation history
            system_instruction: System prompt
            thinking_level: Thinking depth level
            response_mime_type: Force response format
            response_schema: JSON Schema for output

        Returns:
            Dict with 'text', 'usage', 'thought_signature'
        """
        url = self._build_url(model_type, streaming=False)
        payload = self._build_payload(
            contents=contents,
            system_instruction=system_instruction,
            thinking_level=thinking_level,
            response_mime_type=response_mime_type,
            response_schema=response_schema
        )

        response = self._request_with_retry(url, payload, stream=False)
        result = response.json()

        # Extract text with comprehensive null checks
        text = ""
        thought_signature = None

        candidates = result.get('candidates', [])
        if not candidates:
            raise GeminiAPIError(
                "API returned empty candidates",
                response=result
            )

        candidate = candidates[0]
        content = candidate.get('content')

        if content:
            parts = content.get('parts', [])
            for part in parts:
                if part and 'text' in part:
                    text += part['text']

        thought_signature = candidate.get('thoughtSignature')

        # Check for blocked or empty response
        finish_reason = candidate.get('finishReason', '')
        if finish_reason == 'SAFETY' or finish_reason == 'BLOCKED':
            raise GeminiAPIError(
                f"Response blocked by safety filter: {finish_reason}",
                response=result
            )

        if not text:
            raise GeminiAPIError(
                "API returned empty text content",
                response=result
            )

        return {
            "text": text,
            "usage": result.get("usageMetadata", {}),
            "thought_signature": thought_signature
        }

    def evaluate_interview(
        self,
        chat_history: str,
        job_description: str,
        system_instruction: str
    ) -> Dict[str, Any]:
        """
        Evaluate interview using Evaluator model with structured JSON output

        Args:
            chat_history: Full interview conversation text
            job_description: Job description
            system_instruction: Evaluator system prompt

        Returns:
            Parsed evaluation result dict
        """
        prompt = f"""
请根据以下信息对候选人进行评估：

【岗位描述】
{job_description}

【面试对话记录】
{chat_history}

请按照系统要求输出 JSON 格式的评估结果。
"""

        result = self.generate(
            model_type="evaluator",
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            system_instruction=system_instruction,
            thinking_level="HIGH",
            response_mime_type="application/json",
            response_schema=EVALUATION_SCHEMA
        )

        # Parse JSON response
        try:
            return json.loads(result["text"])
        except json.JSONDecodeError as e:
            raise GeminiAPIError(f"Failed to parse evaluation JSON: {e}")


class ConversationManager:
    """
    Manage multi-turn conversation with Thought Signature handling

    Gemini 3.0 requires thought_signature to be passed back in multi-turn
    conversations to maintain model's reasoning state.
    """

    def __init__(self, gemini_service: GeminiService):
        self.service = gemini_service
        self.history: List[Dict] = []
        self.thought_signature: Optional[str] = None

    def add_user_message(self, text: str) -> None:
        """Add user message to history"""
        self.history.append({
            "role": "user",
            "parts": [{"text": text}]
        })

    def add_model_message(self, text: str) -> None:
        """Add model message to history"""
        self.history.append({
            "role": "model",
            "parts": [{"text": text}]
        })

    def stream_chat(
        self,
        user_message: str,
        system_instruction: str,
        thinking_level: str = "MEDIUM"
    ) -> Generator[str, None, str]:
        """
        Stream chat with automatic thought signature management

        Args:
            user_message: User's input
            system_instruction: System prompt
            thinking_level: Thinking depth

        Yields:
            str: Text chunks

        Returns:
            str: Full response text
        """
        self.add_user_message(user_message)

        full_response = ""

        for chunk, signature in self.service.stream_generate(
            model_type="interviewer",
            contents=self.history,
            system_instruction=system_instruction,
            thinking_level=thinking_level,
            thought_signature=self.thought_signature
        ):
            if chunk:
                full_response += chunk
                yield chunk

            # Update thought signature
            if signature:
                self.thought_signature = signature

        # Save model response to history
        self.add_model_message(full_response)

        return full_response

    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.history.copy()

    def clear(self) -> None:
        """Clear conversation history and signature"""
        self.history = []
        self.thought_signature = None
