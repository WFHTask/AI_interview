"""
Sidebar Component for HR Admin Configuration

Provides interface for:
- Company information configuration
- Job Description input
- S-tier invitation configuration
- Feishu webhook settings
- Generate interview link
- View job configurations
- Interview history
"""
import streamlit as st
from typing import Callable, Optional

from config.settings import Settings
from components.styles import icon
from services.company_config_service import company_config_service, CompanyConfig


def render_admin_sidebar(
    on_generate_link: Optional[Callable] = None,
    on_select_config: Optional[Callable[[str], None]] = None
) -> dict:
    """
    Render HR admin sidebar for job configuration

    Args:
        on_generate_link: Callback when generating interview link
        on_select_config: Callback when selecting existing config

    Returns:
        dict with configuration values
    """
    with st.sidebar:
        # Logo/Title - 更紧凑的设计
        target_icon = icon("target", size=20, color="#5EEAD4")
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0 1rem 0;">
            {target_icon}
            <span style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">VoiVerse</span>
            <span style="font-size: 0.75rem; color: #99F6E4; margin-left: auto;">HR 后台</span>
        </div>
        """, unsafe_allow_html=True)

        # ===========================================
        # 公司信息配置 - 使用expander折叠
        # ===========================================
        existing_company_config = company_config_service.get_config()
        has_company_config = company_config_service.has_config()

        company_status = "✓" if has_company_config else "!"
        with st.expander(f"公司信息 {company_status}", expanded=not has_company_config):
            if "company_background" not in st.session_state:
                st.session_state.company_background = existing_company_config.company_background

            company_background = st.text_area(
                "公司背景",
                value=st.session_state.get("company_background", ""),
                height=100,
                placeholder="公司背景、招聘目标...",
                key="company_background_input",
                label_visibility="collapsed"
            )
            st.session_state.company_background = company_background

            if st.button("保存", use_container_width=True, key="save_company_config_btn"):
                if company_background and company_background.strip():
                    if company_config_service.update_background(company_background.strip()):
                        st.toast("已保存")
                        st.rerun()
                else:
                    st.warning("请填写内容")

        # ===========================================
        # 岗位配置选择 - 紧凑下拉框
        # ===========================================
        from services.job_config_service import job_config_service
        existing_configs = job_config_service.list_configs(active_only=True)

        config_options = {"新建配置": None}
        if existing_configs:
            for c in existing_configs:
                label = c.job_title if c.job_title else c.job_description[:15] + "..."
                config_options[label] = c.config_id

        current_config_id = st.session_state.get("current_config_id")
        default_index = 0
        if current_config_id:
            for i, (_, cid) in enumerate(config_options.items()):
                if cid == current_config_id:
                    default_index = i
                    break

        selected_option = st.selectbox(
            "岗位",
            options=list(config_options.keys()),
            index=default_index,
            key="config_selector",
            label_visibility="collapsed"
        )

        selected_config_id = config_options[selected_option]
        is_editing = selected_config_id is not None

        # Handle config selection change
        if selected_config_id != st.session_state.get("_last_selected_config"):
            st.session_state._last_selected_config = selected_config_id

            if selected_config_id:
                selected_config = job_config_service.load_config(selected_config_id)
                if selected_config:
                    st.session_state.job_description = selected_config.job_description
                    st.session_state.job_title = selected_config.job_title
                    st.session_state.custom_greeting = selected_config.custom_greeting
                    st.session_state.s_tier_invitation = selected_config.s_tier_invitation
                    st.session_state.s_tier_link = selected_config.s_tier_link
                    st.session_state.feishu_webhook = selected_config.feishu_webhook
                    st.session_state.test_mode = selected_config.test_mode
                    st.session_state.current_config_id = selected_config_id
                    st.session_state.generated_url = selected_config.get_interview_url()
                    if on_select_config:
                        on_select_config(selected_config_id)
            else:
                st.session_state.job_description = ""
                st.session_state.job_title = ""
                st.session_state.custom_greeting = ""
                st.session_state.s_tier_invitation = "请直接添加 CTO 微信：VoiCTO"
                st.session_state.s_tier_link = ""
                st.session_state.feishu_webhook = ""
                st.session_state.test_mode = False
                st.session_state.current_config_id = None
                st.session_state.generated_url = None

        # 编辑模式显示面试数量
        if is_editing:
            cfg = job_config_service.load_config(selected_config_id)
            if cfg:
                st.caption(f"已面试 {cfg.interview_count} 人")

        # ===========================================
        # 岗位信息 - 使用expander
        # ===========================================
        with st.expander("岗位信息", expanded=True):
            job_title = st.text_input(
                "岗位名称",
                value=st.session_state.get("job_title", ""),
                placeholder="高级 Go 开发工程师",
                key="job_title_input"
            )

            job_description = st.text_area(
                "岗位描述 (JD)",
                value=st.session_state.get("job_description", ""),
                height=120,
                placeholder="技术要求、工作职责...",
                key="jd_input"
            )

            custom_greeting = st.text_area(
                "自定义开场白 (可选)",
                value=st.session_state.get("custom_greeting", ""),
                height=60,
                placeholder="留空则 AI 自动生成",
                key="custom_greeting_input"
            )
            st.session_state.custom_greeting = custom_greeting

            st.session_state.job_description = job_description
            st.session_state.job_title = job_title

        # ===========================================
        # S级人才和通知 - 合并为一个expander
        # ===========================================
        with st.expander("高级设置", expanded=False):
            st.markdown("**S 级人才邀请**")
            s_tier_invitation = st.text_area(
                "邀请文案",
                value=st.session_state.get("s_tier_invitation", "请直接添加 CTO 微信：VoiCTO"),
                height=60,
                placeholder="S 级人才专属邀请...",
                key="s_tier_invitation_input",
                label_visibility="collapsed"
            )

            s_tier_link = st.text_input(
                "预约链接",
                value=st.session_state.get("s_tier_link", ""),
                placeholder="https://calendly.com/...",
                key="s_tier_link_input"
            )

            st.session_state.s_tier_invitation = s_tier_invitation
            st.session_state.s_tier_link = s_tier_link

            st.markdown("---")
            st.markdown("**飞书通知**")
            feishu_webhook = st.text_input(
                "Webhook URL",
                value=st.session_state.get("feishu_webhook", ""),
                type="password",
                placeholder="https://open.feishu.cn/...",
                key="feishu_webhook_input",
                label_visibility="collapsed"
            )
            st.session_state.feishu_webhook = feishu_webhook

            if feishu_webhook:
                if st.button("测试", key="test_feishu"):
                    with st.spinner("测试中..."):
                        try:
                            from services.feishu_service import FeishuService
                            service = FeishuService(feishu_webhook)
                            if service.test_connection():
                                st.success("连接成功")
                            else:
                                st.error("连接失败")
                        except Exception as e:
                            st.error(f"错误: {str(e)}")

            st.markdown("---")
            st.markdown("**测试模式**")
            if "test_mode" not in st.session_state:
                st.session_state.test_mode = False

            test_mode = st.toggle(
                "启用 (/stop 结束)",
                value=st.session_state.get("test_mode", False),
                key="test_mode_toggle"
            )
            st.session_state.test_mode = test_mode

        # ===========================================
        # 操作按钮 - 更紧凑
        # ===========================================
        can_save = bool(job_description and job_description.strip())

        if selected_config_id:
            # 编辑已有配置
            col1, col2 = st.columns(2)
            with col1:
                if st.button("保存", use_container_width=True, disabled=not can_save, type="primary", key="save_config_btn"):
                    if can_save:
                        from services.job_config_service import JobConfig
                        existing = job_config_service.load_config(selected_config_id)
                        if existing:
                            existing.job_description = job_description
                            existing.job_title = job_title
                            existing.custom_greeting = custom_greeting
                            existing.s_tier_invitation = s_tier_invitation
                            existing.s_tier_link = s_tier_link
                            existing.feishu_webhook = feishu_webhook
                            existing.test_mode = test_mode
                            job_config_service.update_config(existing)
                            st.session_state.generated_url = existing.get_interview_url()
                            st.toast("已保存")
                            st.rerun()

            with col2:
                if st.button("复制", use_container_width=True, key="duplicate_config_btn"):
                    from services.job_config_service import create_job_config
                    new_config = create_job_config(
                        job_description=job_description,
                        job_title=f"{job_title} (副本)" if job_title else "",
                        custom_greeting=custom_greeting,
                        s_tier_invitation=s_tier_invitation,
                        s_tier_link=s_tier_link,
                        feishu_webhook=feishu_webhook
                    )
                    st.session_state.current_config_id = new_config.config_id
                    st.session_state._last_selected_config = new_config.config_id
                    st.session_state.generated_url = new_config.get_interview_url()
                    st.toast("已复制")
                    st.rerun()

            # 删除按钮
            if st.button("删除配置", use_container_width=True, key="delete_config_btn"):
                st.session_state._confirm_delete = selected_config_id

            if st.session_state.get("_confirm_delete") == selected_config_id:
                st.warning("确定删除？")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("确定", use_container_width=True, key="confirm_delete"):
                        job_config_service.delete_config(selected_config_id)
                        st.session_state.current_config_id = None
                        st.session_state._last_selected_config = None
                        st.session_state.generated_url = None
                        st.session_state._confirm_delete = None
                        st.toast("已删除")
                        st.rerun()
                with c2:
                    if st.button("取消", use_container_width=True, key="cancel_delete"):
                        st.session_state._confirm_delete = None
                        st.rerun()

        else:
            # 新建配置
            if st.button("生成面试链接", use_container_width=True, disabled=not can_save, type="primary", key="generate_link_btn"):
                if can_save:
                    from services.job_config_service import create_job_config
                    config = create_job_config(
                        job_description=job_description,
                        job_title=job_title,
                        custom_greeting=custom_greeting,
                        s_tier_invitation=s_tier_invitation,
                        s_tier_link=s_tier_link,
                        feishu_webhook=feishu_webhook,
                        test_mode=test_mode
                    )
                    st.session_state.current_config_id = config.config_id
                    st.session_state._last_selected_config = config.config_id
                    st.session_state.generated_url = config.get_interview_url()
                    if on_generate_link:
                        on_generate_link()
                    st.toast("已创建")
                    st.rerun()

            if not can_save:
                st.caption("请先填写岗位描述")

        # 显示生成的链接
        if st.session_state.get("generated_url"):
            st.code(st.session_state.generated_url, language=None)
            st.caption("发送给候选人")

        # ===========================================
        # Interview History
        # ===========================================
        history_icon = icon("clock", size=20, color="#CCFBF1")
        st.markdown(f"### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{history_icon} 面试历史</span>", unsafe_allow_html=True)

        from services.storage_service import storage_service

        # Get grade counts for filter display
        grade_counts = storage_service.get_grade_counts(days=7)
        total_count = sum(grade_counts.values())

        if total_count > 0:
            # Grade filter tabs
            st.caption(f"最近 7 天: {total_count} 条记录")

            # Grade filter selector
            grade_options = {
                "全部": None,
                f"S级 ({grade_counts['S']})": "S",
                f"A级 ({grade_counts['A']})": "A",
                f"B级 ({grade_counts['B']})": "B",
                f"C级 ({grade_counts['C']})": "C",
                f"待评估 ({grade_counts['pending']})": "pending"
            }

            # Initialize filter state
            if "_history_grade_filter" not in st.session_state:
                st.session_state._history_grade_filter = "全部"

            selected_filter = st.selectbox(
                "筛选等级",
                options=list(grade_options.keys()),
                index=list(grade_options.keys()).index(st.session_state._history_grade_filter) if st.session_state._history_grade_filter in grade_options else 0,
                key="grade_filter_select"
            )
            st.session_state._history_grade_filter = selected_filter

            grade_filter_value = grade_options[selected_filter]

            # Handle "pending" as no grade
            if grade_filter_value == "pending":
                recent_sessions = [s for s in storage_service.get_recent_sessions(days=7) if s.get("grade") is None]
            else:
                recent_sessions = storage_service.get_recent_sessions(days=7, grade_filter=grade_filter_value)

            # Grade statistics display
            st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.5rem 0;">
                <span style="background: linear-gradient(135deg, #FCD34D, #F59E0B); color: #78350F; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">S: {grade_counts['S']}</span>
                <span style="background: linear-gradient(135deg, #34D399, #10B981); color: #064E3B; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">A: {grade_counts['A']}</span>
                <span style="background: linear-gradient(135deg, #60A5FA, #3B82F6); color: #1E3A8A; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">B: {grade_counts['B']}</span>
                <span style="background: linear-gradient(135deg, #F87171, #EF4444); color: #7F1D1D; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">C: {grade_counts['C']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Clear all button
            col_clear, col_spacer = st.columns([1, 1])
            with col_clear:
                if st.button("清空所有记录", use_container_width=True, key="clear_all_history_btn"):
                    st.session_state._confirm_clear_all = True

            # Confirm clear all dialog
            if st.session_state.get("_confirm_clear_all"):
                st.warning(f"确定要清空最近 7 天的 {total_count} 条记录吗？此操作不可恢复！")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("确定清空", use_container_width=True, key="confirm_clear_all"):
                        deleted_count = storage_service.clear_all_sessions(days=7)
                        st.session_state._confirm_clear_all = False
                        st.toast(f"已清空 {deleted_count} 条记录")
                        st.rerun()
                with col_no:
                    if st.button("取消", use_container_width=True, key="cancel_clear_all"):
                        st.session_state._confirm_clear_all = False
                        st.rerun()

            with st.expander(f"查看历史记录 ({len(recent_sessions)})", expanded=False):
                for idx, session_info in enumerate(recent_sessions[:20]):
                    status_indicator = {
                        "completed": "完成",
                        "terminated": "终止",
                        "in_progress": "进行中",
                        "pending": "待开始"
                    }.get(session_info.get("status", ""), "未知")

                    candidate = session_info.get("candidate_name", "Unknown")
                    email = session_info.get("candidate_email", "")
                    turns = session_info.get("turn_count", 0)
                    date = session_info.get("date", "")
                    session_id = session_info.get("session_id", "")
                    grade = session_info.get("grade")
                    score = session_info.get("score")
                    is_s_tier = session_info.get("is_s_tier", False)

                    # Grade badge styling
                    grade_badge = ""
                    if grade:
                        grade_colors = {
                            "S": ("linear-gradient(135deg, #FCD34D, #F59E0B)", "#78350F"),
                            "A": ("linear-gradient(135deg, #34D399, #10B981)", "#064E3B"),
                            "B": ("linear-gradient(135deg, #60A5FA, #3B82F6)", "#1E3A8A"),
                            "C": ("linear-gradient(135deg, #F87171, #EF4444)", "#7F1D1D")
                        }
                        bg, color = grade_colors.get(grade, ("#9CA3AF", "#374151"))
                        score_text = f" {score}分" if score else ""
                        grade_badge = f'<span style="background: {bg}; color: {color}; padding: 0.125rem 0.375rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700;">{grade}{score_text}</span>'
                    else:
                        grade_badge = '<span style="background: #6B7280; color: white; padding: 0.125rem 0.375rem; border-radius: 4px; font-size: 0.7rem;">待评估</span>'

                    # Generate detail URL
                    import os
                    base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")
                    detail_url = f"{base_url}/?session={session_id}"

                    st.markdown(f"""
                    <div style="
                        background: rgba(255,255,255,0.1);
                        padding: 0.75rem;
                        border-radius: 8px;
                        margin-bottom: 0.5rem;
                        font-size: 0.8rem;
                        border-left: 3px solid {'#F59E0B' if is_s_tier else '#0D9488'};
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                            <span style="font-weight: 600;">{candidate}</span>
                            {grade_badge}
                        </div>
                        <div style="opacity: 0.7; font-size: 0.7rem; margin-bottom: 0.25rem;">
                            {email}
                        </div>
                        <div style="opacity: 0.6; font-size: 0.7rem; margin-bottom: 0.25rem;">
                            {date} | {turns} 轮 | {status_indicator}
                        </div>
                        <a href="{detail_url}" target="_blank" style="
                            color: #5EEAD4;
                            font-size: 0.75rem;
                            text-decoration: none;
                        ">查看详情 →</a>
                    </div>
                    """, unsafe_allow_html=True)

                    # Delete button for each record
                    col_del, col_space = st.columns([1, 2])
                    with col_del:
                        delete_key = f"delete_session_{session_id}_{idx}"
                        if st.button("删除", key=delete_key, use_container_width=True):
                            st.session_state[f"_confirm_delete_session_{session_id}"] = date

                    # Confirm delete single session
                    if st.session_state.get(f"_confirm_delete_session_{session_id}"):
                        st.warning(f"确定要删除 {candidate} 的面试记录吗？")
                        col_y, col_n = st.columns(2)
                        with col_y:
                            if st.button("确定", key=f"confirm_del_{session_id}_{idx}", use_container_width=True):
                                storage_service.delete_session_by_date_str(session_id, date)
                                st.session_state[f"_confirm_delete_session_{session_id}"] = None
                                st.toast(f"已删除 {candidate} 的记录")
                                st.rerun()
                        with col_n:
                            if st.button("取消", key=f"cancel_del_{session_id}_{idx}", use_container_width=True):
                                st.session_state[f"_confirm_delete_session_{session_id}"] = None
                                st.rerun()
        else:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 1rem;
                opacity: 0.8;
                color: #CCFBF1;
            ">
                <p style="margin: 0 0 0.5rem 0;">暂无面试记录</p>
                <p style="margin: 0; font-size: 0.75rem; opacity: 0.7;">
                    生成面试链接并发送给候选人后<br>记录将显示在这里
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ===========================================
        # API Status
        # ===========================================
        plug_icon = icon("plug", size=20, color="#CCFBF1")
        st.markdown(f"### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{plug_icon} API 状态</span>", unsafe_allow_html=True)

        api_key = Settings.GEMINI_API_KEY
        if api_key:
            # Only show status indicator, not partial key (security best practice)
            check_icon = icon("check-circle", size=16, color="#10B981")
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 0.75rem;
                background: rgba(16, 185, 129, 0.15);
                border-radius: 8px;
                border: 1px solid rgba(16, 185, 129, 0.3);
            ">
                {check_icon}
                <span style="color: #10B981; font-weight: 500;">API Key 已配置</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            alert_icon = icon("alert-triangle", size=16, color="#F59E0B")
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 0.75rem;
                background: rgba(245, 158, 11, 0.15);
                border-radius: 8px;
                border: 1px solid rgba(245, 158, 11, 0.3);
            ">
                {alert_icon}
                <span style="color: #F59E0B; font-weight: 500;">未配置 API Key</span>
            </div>
            """, unsafe_allow_html=True)
            st.caption("请在 .env 文件中设置 GEMINI_API_KEY")

        st.divider()

        # ===========================================
        # Footer Info
        # ===========================================
        st.markdown("""
        <div style="text-align: center; font-size: 0.75rem; opacity: 0.6; margin-top: 1rem;">
            <p>© 2026 VoiVerse</p>
        </div>
        """, unsafe_allow_html=True)

    # Return configuration
    return {
        "job_description": job_description,
        "job_title": job_title,
        "s_tier_invitation": s_tier_invitation,
        "s_tier_link": s_tier_link,
        "feishu_webhook": feishu_webhook,
        "config_id": st.session_state.get("current_config_id")
    }


def init_admin_sidebar_state():
    """Initialize admin sidebar session state with defaults"""
    defaults = {
        "job_description": "",
        "job_title": "",
        "custom_greeting": "",
        "s_tier_invitation": "请直接添加 CTO 微信：VoiCTO",
        "s_tier_link": "",
        "feishu_webhook": "",
        "current_config_id": None,
        "generated_url": None,
        "_last_selected_config": None,
        "_confirm_delete": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Keep old function names for backward compatibility
render_sidebar = render_admin_sidebar
init_sidebar_state = init_admin_sidebar_state
