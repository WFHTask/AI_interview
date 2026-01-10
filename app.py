"""
AI-HR Interview System - Main Application

Streamlit-based AI interview platform using Gemini 3.0 API.

Two views:
1. HR Admin View (default): Configure jobs, generate interview links
2. Candidate View (?job=xxx): Clean interview interface for candidates
"""
import streamlit as st
import time
from typing import Optional

# Page config must be first Streamlit command
st.set_page_config(
    page_title="VoiVerse AI 面试",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components and services
from components.styles import MAIN_CSS
from components.admin_dashboard import render_admin_dashboard, init_admin_dashboard_state
from components.chat_ui import (
    render_chat_header,
    render_welcome_screen,
    render_chat_messages,
    render_interview_ended_message,
    render_thinking_indicator,
    init_chat_state,
    add_message_to_state,
    clear_chat_state
)
from components.result_card import (
    render_evaluation_result,
    render_loading_evaluation,
    render_evaluation_error,
    render_interview_ended_safe,
    render_s_tier_result_safe
)
from components.candidate_view import (
    render_candidate_header,
    render_candidate_welcome,
    render_candidate_chat_header,
    render_interview_complete_message,
    render_invalid_link,
    render_candidate_footer
)
from components.detail_view import render_detail_view

from config.settings import Settings
from models.schemas import InterviewSession, MessageRole, SessionStatus, CandidateSafeConfig
from core.interviewer import InterviewerEngine, create_interviewer, restore_interviewer
from core.evaluator import evaluate_interview, create_evaluator
from services.gemini_service import GeminiService
from services.feishu_service import send_interview_result
from services.storage_service import save_interview_complete, storage_service
from services.job_config_service import get_job_config, job_config_service
from services.company_config_service import get_company_background
from services.auth_service import verify_login, check_session, logout, is_auth_required
from utils.rate_limiter import check_interview_rate_limit
from utils.validators import validate_user_input
from components.login_form import (
    render_login_page,
    render_logout_button,
    init_auth_state,
    set_auth_state,
    clear_auth_state,
    is_authenticated
)


def get_view_mode() -> tuple[str, Optional[str]]:
    """
    Determine view mode from URL parameters

    Returns:
        Tuple of (mode, param_id)
        mode: 'admin', 'candidate', or 'detail'
        param_id: Config ID (candidate) or Session ID (detail)
    """
    query_params = st.query_params

    # Check for job parameter (candidate view)
    job_id = query_params.get("job")
    if job_id:
        return ("candidate", job_id)

    # Check for session parameter (detail view)
    session_id = query_params.get("session")
    if session_id:
        return ("detail", session_id)

    # Default to admin view
    return ("admin", None)


def init_session_state():
    """Initialize all session state variables"""
    init_admin_dashboard_state()
    init_chat_state()
    init_auth_state()

    # Interview engine state
    if "interviewer_engine" not in st.session_state:
        st.session_state.interviewer_engine = None

    if "interview_session" not in st.session_state:
        st.session_state.interview_session = None

    if "is_evaluating" not in st.session_state:
        st.session_state.is_evaluating = False

    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False

    # Candidate view state
    if "candidate_name" not in st.session_state:
        st.session_state.candidate_name = ""

    if "candidate_email" not in st.session_state:
        st.session_state.candidate_email = ""


def start_interview_for_candidate(
    job_config,
    candidate_name: str,
    candidate_email: str,
    candidate_resume: str = ""
):
    """Start interview for a candidate"""
    try:
        # Validate API key
        if not Settings.GEMINI_API_KEY:
            st.error("系统配置错误，请联系管理员")
            return

        # Increment interview count
        job_config_service.increment_interview_count(job_config.config_id)

        # Get company background
        company_background = get_company_background()

        # Create interviewer and session
        engine, session = create_interviewer(
            job_description=job_config.job_description,
            s_tier_invitation=job_config.s_tier_invitation,
            s_tier_link=job_config.s_tier_link,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_resume=candidate_resume,
            custom_greeting=job_config.custom_greeting,
            company_background=company_background,
            test_mode=job_config.test_mode
        )

        # Save resume file if uploaded
        resume_file_data = st.session_state.get("resume_file_data")
        resume_file_name = st.session_state.get("resume_file_name")
        if resume_file_data and resume_file_name:
            try:
                file_path = storage_service.save_resume_file(
                    session_id=session.session_id,
                    file_data=resume_file_data,
                    original_filename=resume_file_name
                )
                session.resume_file_path = file_path
            except Exception as e:
                import logging
                logging.warning(f"Failed to save resume file: {e}")

        # SECURITY: Store engine and session (needed for interview logic)
        # These are Python objects, not directly exposed to browser JS
        st.session_state.interviewer_engine = engine
        st.session_state.interview_session = session
        st.session_state.interview_started = True
        st.session_state.interview_ended = False
        st.session_state.messages = []
        st.session_state.candidate_name = candidate_name
        st.session_state.candidate_email = candidate_email

        # Clear resume session state after interview starts
        if "parsed_resume" in st.session_state:
            del st.session_state.parsed_resume
        if "resume_summary" in st.session_state:
            del st.session_state.resume_summary
        if "resume_file_data" in st.session_state:
            del st.session_state.resume_file_data
        if "resume_file_name" in st.session_state:
            del st.session_state.resume_file_name

        # SECURITY: Store only safe subset of job config for candidate view
        # Full config is only used internally, not exposed
        st.session_state.candidate_safe_config = CandidateSafeConfig.from_job_config(job_config)

        # Store full config separately for internal use (evaluation, feishu)
        # This is a Python object reference, not serialized to frontend
        st.session_state._internal_job_config = job_config

        # Generate initial greeting
        with st.spinner("AI 面试官准备中..."):
            greeting = ""
            for chunk in engine.start_interview():
                greeting += chunk

            add_message_to_state("assistant", greeting)

        st.session_state.turn_count = session.turn_count

        # Save session progress to storage for page refresh recovery
        save_interview_progress()

        # Add session ID to URL for page refresh recovery (pure Python, no JS needed)
        # This modifies URL from ?job=xxx to ?job=xxx&session=yyy
        st.query_params["session"] = session.session_id

        st.rerun()

    except Exception as e:
        st.error("启动面试失败，请刷新页面重试")

        import logging
        logging.error(f"Interview start failed: {e}", exc_info=True)


def process_user_input(user_input: str):
    """Process user input and generate AI response"""
    engine: InterviewerEngine = st.session_state.interviewer_engine
    session: InterviewSession = st.session_state.interview_session

    if not engine or not session:
        return

    # Input validation and sanitization
    is_valid, sanitized_input, error_msg = validate_user_input(user_input)
    if not is_valid:
        st.warning(error_msg)
        return

    # Use sanitized input
    user_input = sanitized_input

    # Rate limiting check
    is_allowed, error_msg = check_interview_rate_limit(session.session_id)
    if not is_allowed:
        st.warning(error_msg)
        return

    # Add user message to display
    add_message_to_state("user", user_input)

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Mark as processing
    st.session_state.is_processing = True

    try:
        full_response = ""

        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("**AI 正在评估您的回答...**")

            message_placeholder = st.empty()

            for chunk in engine.chat(user_input):
                if not full_response:
                    thinking_placeholder.empty()

                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.01)

            message_placeholder.markdown(full_response)

        add_message_to_state("assistant", full_response)
        st.session_state.turn_count = session.turn_count
        st.session_state.is_processing = False

        # Save progress after each message exchange
        save_interview_progress()

        if engine.should_evaluate:
            st.session_state.interview_ended = True
            trigger_evaluation()

    except Exception as e:
        st.session_state.is_processing = False
        st.error("生成回复时出现问题，请重试")

        if st.button("重试", key="retry_response"):
            st.rerun()

        import logging
        logging.error(f"Response generation failed: {e}", exc_info=True)


