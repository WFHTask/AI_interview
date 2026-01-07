"""
Chat UI Component

Provides the main chat interface for interview interaction.
Handles message display, streaming responses, and input management.
"""
import streamlit as st
from typing import Generator, Optional, List
import time

from components.styles import THINKING_INDICATOR_HTML, get_progress_bar, icon
from models.schemas import Message, MessageRole


def render_chat_header(
    title: str = "AI 面试官",
    subtitle: str = "VoiVerse 技术面试"
):
    """Render chat header"""
    target_icon = icon("target", size=28, color="#0D9488")
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <h1 style="margin: 0; font-size: 1.75rem; display: inline-flex; align-items: center; gap: 0.5rem;">
            {target_icon}
            {title}
        </h1>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 0.95rem;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_progress(current: int, max_turns: int):
    """Render interview progress bar"""
    st.markdown(get_progress_bar(current, max_turns), unsafe_allow_html=True)


def render_chat_messages(messages: List[Message]):
    """
    Render chat message history

    Args:
        messages: List of Message objects
    """
    for msg in messages:
        if msg.role == MessageRole.MODEL:
            with st.chat_message("assistant"):
                st.markdown(msg.content)
        elif msg.role == MessageRole.USER:
            with st.chat_message("user"):
                st.markdown(msg.content)


def render_thinking_indicator():
    """Show thinking animation"""
    return st.markdown(THINKING_INDICATOR_HTML, unsafe_allow_html=True)


def stream_response(
    response_generator: Generator[str, None, None],
    placeholder: Optional[st.delta_generator.DeltaGenerator] = None
) -> str:
    """
    Stream response with typing effect

    Args:
        response_generator: Generator yielding text chunks
        placeholder: Streamlit placeholder for updating content

    Returns:
        Complete response text
    """
    if placeholder is None:
        placeholder = st.empty()

    full_response = ""

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        for chunk in response_generator:
            full_response += chunk
            # Show with cursor
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.01)  # Small delay for visual effect

        # Final render without cursor
        message_placeholder.markdown(full_response)

    return full_response


def render_chat_input(
    disabled: bool = False,
    placeholder: str = "请输入您的回答...",
    key: str = "chat_input"
) -> Optional[str]:
    """
    Render chat input box

    Args:
        disabled: Whether input is disabled
        placeholder: Placeholder text
        key: Unique key for the input

    Returns:
        User input or None
    """
    if disabled:
        placeholder = "面试已结束，输入已禁用"

    return st.chat_input(
        placeholder=placeholder,
        disabled=disabled,
        key=key
    )


def render_interview_ended_message():
    """Show interview ended state"""
    flag_icon = icon("flag", size=20, color="#475569")
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #E2E8F0 0%, #CBD5E1 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    ">
        <p style="margin: 0; font-size: 1.1rem; color: #475569; display: inline-flex; align-items: center; gap: 0.5rem;">
            {flag_icon}
            面试已结束，请等待评估结果...
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_welcome_screen():
    """Show welcome screen before interview starts"""
    # Generate icons
    user_icon = icon("user", size=48, color="#0D9488")
    message_icon = icon("message", size=28, color="#0D9488")
    target_icon = icon("target", size=28, color="#0D9488")
    zap_icon = icon("zap", size=28, color="#0D9488")

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
        border-radius: 20px;
        margin: 2rem 0;
    ">
        <div style="margin-bottom: 1rem; display: flex; justify-content: center;">{user_icon}</div>
        <h2 style="margin: 0 0 1rem 0; color: #134E4A;">欢迎来到 VoiVerse AI 面试</h2>
        <p style="color: #0F766E; font-size: 1.1rem; max-width: 500px; margin: 0 auto; line-height: 1.6;">
            我是您的 AI 面试官，将通过对话了解您的技术背景和工作经验。
            请在左侧配置好岗位信息后，点击「开始面试」按钮。
        </p>
    </div>

    <div style="
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 2rem;
    ">
        <div style="
            background: white;
            padding: 1.25rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #E2E8F0;
        ">
            <div style="margin-bottom: 0.5rem; display: flex; justify-content: center;">{message_icon}</div>
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.95rem;">自然对话</h4>
            <p style="margin: 0; font-size: 0.8rem; color: #64748B;">像与真人面试一样交流</p>
        </div>
        <div style="
            background: white;
            padding: 1.25rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #E2E8F0;
        ">
            <div style="margin-bottom: 0.5rem; display: flex; justify-content: center;">{target_icon}</div>
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.95rem;">STAR 原则</h4>
            <p style="margin: 0; font-size: 0.8rem; color: #64748B;">深入了解您的实战经验</p>
        </div>
        <div style="
            background: white;
            padding: 1.25rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #E2E8F0;
        ">
            <div style="margin-bottom: 0.5rem; display: flex; justify-content: center;">{zap_icon}</div>
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.95rem;">即时反馈</h4>
            <p style="margin: 0; font-size: 0.8rem; color: #64748B;">面试结束后立即获得结果</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def init_chat_state():
    """Initialize chat session state"""
    defaults = {
        "messages": [],
        "interview_started": False,
        "interview_ended": False,
        "evaluation_result": None,
        "current_response": ""
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_message_to_state(role: str, content: str):
    """Add message to session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.session_state.messages.append({
        "role": role,
        "content": content
    })


def clear_chat_state():
    """Clear all chat state"""
    st.session_state.messages = []
    st.session_state.interview_started = False
    st.session_state.interview_ended = False
    st.session_state.evaluation_result = None
    st.session_state.current_response = ""
