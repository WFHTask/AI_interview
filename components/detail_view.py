"""
Interview Detail View Component

Displays complete interview record for HR review.
Accessed via ?session=xxx parameter from Feishu notification.
"""
import streamlit as st
from typing import Optional
from datetime import datetime

from components.styles import icon, MAIN_CSS
from models.schemas import InterviewSession, EvaluationResult, DecisionTier


def render_detail_header():
    """Render header for detail view"""
    target_icon = icon("target", size=32, color="#0D9488")

    st.markdown(f"""<div style="text-align: center; padding: 1.5rem 0 1rem 0;">
<div style="display: flex; justify-content: center; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
{target_icon}
<h1 style="margin: 0; font-size: 1.75rem; color: #0D9488;">VoiVerse AI 面试</h1>
</div>
<p style="color: #64748B; margin: 0; font-size: 1rem;">面试详情记录</p>
</div>""", unsafe_allow_html=True)


def render_not_found(session_id: str):
    """Render not found message"""
    alert_icon = icon("alert-triangle", size=48, color="#F59E0B")

    st.markdown(f"""<div style="
text-align: center;
padding: 3rem;
background: #FFFBEB;
border-radius: 16px;
margin: 2rem 0;
border: 1px solid #FDE68A;
">
<div style="margin-bottom: 1rem; display: flex; justify-content: center;">{alert_icon}</div>
<h2 style="margin: 0 0 1rem 0; color: #92400E;">未找到面试记录</h2>
<p style="color: #B45309; margin: 0;">
找不到 ID 为 "{session_id}" 的面试记录。<br>
记录可能已被删除或链接已过期。
</p>
</div>""", unsafe_allow_html=True)


def render_candidate_info(
    session: InterviewSession,
    evaluation: Optional[EvaluationResult] = None
):
    """Render candidate information card"""
    user_icon = icon("user", size=20, color="#0D9488")

    candidate_name = evaluation.candidate_name if evaluation else session.candidate_name or "Unknown"
    candidate_email = session.candidate_email or "未提供"

    # Check for resume file
    resume_info_html = ""
    if session.resume_file_path:
        import os
        from pathlib import Path
        file_path = Path(session.resume_file_path)
        if file_path.exists():
            file_ext = file_path.suffix.upper().replace(".", "")
            file_size = file_path.stat().st_size / 1024  # KB
            file_icon = icon("file-text", size=14, color="#0D9488")
            resume_info_html = f"""
        <div>
            <p style="color: #64748B; margin: 0 0 0.25rem 0; font-size: 0.875rem;">简历文件</p>
            <p style="color: #1E293B; margin: 0; display: flex; align-items: center; gap: 0.25rem;">
                {file_icon} {file_ext} ({file_size:.1f} KB)
            </p>
        </div>
            """

    st.markdown(f"""
<div style="
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
">
    <h4 style="margin: 0 0 1rem 0; color: #134E4A; display: flex; align-items: center; gap: 0.5rem;">
        {user_icon} 候选人信息
    </h4>
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
        <div>
            <p style="color: #64748B; margin: 0 0 0.25rem 0; font-size: 0.875rem;">姓名</p>
            <p style="color: #1E293B; margin: 0; font-weight: 600;">{candidate_name}</p>
        </div>
        <div>
            <p style="color: #64748B; margin: 0 0 0.25rem 0; font-size: 0.875rem;">邮箱</p>
            <p style="color: #1E293B; margin: 0;">{candidate_email}</p>
        </div>
        <div>
            <p style="color: #64748B; margin: 0 0 0.25rem 0; font-size: 0.875rem;">面试时间</p>
            <p style="color: #1E293B; margin: 0;">{session.created_at.strftime('%Y-%m-%d %H:%M') if session.created_at else '未知'}</p>
        </div>
        <div>
            <p style="color: #64748B; margin: 0 0 0.25rem 0; font-size: 0.875rem;">对话轮次</p>
            <p style="color: #1E293B; margin: 0;">{session.turn_count} 轮</p>
        </div>
{resume_info_html}
    </div>
</div>
    """, unsafe_allow_html=True)

    # Resume file download button
    if session.resume_file_path:
        from pathlib import Path
        file_path = Path(session.resume_file_path)
        if file_path.exists():
            with open(file_path, "rb") as f:
                file_data = f.read()
            st.download_button(
                label="下载简历文件",
                data=file_data,
                file_name=file_path.name,
                mime="application/octet-stream",
                key="download_resume_btn"
            )


def render_evaluation_summary(evaluation: EvaluationResult):
    """Render evaluation summary card"""
    award_icon = icon("award", size=20, color="#0D9488")

    # Tier colors
    tier_colors = {
        DecisionTier.S: ("#F59E0B", "#FFFBEB", "#FDE68A"),  # Amber
        DecisionTier.A: ("#10B981", "#ECFDF5", "#A7F3D0"),  # Green
        DecisionTier.B: ("#F97316", "#FFF7ED", "#FED7AA"),  # Orange
        DecisionTier.C: ("#6B7280", "#F9FAFB", "#E5E7EB"),  # Gray
    }

    tier_bg, tier_card_bg, tier_border = tier_colors.get(
        evaluation.decision_tier,
        ("#6B7280", "#F9FAFB", "#E5E7EB")
    )

    tier_labels = {
        DecisionTier.S: "S 级 - 卓越人才",
        DecisionTier.A: "A 级 - 优秀",
        DecisionTier.B: "B 级 - 合格",
        DecisionTier.C: "C 级 - 不通过",
    }

    tier_label = tier_labels.get(evaluation.decision_tier, "未知")

    st.markdown(f"""<div style="
background: {tier_card_bg};
border: 2px solid {tier_border};
border-radius: 12px;
padding: 1.5rem;
margin-bottom: 1.5rem;
">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<h4 style="margin: 0; color: #134E4A; display: flex; align-items: center; gap: 0.5rem;">
{award_icon} 评估结果
</h4>
<span style="
background: {tier_bg};
color: white;
padding: 0.375rem 0.875rem;
border-radius: 20px;
font-weight: 600;
font-size: 0.875rem;
">{tier_label}</span>
</div>
<div style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 1rem;">
<span style="font-size: 3rem; font-weight: 700; color: {tier_bg};">{evaluation.total_score}</span>
<span style="color: #64748B; font-size: 1rem;">/ 100 分</span>
</div>
<p style="color: #475569; margin: 0; line-height: 1.6;">{evaluation.summary}</p>
</div>""", unsafe_allow_html=True)


