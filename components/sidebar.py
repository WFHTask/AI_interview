"""
Sidebar Component for HR Admin Configuration

Provides interface for:
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
        # Logo/Title with SVG icon
        target_icon = icon("target", size=24, color="#FFFFFF")
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h1 style="font-size: 1.5rem; margin: 0; display: inline-flex; align-items: center; gap: 0.5rem; justify-content: center;">
                {target_icon}
                VoiVerse
            </h1>
            <p style="font-size: 0.875rem; opacity: 0.8; margin: 0;">HR 管理后台</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ===========================================
        # Existing Job Configurations
        # ===========================================
        folder_icon = icon("clipboard", size=20, color="#CCFBF1")
        st.markdown(f"### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{folder_icon} 岗位配置</span>", unsafe_allow_html=True)

        # Load existing configs
        from services.job_config_service import job_config_service
        existing_configs = job_config_service.list_configs(active_only=True)

        # Build options
        config_options = {"-- 新建配置 --": None}
        if existing_configs:
            for c in existing_configs:
                label = c.job_title if c.job_title else c.job_description[:20] + "..."
                config_options[f"{label} ({c.config_id})"] = c.config_id

        # Determine current selection index
        current_config_id = st.session_state.get("current_config_id")
        default_index = 0
        if current_config_id:
            for i, (_, cid) in enumerate(config_options.items()):
                if cid == current_config_id:
                    default_index = i
                    break

        selected_option = st.selectbox(
            "选择已有配置或新建",
            options=list(config_options.keys()),
            index=default_index,
            key="config_selector"
        )

        selected_config_id = config_options[selected_option]

        # Track edit mode
        is_editing = selected_config_id is not None
        is_new = selected_config_id is None

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
                st.session_state.current_config_id = None
                st.session_state.generated_url = None

        # Show config info if editing
        if is_editing:
            selected_config = job_config_service.load_config(selected_config_id)
            if selected_config:
                st.info(f"编辑模式 | 已面试 {selected_config.interview_count} 人")

        st.divider()

        # ===========================================
        # Job Description Section
        # ===========================================
        edit_icon = icon("file-text", size=20, color="#CCFBF1")
        st.markdown(f"### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{edit_icon} 岗位信息</span>", unsafe_allow_html=True)

        job_title = st.text_input(
            "岗位名称",
            value=st.session_state.get("job_title", ""),
            placeholder="例如：高级 Go 开发工程师",
            key="job_title_input"
        )

        job_description = st.text_area(
            "岗位描述 (JD)",
            value=st.session_state.get("job_description", ""),
            height=150,
            placeholder="请输入岗位描述...\n\n例如：\n- 技术要求：精通 Golang、熟悉微服务架构\n- 工作职责：负责核心系统开发...",
            key="jd_input"
        )

        # Custom greeting
        with st.expander("自定义面试官开场白 (可选)", expanded=False):
            custom_greeting = st.text_area(
                "开场白内容",
                value=st.session_state.get("custom_greeting", ""),
                height=100,
                placeholder="留空则使用 AI 自动生成的开场白。\n\n例如：\n您好！我是 VoiVerse 的 AI 面试官。今天我们将围绕高级 Go 开发工程师岗位进行交流...",
                key="custom_greeting_input"
            )
            st.caption("如果填写，AI 面试官将使用此内容作为第一句话")
            st.session_state.custom_greeting = custom_greeting

        # Save to session state
        st.session_state.job_description = job_description
        st.session_state.job_title = job_title

        st.divider()

        # ===========================================
        # S-Tier Configuration
        # ===========================================
        star_icon = icon("star", size=20, color="#F59E0B")
        st.markdown(f"### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{star_icon} S 级人才配置</span>", unsafe_allow_html=True)

        s_tier_invitation = st.text_area(
            "邀请文案",
            value=st.session_state.get("s_tier_invitation", "请直接添加 CTO 微信：VoiCTO"),
            height=80,
            placeholder="S 级人才专属邀请文案...",
            key="s_tier_invitation_input"
        )

        s_tier_link = st.text_input(
            "预约链接 (可选)",
            value=st.session_state.get("s_tier_link", ""),
            placeholder="https://calendly.com/...",
            key="s_tier_link_input"
        )

        st.session_state.s_tier_invitation = s_tier_invitation
        st.session_state.s_tier_link = s_tier_link

        st.divider()

        # ===========================================
        # Notification Configuration
        # ===========================================
        bell_icon = icon("bell", size=20, color="#CCFBF1")
        st.markdown(f"### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{bell_icon} 通知配置</span>", unsafe_allow_html=True)

        feishu_webhook = st.text_input(
            "飞书 Webhook URL",
            value=st.session_state.get("feishu_webhook", ""),
            type="password",
            placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/...",
            key="feishu_webhook_input"
        )

        st.session_state.feishu_webhook = feishu_webhook

        # Test connection button
        if feishu_webhook:
            if st.button("测试连接", use_container_width=True, key="test_feishu"):
                with st.spinner("测试中..."):
                    try:
                        from services.feishu_service import FeishuService
                        service = FeishuService(feishu_webhook)
                        if service.test_connection():
                            st.success("连接成功!")
                        else:
                            st.error("连接失败")
                    except Exception as e:
                        st.error(f"错误: {str(e)}")

        st.divider()

        # ===========================================
        # Action Buttons
        # ===========================================
        action_icon = icon("zap", size=20, color="#CCFBF1")
        st.markdown(f"### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{action_icon} 操作</span>", unsafe_allow_html=True)

        # Validation check
        can_save = bool(job_description and job_description.strip())

        # Use selected_config_id directly for button logic
        if selected_config_id:
            # Editing existing config
            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "保存修改",
                    use_container_width=True,
                    disabled=not can_save,
                    type="primary",
                    key="save_config_btn"
                ):
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

                            job_config_service.update_config(existing)
                            st.session_state.generated_url = existing.get_interview_url()
                            st.toast("配置已保存")
                            st.rerun()

            with col2:
                if st.button(
                    "复制为新配置",
                    use_container_width=True,
                    key="duplicate_config_btn"
                ):
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
                    st.toast("已复制为新配置")
                    st.rerun()

            # Delete button
            if st.button(
                "删除配置",
                use_container_width=True,
                key="delete_config_btn"
            ):
                st.session_state._confirm_delete = selected_config_id

            # Confirm delete dialog
            if st.session_state.get("_confirm_delete") == selected_config_id:
                st.warning("确定要删除此配置吗？")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("确定删除", use_container_width=True, key="confirm_delete"):
                        job_config_service.delete_config(selected_config_id)
                        st.session_state.current_config_id = None
                        st.session_state._last_selected_config = None
                        st.session_state.generated_url = None
                        st.session_state._confirm_delete = None
                        st.toast("配置已删除")
                        st.rerun()
                with col_no:
                    if st.button("取消", use_container_width=True, key="cancel_delete"):
                        st.session_state._confirm_delete = None
                        st.rerun()

            # Show interview link
            if st.session_state.get("generated_url"):
                st.divider()
                st.success("面试链接")
                st.code(st.session_state.generated_url, language=None)
                st.caption("将此链接发送给候选人")

        else:
            # Creating new config
            if st.button(
                "生成面试链接",
                use_container_width=True,
                disabled=not can_save,
                type="primary",
                key="generate_link_btn"
            ):
                if can_save:
                    from services.job_config_service import create_job_config

                    config = create_job_config(
                        job_description=job_description,
                        job_title=job_title,
                        custom_greeting=custom_greeting,
                        s_tier_invitation=s_tier_invitation,
                        s_tier_link=s_tier_link,
                        feishu_webhook=feishu_webhook
                    )

                    st.session_state.current_config_id = config.config_id
                    st.session_state._last_selected_config = config.config_id
                    st.session_state.generated_url = config.get_interview_url()

                    if on_generate_link:
                        on_generate_link()

                    st.toast("配置已创建")
                    st.rerun()

            if not can_save:
                st.caption("请先填写岗位描述")

            # Show generated URL for newly created
            if st.session_state.get("generated_url"):
                st.success("链接已生成！")
                st.code(st.session_state.generated_url, language=None)
                st.caption("将此链接发送给候选人")

        st.divider()

        # ===========================================
        # Interview History
        # ===========================================
        history_icon = icon("clock", size=20, color="#CCFBF1")
        st.markdown(f"### <span style='display: inline-flex; align-items: center; gap: 0.5rem;'>{history_icon} 面试历史</span>", unsafe_allow_html=True)

        from services.storage_service import storage_service

        recent_sessions = storage_service.get_recent_sessions(days=7)

        if recent_sessions:
            st.caption(f"最近 7 天: {len(recent_sessions)} 条记录")

            with st.expander("查看历史记录", expanded=False):
                for session_info in recent_sessions[:10]:
                    status_indicator = {
                        "completed": "[完成]",
                        "terminated": "[终止]",
                        "in_progress": "[进行中]",
                        "pending": "[待开始]"
                    }.get(session_info.get("status", ""), "[未知]")

                    candidate = session_info.get("candidate_name", "Unknown")
                    turns = session_info.get("turn_count", 0)
                    date = session_info.get("date", "")
                    session_id = session_info.get("session_id", "")

                    st.markdown(f"""
                    <div style="
                        background: rgba(255,255,255,0.1);
                        padding: 0.5rem;
                        border-radius: 6px;
                        margin-bottom: 0.5rem;
                        font-size: 0.8rem;
                    ">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: 600;">{candidate}</span>
                            <span style="opacity: 0.7;">{status_indicator}</span>
                        </div>
                        <div style="opacity: 0.6; font-size: 0.75rem;">
                            {date} | {turns} 轮 | ID: {session_id}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
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
            <p>Powered by Gemini 3.0</p>
            <p>© 2024 VoiVerse</p>
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
