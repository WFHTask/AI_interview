"""
Data models for AI-HR Interview System
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class CompanyConfig(BaseModel):
    """公司信息配置"""
    company_background: str = ""  # 公司背景及招聘目标（必填）
    updated_at: datetime = Field(default_factory=datetime.now)


class SessionStatus(str, Enum):
    """Interview session status"""
    PENDING = "pending"           # Waiting to start
    IN_PROGRESS = "in_progress"   # Interview ongoing
    COMPLETED = "completed"       # Interview finished normally
    TERMINATED = "terminated"     # Interview ended early (by AI or error)


class DecisionTier(str, Enum):
    """Candidate decision tier"""
    S = "S"  # >= 90: Exceptional, direct hire
    A = "A"  # 80-89: Excellent, proceed to next round
    B = "B"  # 60-79: Acceptable, backup candidate
    C = "C"  # < 60: Rejected


class MessageRole(str, Enum):
    """Chat message role"""
    USER = "user"
    MODEL = "model"
    SYSTEM = "system"


class Message(BaseModel):
    """Single chat message"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_gemini_format(self) -> Dict[str, Any]:
        """
        Convert to Gemini API format.

        Note: Gemini API doesn't support a dedicated 'system' role in contents.
        System instructions should be passed via the systemInstruction parameter.
        If MessageRole.SYSTEM appears here, it's converted to 'user' as a fallback,
        though this should ideally be handled at the API call level.
        """
        return {
            "role": self.role.value if self.role != MessageRole.SYSTEM else "user",
            "parts": [{"text": self.content}]
        }


class InterviewSession(BaseModel):
    """Interview session data model"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Job configuration
    job_description: str
    s_tier_invitation: str = ""  # S级邀请文案
    s_tier_link: str = ""        # S级预约链接

    # Candidate info
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_phone: Optional[str] = None
    candidate_wechat: Optional[str] = None
    candidate_resume: Optional[str] = None
    candidate_info: Optional[Dict[str, Any]] = None
    resume_file_path: Optional[str] = None  # Path to uploaded resume file (for HR review)

    # Conversation
    chat_history: List[Message] = Field(default_factory=list)
    thought_signature: Optional[str] = None  # Gemini 3.0 Thought Signature

    # Session state
    status: SessionStatus = SessionStatus.PENDING
    turn_count: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None

    def add_message(self, role: MessageRole, content: str) -> None:
        """Add a message to chat history"""
        self.chat_history.append(Message(role=role, content=content))
        if role == MessageRole.USER:
            self.turn_count += 1
        self.updated_at = datetime.now()

    @property
    def messages(self) -> List[Message]:
        """Alias for chat_history for backward compatibility"""
        return self.chat_history

    def get_gemini_contents(self) -> List[Dict[str, Any]]:
        """Get chat history in Gemini API format"""
        return [msg.to_gemini_format() for msg in self.chat_history]

    def get_chat_history_text(self) -> str:
        """Get chat history as plain text for evaluation"""
        lines = []
        for msg in self.chat_history:
            role_label = "面试官" if msg.role == MessageRole.MODEL else "候选人"
            lines.append(f"{role_label}: {msg.content}")
        return "\n\n".join(lines)

    def end_session(self, status: SessionStatus = SessionStatus.COMPLETED) -> None:
        """Mark session as ended"""
        self.status = status
        self.ended_at = datetime.now()
        self.updated_at = datetime.now()


class EvaluationResult(BaseModel):
    """Evaluation result from Judge AI"""
    candidate_name: str = "Unknown"
    total_score: int = Field(ge=0, le=100)
    decision_tier: DecisionTier
    is_pass: bool

    # Detailed scores
    skill_match_score: Optional[int] = Field(default=None, ge=0, le=100)
    communication_score: Optional[int] = Field(default=None, ge=0, le=100)
    remote_readiness_score: Optional[int] = Field(default=None, ge=0, le=100)

    # Analysis
    key_strengths: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    summary: str
    notification_text: str

    # Metadata
    evaluated_at: datetime = Field(default_factory=datetime.now)
    raw_response: Optional[Dict[str, Any]] = None

    @property
    def is_s_tier(self) -> bool:
        """Check if candidate is S-tier"""
        return self.decision_tier == DecisionTier.S

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "EvaluationResult":
        """Create from JSON response"""
        # Map tier string to enum
        tier_str = data.get("decision_tier", "C")
        tier = DecisionTier(tier_str) if tier_str in ["S", "A", "B", "C"] else DecisionTier.C

        return cls(
            candidate_name=data.get("candidate_name", "Unknown"),
            total_score=data.get("total_score", 0),
            decision_tier=tier,
            is_pass=data.get("is_pass", False),
            skill_match_score=data.get("skill_match_score"),
            communication_score=data.get("communication_score"),
            remote_readiness_score=data.get("remote_readiness_score"),
            key_strengths=data.get("key_strengths", []),
            red_flags=data.get("red_flags", []),
            summary=data.get("summary", ""),
            notification_text=data.get("notification_text", ""),
            raw_response=data
        )


class FeishuNotification(BaseModel):
    """Feishu notification data"""
    session_id: str
    candidate_name: str
    candidate_email: str = ""
    job_title: str = ""
    decision_tier: DecisionTier
    total_score: int
    summary: str
    key_strengths: List[str]
    red_flags: List[str]
    chat_history_text: str
    detail_url: str = ""  # URL to view full interview details
    is_urgent: bool = False  # True for S-tier

    @classmethod
    def from_evaluation(
        cls,
        session: InterviewSession,
        evaluation: EvaluationResult,
        job_title: str = "",
        base_url: str = ""
    ) -> "FeishuNotification":
        """Create from session and evaluation result"""
        import os
        # Generate detail URL (use ?session= format compatible with Streamlit routing)
        if not base_url:
            base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")
        # Remove trailing slash if present
        base_url = base_url.rstrip("/")
        detail_url = f"{base_url}/?session={session.session_id[:8]}"

        return cls(
            session_id=session.session_id,
            candidate_name=evaluation.candidate_name,
            candidate_email=session.candidate_email or "",
            job_title=job_title,
            decision_tier=evaluation.decision_tier,
            total_score=evaluation.total_score,
            summary=evaluation.summary,
            key_strengths=evaluation.key_strengths,
            red_flags=evaluation.red_flags,
            chat_history_text=session.get_chat_history_text(),
            detail_url=detail_url,
            is_urgent=evaluation.is_s_tier
        )


class CandidateSafeConfig(BaseModel):
    """
    SECURITY: Safe subset of job config for candidate view.

    Only contains information the candidate needs to see.
    Excludes: feishu_webhook and other internal settings.

    Note: test_mode is included as it's needed for UI logic (keyboard input toggle)
    but is not considered sensitive information.
    """
    config_id: str
    job_title: str = ""
    # S-tier info only shown after evaluation if candidate is S-tier
    s_tier_invitation: str = ""
    s_tier_link: str = ""
    # test_mode is needed for UI logic (allow keyboard input for /stop command)
    test_mode: bool = False

    @classmethod
    def from_job_config(cls, job_config) -> "CandidateSafeConfig":
        """Create safe config from full JobConfig"""
        return cls(
            config_id=job_config.config_id,
            job_title=job_config.job_title,
            s_tier_invitation=job_config.s_tier_invitation,
            s_tier_link=job_config.s_tier_link,
            test_mode=job_config.test_mode
        )
