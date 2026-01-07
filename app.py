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
from components.sidebar import render_admin_sidebar, init_admin_sidebar_state
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
    render_evaluation_error
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
from models.schemas import InterviewSession, MessageRole, SessionStatus
from core.interviewer import InterviewerEngine, create_interviewer
from core.evaluator import evaluate_interview
from services.gemini_service import GeminiService
from services.feishu_service import send_interview_result
from services.storage_service import save_interview_complete, storage_service
from services.job_config_service import get_job_config, job_config_service
from services.auth_service import verify_login, check_session, logout, is_auth_required
from utils.rate_limiter import check_interview_rate_limit
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
    init_admin_sidebar_state()
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

        # Create interviewer and session
        engine, session = create_interviewer(
            job_description=job_config.job_description,
            s_tier_invitation=job_config.s_tier_invitation,
            s_tier_link=job_config.s_tier_link,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_resume=candidate_resume,
            custom_greeting=job_config.custom_greeting
        )

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

        # Store job config for later use (feishu notification)
        st.session_state.current_job_config = job_config

        # Generate initial greeting
        with st.spinner("AI 面试官准备中..."):
            greeting = ""
            for chunk in engine.start_interview():
                greeting += chunk

            add_message_to_state("assistant", greeting)

        st.session_state.turn_count = session.turn_count
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

    # Rate limiting check
    is_allowed, error_msg = check_interview_rate_limit(session.session_id)
    if not is_allowed:
        st.warning(error_msg)
        return

    # Add user message to display
    add_message_to_state("user", user_input)

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

    if not session:
        return

    try:
        render_loading_evaluation()

        with st.spinner("AI 判官正在评估..."):
            # Get job title from config
            job_config = st.session_state.get("current_job_config")
            job_title = job_config.job_title if job_config else ""

            evaluation, notification = evaluate_interview(session, job_title=job_title)

            # Save to storage
            try:
                save_interview_complete(session, evaluation)
            except Exception as e:
                st.warning(f"保存面试记录失败: {e}")

            # Send Feishu notification
            try:
                # Get webhook from job config if available
                job_config = st.session_state.get("current_job_config")
                webhook_url = job_config.feishu_webhook if job_config else ""

                if webhook_url:
                    send_interview_result(notification, webhook_url)
            except Exception as e:
                st.warning(f"发送飞书通知失败: {e}")

            st.session_state.evaluation_result = evaluation
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
    st.session_state.evaluation_result = None
    st.rerun()


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
    """Render HR admin view"""
    # Check authentication if enabled
    if is_auth_required():
        if not is_authenticated():
            # Show login page
            render_login_page(handle_login)
            return

        # Validate session token
        token = st.session_state.get("auth_token")
        if not check_session(token):
            clear_auth_state()
            render_login_page(handle_login)
            return

    # Render sidebar
    config = render_admin_sidebar()

    # Add logout button if authenticated
    if is_auth_required() and is_authenticated():
        with st.sidebar:
            st.divider()
            if render_logout_button():
                handle_logout()

    # Main content - Admin dashboard
    render_chat_header(title="HR 管理后台", subtitle="配置岗位并生成面试链接")

    # Welcome/instruction content
    if not st.session_state.get("generated_url"):
        zap_icon = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/></svg>"""

        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
            border-radius: 16px;
            margin: 2rem 0;
        ">
            <div style="margin-bottom: 1.5rem; display: flex; justify-content: center;">{zap_icon}</div>
            <h2 style="margin: 0 0 1rem 0; color: #134E4A;">开始使用 AI 面试系统</h2>
            <p style="color: #0F766E; margin: 0 auto; max-width: 500px;">
                在左侧填写岗位信息，然后点击「生成面试链接」按钮。<br>
                将生成的链接发送给候选人即可开始面试。
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick guide
        st.markdown("### 快速指南")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **1. 配置岗位**
            - 填写岗位名称和描述
            - 配置 S 级人才邀请文案
            - 设置飞书通知 Webhook
            """)

        with col2:
            st.markdown("""
            **2. 生成链接**
            - 点击「生成面试链接」
            - 复制生成的 URL
            - 发送给候选人
            """)

        with col3:
            st.markdown("""
            **3. 查看结果**
            - 面试结束后自动评估
            - 飞书群收到通知
            - 在历史记录中查看详情
            """)

    else:
        # Show generated link prominently
        st.success("面试链接已生成！")

        st.markdown(f"""
        <div style="
            background: white;
            border: 2px solid #0D9488;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        ">
            <p style="margin: 0 0 0.5rem 0; color: #64748B; font-size: 0.875rem;">面试链接：</p>
            <code style="
                display: block;
                padding: 1rem;
                background: #F8FAFC;
                border-radius: 8px;
                word-break: break-all;
                font-size: 0.9rem;
            ">{st.session_state.generated_url}</code>
        </div>
        """, unsafe_allow_html=True)

        st.info("将此链接发送给候选人，候选人访问后即可开始 AI 面试。")


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

    # Store job config in session
    st.session_state.current_job_config = job_config

    # Get interview state
    is_started = st.session_state.get("interview_started", False)
    is_ended = st.session_state.get("interview_ended", False)
    is_evaluating = st.session_state.get("is_evaluating", False)

    # State machine
    if not is_started:
        # Welcome screen with candidate info collection
        render_candidate_header(job_config.job_title)

        def on_start(name: str, email: str, resume_summary: str = ""):
            start_interview_for_candidate(job_config, name, email, resume_summary)

        render_candidate_welcome(job_config, on_start)

    elif is_evaluating:
        render_candidate_header(job_config.job_title)
        display_chat_history()
        run_evaluation()

    elif is_ended and st.session_state.get("evaluation_result"):
        render_candidate_header(job_config.job_title)
        display_chat_history()
        render_evaluation_result(
            evaluation=st.session_state.evaluation_result,
            s_tier_invitation=job_config.s_tier_invitation,
            s_tier_link=job_config.s_tier_link
        )

    else:
        # Active interview
        render_candidate_chat_header(
            job_title=job_config.job_title,
            turn_count=st.session_state.get("turn_count", 0),
            max_turns=Settings.MAX_INTERVIEW_TURNS
        )

        display_chat_history()

        is_processing = st.session_state.get("is_processing", False)

        if is_ended:
            render_interview_complete_message()
            st.chat_input(placeholder="面试已结束", disabled=True)
        else:
            placeholder_text = "AI 正在评估您的回答..." if is_processing else "请输入您的回答..."
            user_input = st.chat_input(
                placeholder=placeholder_text,
                disabled=is_processing
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
