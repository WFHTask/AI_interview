"""
Interviewer Engine - AI Interview Conductor

Uses Gemini 3.0 Flash for low-latency, multi-turn conversation.
Manages interview flow, STAR questioning, and termination detection.
"""
from typing import Generator, Optional, Callable
from datetime import datetime

from services.gemini_service import GeminiService, ConversationManager
from models.schemas import InterviewSession, MessageRole, SessionStatus
from config.settings import Settings
from core.prompts import (
    format_interviewer_prompt,
    should_terminate,
    STANDARD_RESPONSES
)


class InterviewerEngine:
    """
    AI Interviewer Engine

    Responsibilities:
    - Conduct interview conversation
    - Apply STAR methodology for deep questioning
    - Detect interview termination signals
    - Manage conversation state and history
    """

    def __init__(
        self,
        gemini_service: GeminiService,
        session: InterviewSession,
        custom_greeting: str = "",
        company_background: str = "",
        test_mode: bool = False
    ):
        """
        Initialize interviewer engine

        Args:
            gemini_service: Gemini API service instance
            session: Interview session data
            custom_greeting: Custom greeting for this interview
            company_background: Company background information
            test_mode: Enable test mode (/stop triggers S-tier result)
        """
        self.gemini_service = gemini_service
        self.session = session
        self.conversation = ConversationManager(gemini_service)
        self.custom_greeting = custom_greeting
        self.company_background = company_background
        self.test_mode = test_mode

        # Interview state
        self.is_started = False
        self.is_ended = False
        self.test_mode_triggered = False  # Flag for /stop command

    def _get_system_prompt(self) -> str:
        """Get formatted system prompt with current state"""
        return format_interviewer_prompt(
            job_description=self.session.job_description,
            turn_count=self.session.turn_count,
            max_turns=Settings.MAX_INTERVIEW_TURNS,
            custom_greeting=self.custom_greeting,
            candidate_name=self.session.candidate_name or "",
            candidate_email=self.session.candidate_email or "",
            candidate_resume=self.session.candidate_resume or "",
            company_background=self.company_background
        )

    def start_interview(self) -> Generator[str, None, str]:
        """
        Start interview with initial greeting

        Yields:
            str: Greeting text chunks

        Returns:
            str: Full greeting message
        """
        if self.is_started:
            raise RuntimeError("Interview already started")

        self.is_started = True
        self.session.status = SessionStatus.IN_PROGRESS

        # Generate initial greeting using direct API call (not conversation manager)
        # This avoids adding "请开始面试" to conversation history
        full_response = ""

        for chunk, signature in self.gemini_service.stream_generate(
            model_type="interviewer",
            contents=[{"role": "user", "parts": [{"text": "请开始面试"}]}],
            system_instruction=self._get_system_prompt(),
            thinking_level=Settings.INTERVIEWER_THINKING_LEVEL
        ):
            if chunk:
                full_response += chunk
                yield chunk
            if signature:
                self.session.thought_signature = signature

        # Initialize conversation history with only the greeting
        # Don't include the trigger message "请开始面试"
        self.conversation.add_model_message(full_response)
        self.conversation.thought_signature = self.session.thought_signature

        # Save to session
        self.session.add_message(MessageRole.MODEL, full_response)

        return full_response

    def chat(
        self,
        user_message: str,
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> Generator[str, None, str]:
        """
        Process user message and generate response

        Args:
            user_message: Candidate's response
            on_chunk: Optional callback for each chunk

        Yields:
            str: Response text chunks

        Returns:
            str: Full response message
        """
        if not self.is_started:
            raise RuntimeError("Interview not started. Call start_interview() first.")

        if self.is_ended:
            yield STANDARD_RESPONSES["interview_end_normal"]
            return STANDARD_RESPONSES["interview_end_normal"]

        # Check for /stop command in test mode
        if self.test_mode and user_message.strip().lower() == "/stop":
            # Save user message before ending (for evaluation)
            self.session.add_message(MessageRole.USER, user_message)
            self.is_ended = True
            self.test_mode_triggered = True
            self.session.end_session(SessionStatus.COMPLETED)
            end_msg = "【测试模式】面试已结束，系统正在生成 S 级评估结果..."
            yield end_msg
            return end_msg

        # Save user message to session first (for evaluation later)
        self.session.add_message(MessageRole.USER, user_message)

        # Check turn limit after saving user message
        if self.session.turn_count >= Settings.MAX_INTERVIEW_TURNS:
            self.is_ended = True
            self.session.end_session(SessionStatus.COMPLETED)
            end_msg = "感谢您的时间，我已经了解了您的基本情况。请稍等，系统正在生成评估结果..."
            yield end_msg
            return end_msg

        # Restore thought signature for multi-turn
        self.conversation.thought_signature = self.session.thought_signature

        # Add user message to conversation history
        self.conversation.add_user_message(user_message)

        # Generate response using direct stream (avoid double-adding in stream_chat)
        full_response = ""

        for chunk, signature in self.gemini_service.stream_generate(
            model_type="interviewer",
            contents=self.conversation.history,
            system_instruction=self._get_system_prompt(),
            thinking_level=Settings.INTERVIEWER_THINKING_LEVEL,
            thought_signature=self.conversation.thought_signature
        ):
            if chunk:
                full_response += chunk
                yield chunk
                if on_chunk:
                    on_chunk(chunk)
            if signature:
                self.conversation.thought_signature = signature

        # Save response to conversation history
        self.conversation.add_model_message(full_response)

        # Save response to session
        self.session.add_message(MessageRole.MODEL, full_response)
        self.session.thought_signature = self.conversation.thought_signature

        # Check for termination
        if should_terminate(full_response):
            self.is_ended = True
            self.session.end_session(SessionStatus.COMPLETED)

        return full_response

    def force_end(self, reason: str = "manual") -> str:
        """
        Force end interview

        Args:
            reason: Reason for ending

        Returns:
            str: End message
        """
        self.is_ended = True
        self.session.end_session(SessionStatus.TERMINATED)

        if reason == "security":
            return STANDARD_RESPONSES["security_response"]

        return STANDARD_RESPONSES["interview_end_normal"]

    def get_chat_history_for_evaluation(self) -> str:
        """
        Get formatted chat history for evaluation

        Returns:
            str: Formatted conversation text
        """
        return self.session.get_chat_history_text()

    @property
    def can_continue(self) -> bool:
        """Check if interview can continue"""
        return (
            self.is_started and
            not self.is_ended and
            self.session.turn_count < Settings.MAX_INTERVIEW_TURNS
        )

    @property
    def should_evaluate(self) -> bool:
        """Check if interview should be evaluated"""
        return self.is_ended and self.session.status in [
            SessionStatus.COMPLETED,
            SessionStatus.TERMINATED
        ]


def create_interviewer(
    job_description: str,
    s_tier_invitation: str = "",
    s_tier_link: str = "",
    candidate_name: str = "",
    candidate_email: str = "",
    candidate_resume: str = "",
    custom_greeting: str = "",
    company_background: str = "",
    test_mode: bool = False,
    api_key: str = None
) -> tuple[InterviewerEngine, InterviewSession]:
    """
    Factory function to create interviewer with new session

    Args:
        job_description: Job description text
        s_tier_invitation: S-tier invitation text
        s_tier_link: S-tier booking link
        candidate_name: Candidate name (optional)
        candidate_email: Candidate email (optional)
        candidate_resume: Candidate resume summary (optional)
        custom_greeting: Custom interviewer greeting (optional)
        company_background: Company background information (optional)
        test_mode: Enable test mode (/stop triggers S-tier result)
        api_key: Optional Gemini API key

    Returns:
        Tuple of (InterviewerEngine, InterviewSession)
    """
    # Create session
    session = InterviewSession(
        job_description=job_description,
        s_tier_invitation=s_tier_invitation,
        s_tier_link=s_tier_link,
        candidate_name=candidate_name or None,
        candidate_email=candidate_email or None,
        candidate_resume=candidate_resume or None
    )

    # Create Gemini service
    gemini_service = GeminiService(api_key=api_key)

    # Create interviewer engine
    engine = InterviewerEngine(
        gemini_service=gemini_service,
        session=session,
        custom_greeting=custom_greeting,
        company_background=company_background,
        test_mode=test_mode
    )

    return engine, session


def restore_interviewer(
    session: InterviewSession,
    custom_greeting: str = "",
    company_background: str = "",
    test_mode: bool = False,
    api_key: str = None
) -> InterviewerEngine:
    """
    Restore interviewer engine from existing session

    Args:
        session: Existing InterviewSession with conversation history
        custom_greeting: Custom interviewer greeting (optional)
        company_background: Company background information (optional)
        test_mode: Enable test mode
        api_key: Optional Gemini API key

    Returns:
        InterviewerEngine with restored state
    """
    # Create Gemini service
    gemini_service = GeminiService(api_key=api_key)

    # Create interviewer engine
    engine = InterviewerEngine(
        gemini_service=gemini_service,
        session=session,
        custom_greeting=custom_greeting,
        company_background=company_background,
        test_mode=test_mode
    )

    # Restore state flags
    engine.is_started = True
    engine.is_ended = session.status in [SessionStatus.COMPLETED, SessionStatus.TERMINATED]

    # Restore conversation history from session messages
    for msg in session.messages:
        if msg.role == MessageRole.USER:
            engine.conversation.add_user_message(msg.content)
        elif msg.role == MessageRole.MODEL:
            engine.conversation.add_model_message(msg.content)

    # Restore thought signature if available
    if session.thought_signature:
        engine.conversation.thought_signature = session.thought_signature

    return engine
