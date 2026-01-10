"""
HR Admin Dashboard - 2026 Bento Grid Layout

Design System:
- Bento Grid: 模块化网格布局
- Glassmorphism: 毛玻璃卡片效果
- 大字体 + 渐变色
- 微动效 + 悬停交互
"""
import streamlit as st
from typing import Optional, Callable
import os

from components.styles import icon
from services.company_config_service import company_config_service
from services.job_config_service import job_config_service, create_job_config
from services.storage_service import storage_service

# Bento Grid CSS
BENTO_CSS = """
<style>
/* Prevent scroll reset on tab switch */
html {
    scroll-behavior: auto !important;
}

/* Bento Grid Container */
.bento-grid {
    display: grid;
    gap: 1rem;
    margin: 1rem 0;
}

.bento-2col { grid-template-columns: repeat(2, 1fr); }
.bento-3col { grid-template-columns: repeat(3, 1fr); }
.bento-4col { grid-template-columns: repeat(4, 1fr); }

/* Glassmorphism Card */
.glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 20px;
    padding: 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
}

.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(13, 148, 136, 0.15);
    border-color: rgba(13, 148, 136, 0.3);
}

/* Metric Card - Big Numbers */
.metric-card {
    text-align: center;
    padding: 1.5rem 1rem;
}

.metric-value {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, var(--color-start), var(--color-end));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 0.875rem;
    color: #64748B;
    margin-top: 0.5rem;
    font-weight: 500;
}

/* Section Title */
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-title svg {
    color: #0D9488;
}

/* Input Card */
.input-card {
    background: white;
    border-radius: 16px;
    padding: 1.25rem;
    border: 1px solid #E2E8F0;
    margin-bottom: 1rem;
}

.input-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

/* Gradient Header */
.gradient-header {
    background: linear-gradient(135deg, #0D9488 0%, #0F766E 50%, #134E4A 100%);
    border-radius: 24px;
    padding: 2rem;
    color: white;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.gradient-header::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    pointer-events: none;
}

.header-title {
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
}

.header-subtitle {
    opacity: 0.8;
    margin-top: 0.25rem;
    font-size: 1rem;
}

/* Link Card */
.link-card {
    background: linear-gradient(135deg, #F0FDFA, #CCFBF1);
    border: 2px dashed #0D9488;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}

/* Badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Animation */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-in {
    animation: slideUp 0.5s ease-out forwards;
}

/* Responsive - Mobile First */
@media (max-width: 480px) {
    /* iPhone SE, small phones */
    .bento-2col, .bento-3col, .bento-4col {
        grid-template-columns: 1fr;
        gap: 0.75rem;
    }
    .metric-value { font-size: 1.75rem; }
    .header-title { font-size: 1.25rem; }
    .header-subtitle { font-size: 0.875rem; }
    .gradient-header { padding: 1.25rem; border-radius: 16px; }
    .glass-card { padding: 1rem; border-radius: 14px; }
    .section-title { font-size: 1rem; }
    .metric-card { padding: 1rem 0.75rem; }
    .metric-label { font-size: 0.75rem; }
}

@media (min-width: 481px) and (max-width: 768px) {
    /* Tablets portrait, large phones */
    .bento-4col { grid-template-columns: repeat(2, 1fr); }
    .bento-3col { grid-template-columns: repeat(2, 1fr); }
    .bento-2col { grid-template-columns: 1fr; }
    .metric-value { font-size: 2.25rem; }
    .header-title { font-size: 1.5rem; }
    .gradient-header { padding: 1.5rem; border-radius: 20px; }
    .glass-card { padding: 1.25rem; border-radius: 16px; }
}

@media (min-width: 769px) and (max-width: 1024px) {
    /* Tablets landscape, small laptops */
    .bento-4col { grid-template-columns: repeat(4, 1fr); }
    .metric-value { font-size: 2.5rem; }
}

/* Apple Device Optimizations */
@supports (-webkit-touch-callout: none) {
    /* iOS Safari specific */
    .glass-card {
        -webkit-backdrop-filter: blur(20px);
        backdrop-filter: blur(20px);
    }

    /* Fix iOS input zoom */
    input, select, textarea {
        font-size: 16px !important;
    }

    /* Smooth momentum scrolling */
    .bento-grid {
        -webkit-overflow-scrolling: touch;
    }
}

/* Safe area for notched devices (iPhone X+) */
@supports (padding: max(0px)) {
    .gradient-header {
        padding-left: max(2rem, env(safe-area-inset-left));
        padding-right: max(2rem, env(safe-area-inset-right));
    }

    .glass-card {
        margin-left: max(0px, env(safe-area-inset-left));
        margin-right: max(0px, env(safe-area-inset-right));
    }
}

/* Touch-friendly targets (44px minimum for iOS) */
@media (pointer: coarse) {
    button, .status-badge, a {
        min-height: 44px;
        min-width: 44px;
    }

    .status-badge {
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
    }
}

/* High DPI / Retina displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    .glass-card {
        border-width: 0.5px;
    }

    .gradient-header::after {
        opacity: 0.8;
    }
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
    .glass-card, .animate-in {
        animation: none;
        transition: none;
    }

    .glass-card:hover {
        transform: none;
    }
}

/* Landscape phone optimization */
@media (max-height: 500px) and (orientation: landscape) {
    .gradient-header {
        padding: 1rem 1.5rem;
    }

    .header-title { font-size: 1.25rem; }
    .metric-value { font-size: 1.5rem; }

    .bento-4col {
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
    }

    .metric-card { padding: 0.75rem 0.5rem; }
}

/* iPad specific */
@media (min-width: 768px) and (max-width: 1024px) and (-webkit-min-device-pixel-ratio: 2) {
    .bento-4col { grid-template-columns: repeat(4, 1fr); }
    .bento-2col { grid-template-columns: repeat(2, 1fr); }

    .glass-card {
        padding: 1.5rem;
        border-radius: 18px;
    }

    .gradient-header {
        border-radius: 22px;
    }
}
</style>
"""