def render_score_breakdown(evaluation: EvaluationResult):
    """Render detailed score breakdown"""
    bar_icon = icon("bar-chart", size=20, color="#0D9488")

    scores = [
        ("技能匹配度", evaluation.skill_match_score, "60%"),
        ("沟通与逻辑", evaluation.communication_score, "20%"),
        ("远程适应性", evaluation.remote_readiness_score, "20%"),
    ]

    scores_html = ""
    for name, score, weight in scores:
        if score is not None:
            # Calculate color based on score
            if score >= 80:
                bar_color = "#10B981"
            elif score >= 60:
                bar_color = "#F59E0B"
            else:
                bar_color = "#EF4444"

            scores_html += f"""<div style="margin-bottom: 1rem;">
<div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
<span style="color: #475569; font-size: 0.9rem;">{name} <span style="color: #94A3B8;">({weight})</span></span>
<span style="color: #1E293B; font-weight: 600;">{score}</span>
</div>
<div style="height: 8px; background: #E2E8F0; border-radius: 4px; overflow: hidden;">
<div style="width: {score}%; height: 100%; background: {bar_color}; border-radius: 4px;"></div>
</div>
</div>"""

    st.markdown(f"""<div style="
background: white;
border: 1px solid #E2E8F0;
border-radius: 12px;
padding: 1.5rem;
margin-bottom: 1.5rem;
">
<h4 style="margin: 0 0 1rem 0; color: #134E4A; display: flex; align-items: center; gap: 0.5rem;">
{bar_icon} 分项评分
</h4>
{scores_html}
</div>""", unsafe_allow_html=True)


def render_strengths_and_flags(evaluation: EvaluationResult):
    """Render key strengths and red flags"""
    check_icon = icon("check-circle", size=16, color="#10B981")
    flag_icon = icon("flag", size=16, color="#EF4444")

    # Strengths
    strengths_html = ""
    for strength in evaluation.key_strengths:
        strengths_html += f"""<div style="display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem;">
{check_icon}
<span style="color: #1E293B;">{strength}</span>
</div>"""

    # Red flags
    flags_html = ""
    for flag in evaluation.red_flags:
        flags_html += f"""<div style="display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem;">
{flag_icon}
<span style="color: #1E293B;">{flag}</span>
</div>"""

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""<div style="
background: #ECFDF5;
border: 1px solid #A7F3D0;
border-radius: 12px;
padding: 1.25rem;
height: 100%;
">
<h5 style="margin: 0 0 1rem 0; color: #065F46;">核心亮点</h5>
{strengths_html or '<p style="color: #64748B; margin: 0;">无</p>'}
</div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div style="
background: #FEF2F2;
border: 1px solid #FECACA;
border-radius: 12px;
padding: 1.25rem;
height: 100%;
">
<h5 style="margin: 0 0 1rem 0; color: #991B1B;">关注点</h5>
{flags_html or '<p style="color: #64748B; margin: 0;">无</p>'}
</div>""", unsafe_allow_html=True)


def render_chat_history(session: InterviewSession):
    """Render full chat history"""
    message_icon = icon("message", size=20, color="#0D9488")

    st.markdown(f"""<h4 style="margin: 1.5rem 0 1rem 0; color: #134E4A; display: flex; align-items: center; gap: 0.5rem;">
{message_icon} 完整对话记录
</h4>""", unsafe_allow_html=True)

    if not session.chat_history:
        st.info("暂无对话记录")
        return

    for msg in session.chat_history:
        role = msg.role.value if hasattr(msg.role, 'value') else msg.role
        content = msg.content

        if role == "model":
            with st.chat_message("assistant"):
                st.markdown(content)
        else:
            with st.chat_message("user"):
                st.markdown(content)


def render_detail_footer():
    """Render footer for detail view"""
    st.markdown("""<div style="
text-align: center;
padding: 1.5rem 0;
margin-top: 2rem;
border-top: 1px solid #E2E8F0;
color: #94A3B8;
font-size: 0.75rem;
">
<p style="margin: 0;">Powered by VoiVerse AI</p>
</div>""", unsafe_allow_html=True)


def render_detail_view(
    session: Optional[InterviewSession],
    evaluation: Optional[EvaluationResult],
    session_id: str
):
    """
    Main render function for detail view

    Args:
        session: Interview session data
        evaluation: Evaluation result data
        session_id: Session ID from URL
    """
    # Hide sidebar for detail view
    st.markdown("""<style>
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
</style>""", unsafe_allow_html=True)

    render_detail_header()

    if not session:
        render_not_found(session_id)
        render_detail_footer()
        return

    # Candidate info
    render_candidate_info(session, evaluation)

    # Evaluation results
    if evaluation:
        render_evaluation_summary(evaluation)
        render_score_breakdown(evaluation)
        render_strengths_and_flags(evaluation)
    else:
        st.warning("评估结果暂未生成")

    # Chat history
    render_chat_history(session)

    render_detail_footer()
