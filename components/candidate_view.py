"""
Candidate Interview View Component

Clean, minimal interface for candidates taking the interview.
No admin configuration visible - only the chat interface.

Features:
- Candidate info collection (name, email)
- Resume upload (PDF, Image, or Text)
- Interview progress tracking
"""
import streamlit as st
from typing import Optional, Callable, Dict, Any

from components.styles import icon, MAIN_CSS
from components.voice_input_guide import (
    render_voice_input_guide,
    render_voice_input_setup,
    render_voice_input_reminder,
    inject_voice_only_mode,
    VOICE_INPUT_CSS
)
from services.job_config_service import JobConfig
from utils.validators import validate_candidate_name, validate_email


def render_candidate_header(job_title: str = ""):
    """
    Render header for candidate view

    Args:
        job_title: Job title to display
    """
    target_icon = icon("target", size=32, color="#0D9488")

    title_display = f" - {job_title}" if job_title else ""

    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
            {target_icon}
            <h1 style="margin: 0; font-size: 1.75rem; color: #0D9488;">VoiVerse AI 面试</h1>
        </div>
        <p style="color: #64748B; margin: 0; font-size: 1rem;">{title_display or "技术面试"}</p>
    </div>
    """, unsafe_allow_html=True)


def render_candidate_welcome(
    job_config: JobConfig,
    on_start: Callable[[str, str, str], None]
):
    """
    Render welcome screen for candidate with info collection and resume upload

    Args:
        job_config: Job configuration
        on_start: Callback when candidate starts interview (name, email, resume_summary)
    """
    # Welcome message
    hand_icon = icon("hand-wave", size=48, color="#0D9488")

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
        border-radius: 16px;
        margin: 1rem 0 2rem 0;
    ">
        <div style="margin-bottom: 1rem; display: flex; justify-content: center;">{hand_icon}</div>
        <h2 style="margin: 0 0 1rem 0; color: #134E4A;">欢迎参加面试</h2>
        <p style="color: #0F766E; margin: 0; max-width: 500px; margin: 0 auto;">
            您即将开始 VoiVerse 的 AI 技术面试。
            面试官将根据岗位要求与您进行对话，请认真作答。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Job info card
    if job_config.job_title or job_config.job_description:
        clipboard_icon = icon("clipboard", size=20, color="#0D9488")
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #134E4A; display: flex; align-items: center; gap: 0.5rem;">
                {clipboard_icon} 岗位信息
            </h4>
            <p style="color: #64748B; margin: 0; font-size: 0.9rem; white-space: pre-wrap;">
                {job_config.job_description[:500]}{'...' if len(job_config.job_description) > 500 else ''}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Candidate info form
    st.markdown("### 请填写您的信息")

    col1, col2 = st.columns(2)

    with col1:
        candidate_name = st.text_input(
            "姓名 *",
            placeholder="请输入您的姓名",
            key="candidate_name_input"
        )

    with col2:
        candidate_email = st.text_input(
            "邮箱 (可选)",
            placeholder="your@email.com",
            key="candidate_email_input"
        )

    # Resume upload section
    st.markdown("### 上传简历 (可选)")
    st.caption("上传简历可以让面试官更好地了解您，进行更有针对性的提问")

    # Resume upload tabs (using text labels instead of emoji per style guide)
    resume_tab1, resume_tab2 = st.tabs(["上传文件", "粘贴文本"])

    resume_data = None
    resume_summary = ""

    with resume_tab1:
        uploaded_file = st.file_uploader(
            "选择文件",
            type=["pdf", "png", "jpg", "jpeg", "webp"],
            help="支持 PDF、PNG、JPG、WEBP 格式，最大 10MB",
            key="resume_file_uploader"
        )

        if uploaded_file is not None:
            # Show file info
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"已选择: {uploaded_file.name} ({file_size_mb:.1f} MB)")

            # Parse resume button
            if st.button("解析简历", key="parse_resume_file_btn"):
                with st.spinner("正在解析简历，请稍候..."):
                    try:
                        from services.resume_service import parse_resume, get_resume_summary

                        file_bytes = uploaded_file.read()
                        mime_type = uploaded_file.type

                        resume_data = parse_resume(file_data=file_bytes, mime_type=mime_type)
                        resume_summary = get_resume_summary(resume_data)

                        # Store in session state
                        st.session_state.parsed_resume = resume_data
                        st.session_state.resume_summary = resume_summary
                        # Store file data for later saving (after interview starts)
                        st.session_state.resume_file_data = file_bytes
                        st.session_state.resume_file_name = uploaded_file.name

                        st.success("简历解析成功！")
                    except Exception as e:
                        st.error(f"简历解析失败: {str(e)}")

            # Show parsed resume preview
            if st.session_state.get("parsed_resume"):
                _render_resume_preview(st.session_state.parsed_resume)

    with resume_tab2:
        resume_text = st.text_area(
            "粘贴简历内容",
            height=200,
            placeholder="请将您的简历内容粘贴到这里...\n\n包括：个人信息、教育背景、工作经历、项目经验、技能特长等",
            key="resume_text_input"
        )

        if resume_text and len(resume_text.strip()) > 50:
            if st.button("解析简历", key="parse_resume_text_btn"):
                with st.spinner("正在解析简历，请稍候..."):
                    try:
                        from services.resume_service import parse_resume, get_resume_summary

                        resume_data = parse_resume(text=resume_text)
                        resume_summary = get_resume_summary(resume_data)

                        st.session_state.parsed_resume = resume_data
                        st.session_state.resume_summary = resume_summary

                        st.success("简历解析成功！")
                    except Exception as e:
                        st.error(f"简历解析失败: {str(e)}")

            # Show parsed resume preview
            if st.session_state.get("parsed_resume"):
                _render_resume_preview(st.session_state.parsed_resume)

    # Get resume summary from session if available
    final_resume_summary = st.session_state.get("resume_summary", "")

    # Voice input guidance
    render_voice_input_guide()

    with st.expander("语音输入设置指南", expanded=False):
        render_voice_input_setup()

    # Interview tips
    with st.expander("面试须知", expanded=False):
        st.markdown("""
        **面试流程：**
        1. AI 面试官会先进行简短的自我介绍
        2. 面试过程中会围绕您的技术经验进行提问
        3. 请使用语音输入详细回答问题
        4. 面试结束后系统会生成评估结果

        **注意事项：**
        - 本系统仅支持语音输入，请先安装豆包输入法
        - 请在安静的环境下进行面试
        - 面试过程中请保持网络稳定
        - 建议使用 Chrome 或 Firefox 浏览器
        """)

    # Validation state
    validation_errors = []

    # Validate name
    name_valid, name_error = validate_candidate_name(candidate_name) if candidate_name else (False, None)

    # Validate email if provided
    email_valid = True
    email_error = None
    if candidate_email and candidate_email.strip():
        email_valid, email_error = validate_email(candidate_email)

    # Check if can start
    can_start = name_valid and email_valid

    # Show validation errors
    if candidate_name and not name_valid and name_error:
        validation_errors.append(f"姓名: {name_error}")

    if candidate_email and not email_valid and email_error:
        validation_errors.append(f"邮箱: {email_error}")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "开始面试",
        use_container_width=True,
        type="primary",
        disabled=not can_start
    ):
        if can_start:
            on_start(
                candidate_name.strip(),
                candidate_email.strip() if candidate_email else "",
                final_resume_summary
            )

    # Show validation messages
    if validation_errors:
        for error in validation_errors:
            st.error(error)
    elif not candidate_name:
        st.caption("请填写您的姓名后开始面试")


def _render_resume_preview(resume_data: Dict[str, Any]):
    """
    Render parsed resume preview

    Args:
        resume_data: Parsed resume data dict
    """
    file_icon = icon("file-text", size=20, color="#0D9488")

    with st.expander("📋 简历解析结果", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            if resume_data.get("name") and resume_data["name"] != "Unknown":
                st.markdown(f"**姓名:** {resume_data['name']}")
            if resume_data.get("current_position"):
                st.markdown(f"**当前职位:** {resume_data['current_position']}")
            if resume_data.get("current_company"):
                st.markdown(f"**当前公司:** {resume_data['current_company']}")
            if resume_data.get("years_of_experience"):
                st.markdown(f"**工作年限:** {resume_data['years_of_experience']}年")

        with col2:
            if resume_data.get("education"):
                st.markdown(f"**学历:** {resume_data['education']}")
            if resume_data.get("email"):
                st.markdown(f"**邮箱:** {resume_data['email']}")
            if resume_data.get("phone"):
                st.markdown(f"**电话:** {resume_data['phone']}")

        if resume_data.get("skills"):
            skills_str = ", ".join(resume_data["skills"][:10])
            st.markdown(f"**技能:** {skills_str}")

        if resume_data.get("highlights"):
            st.markdown("**核心亮点:**")
            for h in resume_data["highlights"][:3]:
                st.markdown(f"- {h}")

        if resume_data.get("summary"):
            st.markdown(f"**摘要:** {resume_data['summary']}")


def render_candidate_chat_header(job_title: str = "", turn_count: int = 0, max_turns: int = 50, test_mode: bool = False):
    """
    Render minimal header during interview

    Args:
        job_title: Job title
        turn_count: Current turn count
        max_turns: Maximum turns
        test_mode: If True, skip voice-only mode to allow keyboard input
    """
    # Inject voice-only mode CSS and JavaScript (blocks keyboard, allows paste)
    # Skip in test mode to allow typing /stop command
    if not test_mode:
        inject_voice_only_mode()

    target_icon = icon("target", size=24, color="#0D9488")

    progress_pct = min((turn_count / max_turns) * 100, 100)

    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background: #F8FAFC;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
    ">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            {target_icon}
            <span style="font-weight: 600; color: #134E4A;">VoiVerse AI 面试</span>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.75rem; color: #475569; margin-bottom: 0.25rem;">
                面试进度
            </div>
            <div
                role="progressbar"
                aria-valuenow="{turn_count}"
                aria-valuemin="0"
                aria-valuemax="{max_turns}"
                aria-label="面试进度: {turn_count}/{max_turns} 轮"
                style="
                    width: 100px;
                    height: 6px;
                    background: #E2E8F0;
                    border-radius: 3px;
                    overflow: hidden;
                "
            >
                <div style="
                    width: {progress_pct}%;
                    height: 100%;
                    background: linear-gradient(90deg, #0D9488, #14B8A6);
                    border-radius: 3px;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show voice input reminder
    render_voice_input_reminder()


def render_interview_complete_message():
    """Render message when interview is complete"""
    check_icon = icon("check-circle", size=48, color="#10B981")

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid #A7F3D0;
    ">
        <div style="margin-bottom: 1rem; display: flex; justify-content: center;">{check_icon}</div>
        <h3 style="margin: 0 0 0.5rem 0; color: #065F46;">面试已结束</h3>
        <p style="color: #047857; margin: 0;">
            感谢您的参与，请等待系统生成评估结果...
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_invalid_link():
    """Render error when interview link is invalid"""
    alert_icon = icon("alert-triangle", size=48, color="#EF4444")

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem;
        background: #FEF2F2;
        border-radius: 16px;
        margin: 2rem 0;
        border: 1px solid #FECACA;
    ">
        <div style="margin-bottom: 1rem; display: flex; justify-content: center;">{alert_icon}</div>
        <h2 style="margin: 0 0 1rem 0; color: #991B1B;">链接无效</h2>
        <p style="color: #B91C1C; margin: 0;">
            您访问的面试链接无效或已过期。<br>
            请联系 HR 获取新的面试链接。
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_candidate_footer():
    """Render footer for candidate view"""
    st.markdown("""
    <div style="
        text-align: center;
        padding: 1.5rem 0;
        margin-top: 2rem;
        border-top: 1px solid #E2E8F0;
        color: #94A3B8;
        font-size: 0.75rem;
    ">
        <p style="margin: 0;">Powered by VoiVerse AI</p>
    </div>
    """, unsafe_allow_html=True)