def render_header():
    """Render gradient header with logo"""
    st.markdown(BENTO_CSS, unsafe_allow_html=True)

    # JavaScript to preserve scroll position on tab switch
    st.markdown("""
    <script>
    (function() {
        const SCROLL_KEY = 'vv_scroll_pos';

        // Save scroll position
        const saveScroll = () => {
            sessionStorage.setItem(SCROLL_KEY, window.scrollY.toString());
        };

        // Restore scroll position
        const restoreScroll = () => {
            const pos = sessionStorage.getItem(SCROLL_KEY);
            if (pos && parseInt(pos) > 0) {
                requestAnimationFrame(() => {
                    window.scrollTo({ top: parseInt(pos), behavior: 'instant' });
                });
            }
        };

        // Listen for any click that might trigger rerun
        document.addEventListener('click', (e) => {
            const tab = e.target.closest('[data-baseweb="tab"]');
            const button = e.target.closest('button');
            if (tab || button) {
                saveScroll();
            }
        }, true);

        // Restore immediately and after delays
        restoreScroll();
        setTimeout(restoreScroll, 50);
        setTimeout(restoreScroll, 150);
        setTimeout(restoreScroll, 300);

        // Watch for DOM changes (Streamlit rerenders)
        const observer = new MutationObserver(() => {
            restoreScroll();
        });
        observer.observe(document.body, { childList: true, subtree: true });

        // Clean up after 2 seconds
        setTimeout(() => observer.disconnect(), 2000);
    })();
    </script>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gradient-header animate-in">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
                    </svg>
                    <span class="header-title">VoiVerse</span>
                </div>
                <div class="header-subtitle">AI 智能面试 · HR 管理后台</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics():
    """Render KPI metric cards with glassmorphism"""
    grade_counts = storage_service.get_grade_counts(days=7)
    total = sum(grade_counts.values())
    configs = job_config_service.list_configs(active_only=True)

    st.markdown(f"""
    <div class="bento-grid bento-4col" style="animation-delay: 0.1s;">
        <div class="glass-card metric-card" style="--color-start: #0D9488; --color-end: #134E4A;">
            <div class="metric-value">{total}</div>
            <div class="metric-label">7天面试总数</div>
        </div>
        <div class="glass-card metric-card" style="--color-start: #F59E0B; --color-end: #D97706;">
            <div class="metric-value">{grade_counts['S']}</div>
            <div class="metric-label">S级人才</div>
        </div>
        <div class="glass-card metric-card" style="--color-start: #10B981; --color-end: #059669;">
            <div class="metric-value">{grade_counts['A']}</div>
            <div class="metric-label">A级人才</div>
        </div>
        <div class="glass-card metric-card" style="--color-start: #6366F1; --color-end: #4F46E5;">
            <div class="metric-value">{len(configs)}</div>
            <div class="metric-label">活跃岗位</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_job_config_tab():
    """Render job configuration with Bento Grid layout - no expanders"""

    # Show success messages
    if st.session_state.get("_show_save_success"):
        st.success("岗位配置已保存")
        st.session_state._show_save_success = False
    if st.session_state.get("_show_copy_success"):
        st.success("岗位配置已复制")
        st.session_state._show_copy_success = False
    if st.session_state.get("_show_create_success"):
        st.success("面试链接已生成")
        st.session_state._show_create_success = False
    if st.session_state.get("_show_delete_success"):
        st.success("岗位配置已删除")
        st.session_state._show_delete_success = False

    # Load existing configs
    existing_configs = job_config_service.list_configs(active_only=True)
    config_options = {"+ 新建岗位": None}
    for c in existing_configs:
        label = c.job_title if c.job_title else c.job_description[:20] + "..."
        config_options[label] = c.config_id

    current_id = st.session_state.get("current_config_id")
    default_idx = 0
    if current_id:
        for i, (_, cid) in enumerate(config_options.items()):
            if cid == current_id:
                default_idx = i
                break

    # Row 1: Job selector + URL display
    col1, col2 = st.columns([2, 1])
    with col1:
        selected = st.selectbox("选择岗位", list(config_options.keys()), index=default_idx, key="job_select")
    with col2:
        pass  # URL will be shown below in a dedicated section

    selected_id = config_options[selected]

    # Handle selection change
    if selected_id != st.session_state.get("_last_config"):
        st.session_state._last_config = selected_id
        if selected_id:
            cfg = job_config_service.load_config(selected_id)
            if cfg:
                st.session_state.job_title = cfg.job_title
                st.session_state.job_description = cfg.job_description
                st.session_state.custom_greeting = cfg.custom_greeting
                st.session_state.s_tier_invitation = cfg.s_tier_invitation
                st.session_state.s_tier_link = cfg.s_tier_link
                st.session_state.feishu_webhook = cfg.feishu_webhook
                st.session_state.test_mode = cfg.test_mode
                st.session_state.current_config_id = selected_id
                st.session_state.generated_url = cfg.get_interview_url()
        else:
            st.session_state.job_title = ""
            st.session_state.job_description = ""
            st.session_state.custom_greeting = ""
            st.session_state.s_tier_invitation = "请直接添加 CTO 微信：VoiCTO"
            st.session_state.s_tier_link = ""
            st.session_state.feishu_webhook = ""
            st.session_state.test_mode = False
            st.session_state.current_config_id = None
            st.session_state.generated_url = None

    # Bento Grid: 2 columns layout
    col_left, col_right = st.columns(2)

    with col_left:
        # 岗位基本信息
        st.markdown(f'<div class="section-title">{icon("clipboard", 20)} 岗位信息</div>', unsafe_allow_html=True)
        job_title = st.text_input("岗位名称", value=st.session_state.get("job_title", ""), placeholder="高级 Go 开发工程师")
        job_desc = st.text_area("岗位描述 (JD)", value=st.session_state.get("job_description", ""), height=120, placeholder="技术要求、工作职责...")
        custom_greeting = st.text_area("自定义开场白", value=st.session_state.get("custom_greeting", ""), height=60, placeholder="留空则AI自动生成")

    with col_right:
        # S级人才 + 通知设置
        st.markdown(f'<div class="section-title">{icon("star", 20)} S级人才邀请</div>', unsafe_allow_html=True)
        s_tier_inv = st.text_area("邀请文案", value=st.session_state.get("s_tier_invitation", "请直接添加 CTO 微信：VoiCTO"), height=60)
        s_tier_link = st.text_input("预约链接", value=st.session_state.get("s_tier_link", ""), placeholder="https://calendly.com/...")

        st.markdown(f'<div class="section-title" style="margin-top:1rem;">{icon("bell", 20)} 通知设置</div>', unsafe_allow_html=True)
        feishu = st.text_input("飞书 Webhook", value=st.session_state.get("feishu_webhook", ""), type="password", placeholder="https://open.feishu.cn/...")
        test_mode = st.toggle("测试模式 (输入 /stop 结束)", value=st.session_state.get("test_mode", False))

    # Update session state
    st.session_state.job_title = job_title
    st.session_state.job_description = job_desc
    st.session_state.custom_greeting = custom_greeting
    st.session_state.s_tier_invitation = s_tier_inv
    st.session_state.s_tier_link = s_tier_link
    st.session_state.feishu_webhook = feishu
    st.session_state.test_mode = test_mode

    # Action buttons row
    can_save = bool(job_desc and job_desc.strip())
    st.markdown("<br>", unsafe_allow_html=True)

    if selected_id:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("保存", use_container_width=True, type="primary", disabled=not can_save):
                cfg = job_config_service.load_config(selected_id)
                if cfg:
                    cfg.job_title = job_title
                    cfg.job_description = job_desc
                    cfg.custom_greeting = custom_greeting
                    cfg.s_tier_invitation = s_tier_inv
                    cfg.s_tier_link = s_tier_link
                    cfg.feishu_webhook = feishu
                    cfg.test_mode = test_mode
                    job_config_service.update_config(cfg)
                    st.session_state.generated_url = cfg.get_interview_url()
                    st.session_state._show_save_success = True
                    st.rerun()
        with c2:
            if st.button("复制", use_container_width=True):
                new_cfg = create_job_config(job_desc, f"{job_title} (副本)", custom_greeting, s_tier_inv, s_tier_link, feishu)
                st.session_state.current_config_id = new_cfg.config_id
                st.session_state._last_config = new_cfg.config_id
                st.session_state.generated_url = new_cfg.get_interview_url()
                st.session_state._show_copy_success = True
                st.rerun()
        with c3:
            if st.button("删除", use_container_width=True):
                st.session_state._confirm_del = selected_id
        with c4:
            pass  # spacer

        if st.session_state.get("_confirm_del") == selected_id:
            st.warning("确定删除此岗位配置？")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("确定删除", key="yes_del"):
                    job_config_service.delete_config(selected_id)
                    st.session_state.current_config_id = None
                    st.session_state._last_config = None
                    st.session_state.generated_url = None
                    st.session_state._confirm_del = None
                    st.session_state._show_delete_success = True
                    st.rerun()
            with cc2:
                if st.button("取消", key="no_del"):
                    st.session_state._confirm_del = None
                    st.rerun()
    else:
        if st.button("生成面试链接", use_container_width=True, type="primary", disabled=not can_save):
            cfg = create_job_config(job_desc, job_title, custom_greeting, s_tier_inv, s_tier_link, feishu, test_mode)
            st.session_state.current_config_id = cfg.config_id
            st.session_state._last_config = cfg.config_id
            st.session_state.generated_url = cfg.get_interview_url()
            st.session_state._show_create_success = True
            st.rerun()

    # URL Display Section with Copy Button
    if st.session_state.get("generated_url"):
        st.markdown("<br>", unsafe_allow_html=True)
        url = st.session_state.generated_url

        # Create unique ID for this URL element
        copy_id = "url_copy_target"

        st.markdown(f"""
        <div class="glass-card" style="background: linear-gradient(135deg, #F0FDFA, #CCFBF1); border: 2px solid #0D9488;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    {icon("arrow-right", 20, "#0D9488")}
                    <span style="font-weight: 700; color: #134E4A;">面试链接已生成</span>
                </div>
                <button onclick="copyToClipboard()" style="
                    background: #0D9488;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 0.25rem;
                    font-size: 0.8rem;
                    transition: all 0.2s;
                " onmouseover="this.style.background='#0F766E'" onmouseout="this.style.background='#0D9488'">
                    {icon("clipboard", 16, "white")}
                    复制链接
                </button>
            </div>
            <div id="{copy_id}" style="background: white; border-radius: 8px; padding: 0.75rem 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #0F766E; word-break: break-all; border: 1px solid #99F6E4; user-select: all;">
                {url}
            </div>
            <div id="copy_feedback" style="margin-top: 0.5rem; font-size: 0.75rem; color: #64748B; display: none;">
                已复制到剪贴板
            </div>
            <div style="margin-top: 0.75rem; font-size: 0.8rem; color: #64748B;">
                发送此链接给候选人即可开始 AI 面试
            </div>
        </div>
        <script>
        function copyToClipboard() {{
            const url = "{url}";
            navigator.clipboard.writeText(url).then(function() {{
                const feedback = document.getElementById('copy_feedback');
                feedback.style.display = 'block';
                feedback.style.color = '#059669';
                feedback.textContent = '已复制到剪贴板';
                setTimeout(function() {{ feedback.style.display = 'none'; }}, 2000);
            }}).catch(function() {{
                // Fallback: select text for manual copy
                const el = document.getElementById('{copy_id}');
                const range = document.createRange();
                range.selectNodeContents(el);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                const feedback = document.getElementById('copy_feedback');
                feedback.style.display = 'block';
                feedback.style.color = '#D97706';
                feedback.textContent = '请按 Ctrl+C 复制';
            }});
        }}
        </script>
        """, unsafe_allow_html=True)


def render_history_tab():
    """Render interview history with modern cards"""
    grade_counts = storage_service.get_grade_counts(days=7)
    total = sum(grade_counts.values())

    # Stats row with grade badges
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">
            最近 7 天 · <span style="color: #0D9488;">{total}</span> 条记录
        </div>
        <div style="display: flex; gap: 0.5rem;">
            <span class="status-badge" style="background: linear-gradient(135deg, #FCD34D, #F59E0B); color: #78350F;">S: {grade_counts['S']}</span>
            <span class="status-badge" style="background: linear-gradient(135deg, #34D399, #10B981); color: #064E3B;">A: {grade_counts['A']}</span>
            <span class="status-badge" style="background: linear-gradient(135deg, #60A5FA, #3B82F6); color: #1E3A8A;">B: {grade_counts['B']}</span>
            <span class="status-badge" style="background: linear-gradient(135deg, #F87171, #EF4444); color: #7F1D1D;">C: {grade_counts['C']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter
    filter_opts = {"全部": None, "S级": "S", "A级": "A", "B级": "B", "C级": "C", "待评估": "pending"}
    selected_filter = st.selectbox("筛选等级", list(filter_opts.keys()), key="grade_filter", label_visibility="collapsed")
    grade_filter = filter_opts[selected_filter]

    # Get sessions
    if grade_filter == "pending":
        sessions = [s for s in storage_service.get_recent_sessions(days=7) if s.get("grade") is None]
    else:
        sessions = storage_service.get_recent_sessions(days=7, grade_filter=grade_filter)

    if not sessions:
        st.info("暂无面试记录")
        return

    # Session cards
    for idx, s in enumerate(sessions[:30]):
        grade = s.get("grade")
        score = s.get("score")
        is_s = s.get("is_s_tier", False)

        # Grade badge
        if grade:
            colors = {"S": ("#F59E0B", "#FEF3C7"), "A": ("#10B981", "#ECFDF5"), "B": ("#3B82F6", "#EFF6FF"), "C": ("#EF4444", "#FEF2F2")}
            fg, bg = colors.get(grade, ("#6B7280", "#F3F4F6"))
            score_txt = f" · {score}分" if score else ""
            badge_html = f'<span style="background: {bg}; color: {fg}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">{grade}级{score_txt}</span>'
        else:
            badge_html = '<span style="background: #F3F4F6; color: #6B7280; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem;">待评估</span>'

        base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")
        detail_url = f"{base_url}/?session={s.get('session_id', '')}"
        border_color = "#F59E0B" if is_s else "#E2E8F0"

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; border-left: 4px solid {border_color}; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: 700; font-size: 1rem; color: #0F172A;">{s.get('candidate_name', 'Unknown')}</span>
                        <span style="color: #64748B; font-size: 0.8rem; margin-left: 0.75rem;">{s.get('candidate_email', '')}</span>
                    </div>
                    {badge_html}
                </div>
                <div style="color: #64748B; font-size: 0.75rem; margin-top: 0.5rem;">
                    {s.get('date', '')} · {s.get('turn_count', 0)} 轮对话
                    <a href="{detail_url}" target="_blank" style="color: #0D9488; margin-left: 1rem; text-decoration: none;">查看详情 →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("删除", key=f"del_{s.get('session_id')}_{idx}"):
                storage_service.delete_session_by_date_str(s.get('session_id', ''), s.get('date', ''))
                st.toast("已删除")
                st.rerun()

    # Clear all
    if total > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("清空所有记录", use_container_width=True):
            st.session_state._confirm_clear = True

        if st.session_state.get("_confirm_clear"):
            st.warning(f"确定清空 {total} 条记录？此操作不可恢复！")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("确定清空", key="yes_clear"):
                    storage_service.clear_all_sessions(days=7)
                    st.session_state._confirm_clear = False
                    st.toast("已清空")
                    st.rerun()
            with c2:
                if st.button("取消", key="no_clear"):
                    st.session_state._confirm_clear = False
                    st.rerun()


def render_settings_tab():
    """Render settings with Bento layout"""
    from config.settings import Settings

    col1, col2 = st.columns(2)

    with col1:
        # 公司信息
        st.markdown(f'<div class="section-title">{icon("building", 20)} 公司信息</div>', unsafe_allow_html=True)
        existing = company_config_service.get_config()
        if "company_background" not in st.session_state:
            st.session_state.company_background = existing.company_background

        bg = st.text_area("公司背景", value=st.session_state.get("company_background", ""), height=120, placeholder="公司背景、文化、招聘目标...")
        st.session_state.company_background = bg

        if st.button("保存公司信息", use_container_width=True):
            if bg.strip():
                company_config_service.update_background(bg.strip())
                st.toast("已保存")

    with col2:
        # API 状态
        st.markdown(f'<div class="section-title">{icon("plug", 20)} API 状态</div>', unsafe_allow_html=True)
        if Settings.GEMINI_API_KEY:
            st.markdown(f"""
            <div class="glass-card" style="background: linear-gradient(135deg, #ECFDF5, #D1FAE5); border-color: #10B981;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    {icon("check-circle", 24, "#059669")}
                    <div>
                        <div style="font-weight: 700; color: #059669;">Gemini API 已连接</div>
                        <div style="font-size: 0.8rem; color: #047857;">模型: Gemini 3.0 Flash / Pro</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="glass-card" style="background: linear-gradient(135deg, #FEF3C7, #FDE68A); border-color: #F59E0B;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    {icon("alert-triangle", 24, "#D97706")}
                    <div>
                        <div style="font-weight: 700; color: #D97706;">未配置 API Key</div>
                        <div style="font-size: 0.8rem; color: #92400E;">请在 .env 文件中设置 GEMINI_API_KEY</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 关于
        st.markdown(f'<div class="section-title" style="margin-top: 1.5rem;">{icon("info", 20)} 关于</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight: 700; font-size: 1.1rem; color: #0F172A; margin-bottom: 0.5rem;">VoiVerse AI 面试系统</div>
            <div style="color: #64748B; font-size: 0.875rem; line-height: 1.6;">
                • 基于 Gemini 3.0 的智能面试平台<br>
                • 自动评估候选人 (S/A/B/C)<br>
                • 飞书实时通知<br>
                • STAR 法则追问
            </div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #E2E8F0; font-size: 0.75rem; color: #94A3B8;">
                © 2026 VoiVerse · Powered by Gemini
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_admin_dashboard():
    """Main admin dashboard with Bento Grid layout"""
    render_header()
    render_metrics()

    st.markdown("<br>", unsafe_allow_html=True)

    # Tab navigation with icons
    tab1, tab2, tab3 = st.tabs(["岗位配置", "面试历史", "设置"])

    with tab1:
        render_job_config_tab()

    with tab2:
        render_history_tab()

    with tab3:
        render_settings_tab()


def init_admin_dashboard_state():
    """Initialize dashboard session state"""
    defaults = {
        "job_description": "",
        "job_title": "",
        "custom_greeting": "",
        "s_tier_invitation": "请直接添加 CTO 微信：VoiCTO",
        "s_tier_link": "",
        "feishu_webhook": "",
        "current_config_id": None,
        "generated_url": None,
        "_last_config": None,
        "_confirm_del": None,
        "_confirm_clear": None,
        "test_mode": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