def trigger_evaluation():
    """Trigger evaluation after interview ends"""
    st.session_state.is_evaluating = True
    st.rerun()


def run_evaluation():
    """Run the evaluation process"""
    session: InterviewSession = st.session_state.interview_session
    engine: InterviewerEngine = st.session_state.interviewer_engine

    if not session:
        return

    try:
        render_loading_evaluation()

        with st.spinner("AI 判官正在评估..."):
            # Get job config from internal storage (not exposed to candidate)
            job_config = st.session_state.get("_internal_job_config")
            job_title = job_config.job_title if job_config else ""

            # Check if test mode was triggered
            if engine and engine.test_mode_triggered:
                # Use test mode S-tier evaluation
                evaluator = create_evaluator()
                evaluation = evaluator.create_test_mode_evaluation(session)
                notification = evaluator.create_notification(session, evaluation, job_title=job_title)
            else:
                # Normal evaluation
                evaluation, notification = evaluate_interview(session, job_title=job_title)

            # Save to storage (full evaluation saved to file only)
            try:
                save_interview_complete(session, evaluation)
            except Exception as e:
                st.warning(f"保存面试记录失败: {e}")

            # Send Feishu notification
            try:
                # Get webhook from internal job config (not exposed to candidate)
                webhook_url = job_config.feishu_webhook if job_config else ""

                if webhook_url:
                    send_interview_result(notification, webhook_url)
            except Exception as e:
                st.warning(f"发送飞书通知失败: {e}")

            # SECURITY: Only store completion flag and session ID
            # Evaluation result is read from file storage when needed
            st.session_state.evaluation_complete = True
            st.session_state._completed_session_id = session.session_id

            st.session_state.is_evaluating = False

            st.rerun()

    except Exception as e:
        st.session_state.is_evaluating = False
        render_evaluation_error(str(e))


