"""
Login Form Component for HR Admin

Clean, secure login interface.
"""
import streamlit as st
from typing import Callable, Optional

from components.styles import icon


def render_login_page(on_login: Callable[[str, str], bool]) -> bool:
    """
    Render the login page for HR admin.

    Args:
        on_login: Callback function that takes (username, password) and returns success bool

    Returns:
        True if user is authenticated
    """
    # Render minimal sidebar with logo (don't hide it completely)
    _render_login_sidebar()

    # Logo and title
    target_icon = icon("target", size=48, color="#0D9488")

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 1rem;
    ">
        <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
            {target_icon}
        </div>
        <h1 style="margin: 0; color: #134E4A; font-size: 2rem;">VoiVerse AI</h1>
        <p style="color: #64748B; margin: 0.5rem 0 0 0;">HR 管理后台</p>
    </div>
    """, unsafe_allow_html=True)

    # Login form container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="
            background: white;
            padding: 2rem;
            border-radius: 16px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        ">
        """, unsafe_allow_html=True)

        # Login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 登录")

            username = st.text_input(
                "用户名",
                placeholder="请输入用户名",
                key="login_username",
                autocomplete="username"
            )

            password = st.text_input(
                "密码",
                type="password",
                placeholder="请输入密码",
                key="login_password",
                autocomplete="current-password"
            )

            is_submitting = st.session_state.get("login_submitting", False)

            submit = st.form_submit_button(
                "登录中..." if is_submitting else "登录",
                use_container_width=True,
                type="primary",
                disabled=is_submitting
            )

            if submit and not is_submitting:
                if not username or not password:
                    st.error("请输入用户名和密码")
                    return False

                st.session_state.login_submitting = True

                if on_login(username, password):
                    st.session_state.login_submitting = False
                    st.toast("登录成功!", icon="✓")
                    st.rerun()
                    return True
                else:
                    st.session_state.login_submitting = False
                    st.error("用户名或密码错误")
                    return False

        st.markdown("</div>", unsafe_allow_html=True)

        # Security notice
        st.markdown("""
        <div style="
            text-align: center;
            margin-top: 1.5rem;
            color: #94A3B8;
            font-size: 0.75rem;
        ">
            <p style="margin: 0;">安全提示: 请勿在公共网络上登录</p>
        </div>
        """, unsafe_allow_html=True)

    return False


def render_logout_button() -> bool:
    """
    Render logout button in sidebar.

    Returns:
        True if logout was clicked
    """
    if st.sidebar.button("退出登录", use_container_width=True, key="logout_btn"):
        return True
    return False


def init_auth_state():
    """Initialize authentication session state"""
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None

    if "auth_username" not in st.session_state:
        st.session_state.auth_username = None


def set_auth_state(token: str, username: str):
    """Set authentication state after successful login"""
    st.session_state.auth_token = token
    st.session_state.auth_username = username


def clear_auth_state():
    """Clear authentication state on logout"""
    st.session_state.auth_token = None
    st.session_state.auth_username = None


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return bool(st.session_state.get("auth_token"))


def get_current_user() -> Optional[str]:
    """Get current authenticated username"""
    return st.session_state.get("auth_username")


def _render_login_sidebar():
    """Render minimal sidebar for login page"""
    with st.sidebar:
        target_icon = icon("target", size=32, color="#FFFFFF")
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
                {target_icon}
            </div>
            <h2 style="margin: 0; color: #FFFFFF; font-size: 1.5rem;">VoiVerse</h2>
            <p style="margin: 0.5rem 0 0 0; color: #CCFBF1; font-size: 0.875rem;">AI 面试系统</p>
        </div>
        <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.2); margin: 1rem 0;">
        <p style="text-align: center; color: #CCFBF1; font-size: 0.8rem; opacity: 0.7;">
            请登录以访问管理后台
        </p>
        """, unsafe_allow_html=True)
