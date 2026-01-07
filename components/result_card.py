"""
Result Card Component

Displays evaluation results with different styles based on tier.
Special celebration card for S-tier candidates.
"""
import streamlit as st
from typing import Optional

from models.schemas import EvaluationResult, DecisionTier
from components.styles import get_s_tier_card, get_result_card, icon


def render_evaluation_result(
    evaluation: EvaluationResult,
    s_tier_invitation: str = "",
    s_tier_link: str = ""
):
    """
    Render evaluation result based on tier

    Args:
        evaluation: Evaluation result object
        s_tier_invitation: Custom S-tier invitation text
        s_tier_link: S-tier booking link
    """
    if evaluation.is_s_tier:
        render_s_tier_celebration(
            evaluation=evaluation,
            invitation=s_tier_invitation,
            link=s_tier_link
        )
    else:
        render_standard_result(evaluation)


def render_s_tier_celebration(
    evaluation: EvaluationResult,
    invitation: str = "",
    link: str = ""
):
    """
    Render S-tier celebration card with special styling

    Args:
        evaluation: Evaluation result
        invitation: Invitation text
        link: Booking link
    """
    # Celebration animation
    st.balloons()

    # S-tier card
    card_html = get_s_tier_card(
        notification_text=evaluation.notification_text,
        invitation=invitation or "请直接添加 CTO 微信进行沟通",
        link=link
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # Additional details in expander
    with st.expander("查看详细评估", expanded=False):
        render_score_breakdown(evaluation)
        render_strengths_and_flags(evaluation)


def render_standard_result(evaluation: EvaluationResult):
    """
    Render standard (non-S-tier) result card

    Args:
        evaluation: Evaluation result
    """
    # Tier-specific icon (SVG)
    tier_icon_names = {
        DecisionTier.A: "check-circle",
        DecisionTier.B: "clipboard",
        DecisionTier.C: "x-circle"
    }
    tier_icon_name = tier_icon_names.get(evaluation.decision_tier, "bar-chart")
    tier_icon_svg = icon(tier_icon_name, size=16, color="white")

    # Result card
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        border-left: 4px solid {'#10B981' if evaluation.is_pass else '#EF4444'};
        margin: 1.5rem 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <span style="font-size: 2.5rem; font-weight: 700; color: #0D9488;">{evaluation.total_score}</span>
                <span style="color: #64748B; font-size: 0.875rem;"> / 100 分</span>
            </div>
            <span style="
                background: {'#10B981' if evaluation.decision_tier == DecisionTier.A else '#F59E0B' if evaluation.decision_tier == DecisionTier.B else '#94A3B8'};
                color: white;
                padding: 0.375rem 0.875rem;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.875rem;
                display: inline-flex;
                align-items: center;
                gap: 0.25rem;
            ">{tier_icon_svg} {evaluation.decision_tier.value} 级</span>
        </div>
        <p style="color: #64748B; margin: 0;">{evaluation.notification_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # Show details
    with st.expander("查看详细评估", expanded=True):
        render_score_breakdown(evaluation)
        render_strengths_and_flags(evaluation)
        render_summary(evaluation)


def render_score_breakdown(evaluation: EvaluationResult):
    """Render score breakdown section"""
    trending_icon = icon("trending-up", size=20, color="#0D9488")
    st.markdown(f"#### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{trending_icon} 分数明细</span>", unsafe_allow_html=True)

    cols = st.columns(3)

    with cols[0]:
        score = evaluation.skill_match_score or 0
        st.metric(
            label="技能匹配 (权重60%)",
            value=f"{score}/100",
            delta="达标" if score >= 60 else "待提升",
            delta_color="normal" if score >= 60 else "inverse"
        )

    with cols[1]:
        score = evaluation.communication_score or 0
        st.metric(
            label="沟通能力 (权重20%)",
            value=f"{score}/100",
            delta="达标" if score >= 60 else "待提升",
            delta_color="normal" if score >= 60 else "inverse"
        )

    with cols[2]:
        score = evaluation.remote_readiness_score or 0
        st.metric(
            label="远程适应性 (权重20%)",
            value=f"{score}/100",
            delta="达标" if score >= 60 else "待提升",
            delta_color="normal" if score >= 60 else "inverse"
        )


def render_strengths_and_flags(evaluation: EvaluationResult):
    """Render strengths and red flags section"""
    cols = st.columns(2)

    sparkles_icon = icon("sparkles", size=20, color="#10B981")
    alert_icon = icon("alert-triangle", size=20, color="#F59E0B")

    with cols[0]:
        st.markdown(f"#### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{sparkles_icon} 亮点</span>", unsafe_allow_html=True)
        if evaluation.key_strengths:
            for strength in evaluation.key_strengths:
                st.markdown(f"- {strength}")
        else:
            st.markdown("_无特别突出的亮点_")

    with cols[1]:
        st.markdown(f"#### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{alert_icon} 关注点</span>", unsafe_allow_html=True)
        if evaluation.red_flags:
            for flag in evaluation.red_flags:
                st.markdown(f"- {flag}")
        else:
            st.markdown("_无明显问题_")


def render_summary(evaluation: EvaluationResult):
    """Render evaluation summary"""
    file_icon = icon("file-text", size=20, color="#0D9488")
    st.markdown(f"#### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{file_icon} 评估总结</span>", unsafe_allow_html=True)
    st.info(evaluation.summary)


def render_loading_evaluation():
    """Show loading state while evaluating"""
    brain_icon = icon("brain", size=40, color="#0D9488")
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
        border-radius: 16px;
        margin: 1.5rem 0;
    ">
        <div style="margin-bottom: 1rem; display: flex; justify-content: center;">{brain_icon}</div>
        <h3 style="margin: 0 0 0.5rem 0; color: #134E4A;">正在生成评估报告...</h3>
        <p style="margin: 0; color: #0F766E;">AI 判官正在分析您的面试表现</p>
    </div>
    """, unsafe_allow_html=True)

    # Show spinner
    with st.spinner("评估中，请稍候..."):
        pass


def render_evaluation_error(error_message: str):
    """Show evaluation error"""
    st.error(f"评估生成失败: {error_message}")
    st.markdown("""
    <div style="
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
    ">
        <p style="margin: 0; color: #991B1B;">
            评估过程中出现错误。您的面试记录已保存，HR 将手动审核您的表现。
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_tier_explanation():
    """Render tier explanation helper"""
    with st.expander("评级说明"):
        st.markdown("""
        | 等级 | 分数范围 | 说明 |
        |------|----------|------|
        | **S 级** | ≥ 90 | 极其优秀，直接进入 CTO 面试 |
        | **A 级** | 80-89 | 优秀，进入下一轮面试 |
        | **B 级** | 60-79 | 合格，作为备选候选人 |
        | **C 级** | < 60 | 不符合要求 |
        """)