def display_chat_history():
    """Display chat message history"""
    if not st.session_state.messages:
        return

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        with st.chat_message(role):
            st.markdown(content)


def reset_interview():
    """Reset interview state"""
    clear_chat_state()
    st.session_state.interviewer_engine = None
    st.session_state.interview_session = None
    st.session_state.turn_count = 0
    st.session_state.is_evaluating = False

    # Clear evaluation state (only completion flag and session ID stored)
    st.session_state.evaluation_complete = False
    st.session_state._completed_session_id = None

    # Clear config references
    st.session_state.candidate_safe_config = None
    st.session_state._internal_job_config = None

    st.rerun()


def save_interview_progress():
    """Save current interview progress to storage for page refresh recovery"""
    session = st.session_state.get("interview_session")
    if session:
        try:
            storage_service.save_session(session)
        except Exception as e:
            import logging
            logging.warning(f"Failed to save interview progress: {e}")


def try_restore_session_from_url(job_config_id: str, session_id: str, job_config) -> bool:
    """
    Try to restore interview session from URL parameter.

    This is called when page is refreshed and URL contains session ID.
    URL format: ?job=xxx&session=yyy

    Args:
        job_config_id: The job config ID from URL
        session_id: The session ID from URL
        job_config: Already loaded job config

    Returns:
        True if session was restored, False otherwise
    """
    if not session_id:
        return False

    import logging
    logging.info(f"Attempting to restore session: {session_id[:12]}...")

    # Try to find session in storage (use first 12 chars as prefix)
    result = storage_service.find_session_by_prefix(session_id[:12])

    if result:
        session, evaluation = result

        # Only restore if session is still in progress
        if session and session.status == SessionStatus.IN_PROGRESS:
            # Get company background
            company_background = get_company_background()

            # Restore the interviewer engine
            engine = restore_interviewer(
                session=session,
                custom_greeting=job_config.custom_greeting,
                company_background=company_background,
                test_mode=job_config.test_mode
            )

            # Restore session state
            st.session_state.interviewer_engine = engine
            st.session_state.interview_session = session
            st.session_state.interview_started = True
            st.session_state.interview_ended = engine.is_ended
            st.session_state.candidate_name = session.candidate_name or ""
            st.session_state.candidate_email = session.candidate_email or ""
            st.session_state.turn_count = session.turn_count

            # Restore messages to chat display
            st.session_state.messages = []
            for msg in session.chat_history:
                role = "assistant" if msg.role == MessageRole.MODEL else "user"
                add_message_to_state(role, msg.content)

            # Store config references
            st.session_state.candidate_safe_config = CandidateSafeConfig.from_job_config(job_config)
            st.session_state._internal_job_config = job_config

            logging.info(f"Session restored successfully: {session_id[:12]}...")
            return True
        else:
            logging.warning(f"Session not in progress, cannot restore: {session_id[:12]}...")
    else:
        logging.warning(f"Session not found in storage: {session_id[:12]}...")

    # If restore failed, remove session param from URL to show welcome screen
    if "session" in st.query_params:
        del st.query_params["session"]

    return False


# =============================================================================
# AUTHENTICATION
# =============================================================================

def handle_login(username: str, password: str) -> bool:
    """
    Handle login attempt.

    Args:
        username: Provided username
        password: Provided password

    Returns:
        True if login successful
    """
    token = verify_login(username, password)
    if token:
        set_auth_state(token, username)
        return True
    return False


def handle_logout():
    """Handle logout"""
    token = st.session_state.get("auth_token")
    if token:
        logout(token)
    clear_auth_state()
    st.rerun()


# =============================================================================
# ADMIN VIEW
# =============================================================================

def render_admin_view():
    """Render HR admin view - Modern Tab-based Dashboard"""
    # Hide sidebar for admin view (using new dashboard layout)
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Check authentication if enabled
    if is_auth_required():
        if not is_authenticated():
            render_login_page(handle_login)
            return

        token = st.session_state.get("auth_token")
        if not check_session(token):
            clear_auth_state()
            render_login_page(handle_login)
            return

    # Render new dashboard layout
    render_admin_dashboard()


# =============================================================================
# CANDIDATE VIEW
# =============================================================================

