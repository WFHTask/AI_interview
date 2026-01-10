"""
Evaluator Engine - AI Interview Judge

Uses Gemini 3.0 Pro for deep reasoning and structured JSON output.
Evaluates interview performance and makes hiring decisions.

Features:
- Timeout handling for long evaluations
- Automatic retry on transient failures
- Fallback evaluation for error cases
"""
import json
import logging
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from services.gemini_service import GeminiService, GeminiAPIError
from models.schemas import (
    InterviewSession,
    EvaluationResult,
    DecisionTier,
    FeishuNotification
)
from config.settings import Settings, EVALUATION_SCHEMA
from core.prompts import EVALUATOR_PROMPT

logger = logging.getLogger(__name__)

# Max retries for evaluation
MAX_RETRIES = 2


class EvaluatorEngine:
    """
    AI Evaluator Engine (Judge)

    Responsibilities:
    - Analyze complete interview conversation
    - Score candidate on multiple dimensions
    - Make tier decision (S/A/B/C)
    - Generate structured evaluation report
    """

    def __init__(self, gemini_service: GeminiService):
        """
        Initialize evaluator engine

        Args:
            gemini_service: Gemini API service instance
        """
        self.gemini_service = gemini_service

    def evaluate(
        self,
        session: InterviewSession,
        timeout: float = None
    ) -> EvaluationResult:
        """
        Evaluate interview session with timeout and retry.

        Args:
            session: Completed interview session
            timeout: Timeout in seconds (defaults to Settings.EVALUATION_TIMEOUT)

        Returns:
            EvaluationResult with scores and decision
        """
        # Use settings timeout if not provided
        if timeout is None:
            timeout = float(Settings.EVALUATION_TIMEOUT)

        # Get chat history as text
        chat_history = session.get_chat_history_text()

        if not chat_history:
            raise ValueError("Cannot evaluate empty interview session")

        # Try evaluation with retries
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                result = self._evaluate_with_timeout(session, chat_history, timeout)
                return result
            except FuturesTimeoutError:
                logger.warning(f"Evaluation timeout on attempt {attempt + 1}")
                last_error = TimeoutError(f"评估超时 ({timeout}秒)")
            except GeminiAPIError as e:
                logger.warning(f"API error on attempt {attempt + 1}: {e}")
                last_error = e
                # Exponential backoff
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Evaluation error on attempt {attempt + 1}: {e}")
                last_error = e
                break  # Don't retry on unexpected errors

        # All retries failed - return fallback evaluation
        logger.error(f"Evaluation failed after {MAX_RETRIES + 1} attempts: {last_error}")
        return self._create_fallback_evaluation(session, str(last_error))

    def _evaluate_with_timeout(
        self,
        session: InterviewSession,
        chat_history: str,
        timeout: float
    ) -> EvaluationResult:
        """
        Run evaluation with timeout using thread pool.

        Note: ThreadPoolExecutor.result(timeout) only raises TimeoutError after
        the specified time, but the underlying thread continues running until
        completion. This means the actual wait time could exceed the timeout
        if the API call is slow. For truly interruptible timeouts, consider
        using asyncio or multiprocessing with Process.terminate().

        Args:
            session: Interview session
            chat_history: Chat history text
            timeout: Timeout in seconds

        Returns:
            EvaluationResult
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                self._do_evaluate,
                session,
                chat_history
            )
            return future.result(timeout=timeout)

    def _do_evaluate(
        self,
        session: InterviewSession,
        chat_history: str
    ) -> EvaluationResult:
        """
        Perform the actual evaluation.

        Args:
            session: Interview session
            chat_history: Chat history text

        Returns:
            EvaluationResult
        """
        # Build evaluation prompt
        prompt = f"""
请根据以下信息对候选人进行评估：

【岗位描述】
{session.job_description}

【面试对话记录】
{chat_history}