def render_candidate_view(job_config_id: str):
    """Render candidate interview view"""
    # Hide sidebar completely for candidate view (including toggle button)
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Load job config
    job_config = get_job_config(job_config_id)

    if not job_config or not job_config.is_valid():
        render_invalid_link()
        return

    # SECURITY: Create safe config for candidate view (excludes sensitive fields)
    safe_config = CandidateSafeConfig.from_job_config(job_config)

    # Check for session restore from URL parameter (on page refresh)
    # URL format: ?job=xxx&session=yyy
    is_started = st.session_state.get("interview_started", False)
    query_params = st.query_params
    session_id_from_url = query_params.get("session")

    # Try to restore session if not started but URL has session ID
    if not is_started and session_id_from_url:
        if try_restore_session_from_url(job_config_id, session_id_from_url, job_config):
            st.rerun()
            return

    # Get interview state
    is_started = st.session_state.get("interview_started", False)
    is_ended = st.session_state.get("interview_ended", False)
    is_evaluating = st.session_state.get("is_evaluating", False)

    # State machine
    if not is_started:
        # Welcome screen with candidate info collection
        # Pass full job_config only for start_interview (needs JD, greeting, etc.)
        render_candidate_header(safe_config.job_title)

        def on_start(name: str, email: str, resume_summary: str = ""):
            start_interview_for_candidate(job_config, name, email, resume_summary)

        render_candidate_welcome(job_config, on_start)

    elif is_evaluating:
        render_candidate_header(safe_config.job_title)
        display_chat_history()
        run_evaluation()

    elif is_ended and st.session_state.get("evaluation_complete"):
        # SECURITY: Read evaluation from file storage (backend only)
        # No evaluation data stored in session_state
        render_candidate_header(safe_config.job_title)
        display_chat_history()

        # Get completed session ID and load evaluation from file
        completed_session_id = st.session_state.get("_completed_session_id", "")

        if completed_session_id:
            # Load evaluation from backend file storage
            result = storage_service.find_session_by_prefix(completed_session_id[:8])

            if result:
                _, evaluation = result

                if evaluation and evaluation.is_s_tier:
                    # S-tier: Show celebration (read from backend)
                    render_s_tier_result_safe(
                        notification_text=evaluation.notification_text,
                        invitation=safe_config.s_tier_invitation,
                        link=safe_config.s_tier_link
                    )
                else:
                    # Non-S tier: Show simple end message
                    notification_text = evaluation.notification_text if evaluation else ""
                    render_interview_ended_safe(notification_text=notification_text)
            else:
                # Fallback if file not found
                render_interview_ended_safe()
        else:
            render_interview_ended_safe()

    else:
        # Active interview - use safe_config from session for ongoing interview
        active_config = st.session_state.get("candidate_safe_config", safe_config)

        render_candidate_chat_header(
            job_title=active_config.job_title,
            turn_count=st.session_state.get("turn_count", 0),
            max_turns=Settings.MAX_INTERVIEW_TURNS,
            test_mode=active_config.test_mode
        )

        display_chat_history()

        is_processing = st.session_state.get("is_processing", False)

        if is_ended:
            render_interview_complete_message()
            st.chat_input(placeholder="面试已结束", disabled=True)
        else:
            # Different placeholder for test mode vs normal mode
            if active_config.test_mode:
                placeholder_text = "AI 正在评估您的回答..." if is_processing else "测试模式：输入 /stop 结束面试"
            else:
                placeholder_text = "AI 正在评估您的回答..." if is_processing else "仅支持语音输入 - 请用豆包输入法长按说话"
            user_input = st.chat_input(
                placeholder=placeholder_text,
                disabled=is_processing,
                max_chars=5000  # Match validator MAX_INPUT_LENGTH
            )

            if user_input and not is_processing:
                process_user_input(user_input)

    render_candidate_footer()


# =============================================================================
# MAIN
# =============================================================================

def render_interview_detail(session_id: str):
    """Render interview detail view for HR review"""
    # Hide sidebar for detail view
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Find session by prefix
    result = storage_service.find_session_by_prefix(session_id)

    if result:
        session, evaluation = result
        render_detail_view(session, evaluation, session_id)
    else:
        render_detail_view(None, None, session_id)


def main():
    """Main application entry point"""
    # Apply custom CSS
    st.markdown(MAIN_CSS, unsafe_allow_html=True)

    # Initialize session state
    init_session_state()

    # Determine view mode
    mode, param_id = get_view_mode()

    if mode == "candidate" and param_id:
        # Candidate interview view
        render_candidate_view(param_id)
    elif mode == "detail" and param_id:
        # Interview detail view (for HR review from Feishu)
        render_interview_detail(param_id)
    else:
        # HR admin view
        render_admin_view()


if __name__ == "__main__":
    main()