请严格按照评分标准进行评估，输出 JSON 格式的评估结果。
"""

        # Call Gemini Pro for evaluation
        result = self.gemini_service.generate(
            model_type="evaluator",
            contents=[{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            system_instruction=EVALUATOR_PROMPT,
            thinking_level=Settings.EVALUATOR_THINKING_LEVEL,
            response_mime_type="application/json",
            response_schema=EVALUATION_SCHEMA
        )

        # Parse JSON response
        try:
            data = json.loads(result["text"])
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from response
            data = self._extract_json(result["text"])
            if not data:
                raise ValueError(f"Failed to parse evaluation JSON: {e}")

        # Validate and adjust scores
        data = self._validate_scores(data)

        # Create EvaluationResult
        evaluation = EvaluationResult.from_json(data)

        # Update session with candidate name only if not already set by user
        if not session.candidate_name and evaluation.candidate_name != "Unknown":
            session.candidate_name = evaluation.candidate_name

        return evaluation

    def _create_fallback_evaluation(
        self,
        session: InterviewSession,
        error_message: str
    ) -> EvaluationResult:
        """
        Create a fallback evaluation when API fails.

        Args:
            session: Interview session
            error_message: Error description

        Returns:
            EvaluationResult marked for manual review
        """
        logger.info(f"Creating fallback evaluation due to: {error_message}")

        data = {
            "candidate_name": session.candidate_name or "Unknown",
            "total_score": 50,  # Neutral score
            "decision_tier": "B",  # Default to B - needs manual review
            "is_pass": True,  # Let HR decide
            "skill_match_score": 50,
            "communication_score": 50,
            "remote_readiness_score": 50,
            "key_strengths": ["需要人工复核"],
            "red_flags": [f"自动评估失败: {error_message}"],
            "summary": "由于系统原因，自动评估未能完成。建议 HR 人工查看面试记录进行评估。",
            "notification_text": "感谢您参加面试，HR 将在近期与您联系。"
        }

        return EvaluationResult.from_json(data)

    def _extract_json(self, text: str) -> Optional[dict]:
        """
        Try to extract JSON from text response

        Args:
            text: Raw response text

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

    def _validate_scores(self, data: dict) -> dict:
        """
        Validate and adjust scores to ensure consistency

        Args:
            data: Raw evaluation data

        Returns:
            Validated data
        """
        # Ensure total_score is within bounds
        total_score = data.get("total_score", 0)
        total_score = max(0, min(100, total_score))
        data["total_score"] = total_score

        # Determine tier based on score
        if total_score >= Settings.S_TIER_THRESHOLD:
            data["decision_tier"] = "S"
            data["is_pass"] = True
        elif total_score >= Settings.A_TIER_THRESHOLD:
            data["decision_tier"] = "A"
            data["is_pass"] = True
        elif total_score >= Settings.B_TIER_THRESHOLD:
            data["decision_tier"] = "B"
            data["is_pass"] = True
        else:
            data["decision_tier"] = "C"
            data["is_pass"] = False

        # Ensure required fields
        if "key_strengths" not in data or not data["key_strengths"]:
            data["key_strengths"] = ["待进一步评估"]

        if "red_flags" not in data:
            data["red_flags"] = []

        if "summary" not in data or not data["summary"]:
            data["summary"] = f"候选人综合得分 {total_score} 分，评级为 {data['decision_tier']} 级。"

        # Generate notification text based on tier (use configurable defaults only if not provided)
        if data["decision_tier"] == "S":
            if "notification_text" not in data or "感谢您的时间" in data.get("notification_text", ""):
                data["notification_text"] = Settings.S_TIER_DEFAULT_NOTIFICATION
        else:
            # Only set default if not provided or empty
            if "notification_text" not in data or not data.get("notification_text", "").strip():
                data["notification_text"] = Settings.DEFAULT_NOTIFICATION

        return data

    def create_test_mode_evaluation(
        self,
        session: InterviewSession
    ) -> EvaluationResult:
        """
        Create S-tier evaluation for test mode (/stop command)

        Args:
            session: Interview session

        Returns:
            EvaluationResult with S-tier rating
        """
        logger.info(f"Creating test mode S-tier evaluation for session {session.session_id}")

        data = {
            "candidate_name": session.candidate_name or "测试用户",
            "total_score": 95,
            "decision_tier": "S",
            "is_pass": True,
            "skill_match_score": 95,
            "communication_score": 95,
            "remote_readiness_score": 95,
            "key_strengths": [
                "【测试模式】自动生成的 S 级评估",
                "技术能力突出",
                "沟通表达清晰"
            ],
            "red_flags": [],
            "summary": "【测试模式】此评估由 /stop 指令触发，候选人被自动判定为 S 级人才。",
            "notification_text": Settings.S_TIER_DEFAULT_NOTIFICATION
        }

        return EvaluationResult.from_json(data)

    def create_notification(
        self,
        session: InterviewSession,
        evaluation: EvaluationResult,
        job_title: str = ""
    ) -> FeishuNotification:
        """
        Create Feishu notification from evaluation

        Args:
            session: Interview session
            evaluation: Evaluation result
            job_title: Job title for the position

        Returns:
            FeishuNotification ready to send
        """
        return FeishuNotification.from_evaluation(session, evaluation, job_title=job_title)


def create_evaluator(api_key: str = None) -> EvaluatorEngine:
    """
    Factory function to create evaluator

    Args:
        api_key: Optional Gemini API key

    Returns:
        EvaluatorEngine instance
    """
    gemini_service = GeminiService(api_key=api_key)
    return EvaluatorEngine(gemini_service)


def evaluate_interview(
    session: InterviewSession,
    api_key: str = None,
    job_title: str = ""
) -> tuple[EvaluationResult, FeishuNotification]:
    """
    Convenience function to evaluate interview and create notification

    Args:
        session: Completed interview session
        api_key: Optional Gemini API key
        job_title: Job title for the position

    Returns:
        Tuple of (EvaluationResult, FeishuNotification)
    """
    evaluator = create_evaluator(api_key)
    evaluation = evaluator.evaluate(session)
    notification = evaluator.create_notification(session, evaluation, job_title=job_title)

    return evaluation, notification
