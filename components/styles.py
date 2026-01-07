"""
CSS Styles for AI-HR Interview System

Design Principles:
- Deep Teal color scheme (avoiding purple AI slop)
- DM Sans + Source Sans Pro fonts
- Professional, memorable, non-generic design
- Lucide-style SVG icons (NO emojis)
"""

# =============================================================================
# SVG ICONS (Lucide-style, 24x24 default)
# =============================================================================

# Icon color will inherit from CSS currentColor
ICONS = {
    # Navigation & UI
    "target": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>''',

    "clipboard": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>''',

    "star": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>''',

    "bell": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>''',

    "settings": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>''',

    "play": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>''',

    "refresh": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M3 21v-5h5"/></svg>''',

    "wrench": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>''',

    "plug": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/><path d="M18 8v5a6 6 0 0 1-12 0V8z"/></svg>''',

    "gamepad": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="15" x2="15.01" y1="13" y2="13"/><line x1="18" x2="18.01" y1="11" y2="11"/><rect width="20" height="12" x="2" y="6" rx="2"/></svg>''',

    "clock": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>''',

    # Chat & Communication
    "message": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>''',

    "bot": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>''',

    "user": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/></svg>''',

    "hand-wave": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 15l4-8 4 8"/><path d="M5.2 17.6A7 7 0 0 0 12 21a7 7 0 0 0 6.8-3.4"/><path d="M17 8.8V4a2 2 0 0 0-4 0v6"/><path d="M9 9.5V4a2 2 0 0 0-4 0v8.8"/></svg>''',

    # Status & Results
    "check-circle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>''',

    "x-circle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>''',

    "alert-triangle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>''',

    "info": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>''',

    "flag": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/></svg>''',

    # Analytics & Data
    "bar-chart": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>''',

    "trending-up": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>''',

    "sparkles": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>''',

    "file-text": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>''',

    "brain": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>''',

    "zap": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/></svg>''',

    "arrow-right": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>''',

    "award": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/></svg>''',
}


def icon(
    name: str,
    size: int = 24,
    color: str = "currentColor",
    class_name: str = "",
    aria_label: str = "",
    decorative: bool = True
) -> str:
    """
    Get an SVG icon by name with customizable size, color, and accessibility.

    Args:
        name: Icon name from ICONS dict
        size: Icon size in pixels (default 24)
        color: Icon color (default currentColor for CSS inheritance)
        class_name: Optional CSS class name
        aria_label: Accessible label for screen readers (required if not decorative)
        decorative: If True, icon is decorative and hidden from screen readers

    Returns:
        SVG HTML string with proper accessibility attributes
    """
    svg = ICONS.get(name, ICONS["target"])  # Default to target if not found

    # Replace size
    svg = svg.replace('width="24"', f'width="{size}"')
    svg = svg.replace('height="24"', f'height="{size}"')

    # Replace color if not currentColor
    if color != "currentColor":
        svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
        svg = svg.replace('fill="currentColor"', f'fill="{color}"')

    # Add class if provided
    if class_name:
        svg = svg.replace('<svg ', f'<svg class="{class_name}" ')

    # Add accessibility attributes
    if aria_label and not decorative:
        # Icon has meaning - add role and label
        svg = svg.replace('<svg ', f'<svg role="img" aria-label="{aria_label}" ')
    else:
        # Decorative icon - hide from screen readers
        svg = svg.replace('<svg ', '<svg aria-hidden="true" focusable="false" ')

    return svg


def icon_with_text(name: str, text: str, size: int = 20, gap: str = "0.5rem") -> str:
    """
    Create an icon + text combination with flexbox alignment.

    Args:
        name: Icon name
        text: Text to display
        size: Icon size in pixels
        gap: Gap between icon and text

    Returns:
        HTML string with icon and text
    """
    return f'''<span style="display: inline-flex; align-items: center; gap: {gap};">{icon(name, size)}<span>{text}</span></span>'''


# =============================================================================
# MAIN CSS STYLES
# =============================================================================

MAIN_CSS = """
<style>
/* ============================================
   FONT IMPORTS
   ============================================ */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Source+Sans+Pro:wght@400;600&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&display=swap');

/* ============================================
   ROOT VARIABLES
   ============================================ */
:root {
    --primary: #0D9488;
    --primary-dark: #0F766E;
    --primary-darker: #134E4A;
    --accent: #F59E0B;
    --accent-dark: #D97706;
    --bg-main: #F8FAFC;
    --bg-secondary: #E2E8F0;
    --bg-card: #FFFFFF;
    --text-primary: #1E293B;
    --text-secondary: #475569;
    --text-muted: #6B7280;
    --border: #CBD5E1;
    --success: #10B981;
    --error: #EF4444;
    --warning: #F59E0B;
}

/* ============================================
   GLOBAL STYLES
   ============================================ */
html, body, [class*="css"] {
    font-family: 'Source Sans Pro', 'Noto Sans SC', -apple-system, sans-serif !important;
    color: var(--text-primary);
}

/* Headings */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'DM Sans', 'Noto Sans SC', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    color: var(--text-primary);
}

/* Code blocks */
code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ============================================
   HIDE STREAMLIT DEFAULTS
   ============================================ */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }

/* Keep sidebar toggle button visible */
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: flex !important;
}

/* ============================================
   MAIN CONTAINER
   ============================================ */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* ============================================
   SIDEBAR STYLES
   ============================================ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--primary-darker) 0%, var(--primary-dark) 100%);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #F0FDFA;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] label {
    color: #CCFBF1 !important;
}

[data-testid="stSidebar"] .stTextInput > div > div > input,
[data-testid="stSidebar"] .stTextArea > div > div > textarea {
    background-color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
    color: #1E293B !important;
}

[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder,
[data-testid="stSidebar"] .stTextArea > div > div > textarea::placeholder {
    color: #94A3B8 !important;
}

/* Password input in sidebar */
[data-testid="stSidebar"] input[type="password"] {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
}

/* ============================================
   CHAT MESSAGE STYLES
   ============================================ */
.stChatMessage {
    border-radius: 16px !important;
    padding: 1rem 1.25rem !important;
    margin: 0.75rem 0 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* User messages - right aligned with teal gradient */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    color: white !important;
    margin-left: 15% !important;
    border-bottom-right-radius: 4px !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: white !important;
}

/* AI messages - left aligned with light background */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    margin-right: 15% !important;
    border-bottom-left-radius: 4px !important;
}

/* ============================================
   INPUT STYLES
   ============================================ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 12px !important;
    border: 2px solid var(--border) !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
}

/* Chat input specific */
[data-testid="stChatInput"] {
    border-radius: 16px !important;
    border: 2px solid var(--border) !important;
    background: var(--bg-card) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
}

/* Fix chat input text color - ensure dark text on light background */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input,
[data-testid="stChatInputTextArea"] textarea {
    color: var(--text-primary) !important;
    background-color: var(--bg-card) !important;
    caret-color: var(--text-primary) !important;
}

[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder,
[data-testid="stChatInputTextArea"] textarea::placeholder {
    color: var(--text-muted) !important;
}

/* Disabled input state */
[data-testid="stChatInput"][data-disabled="true"],
[data-testid="stChatInput"].disabled {
    background: var(--bg-secondary) !important;
    opacity: 0.7;
    cursor: not-allowed;
}

[data-testid="stChatInput"][data-disabled="true"] textarea,
[data-testid="stChatInput"].disabled textarea {
    background: var(--bg-secondary) !important;
    cursor: not-allowed;
}

/* ============================================
   BUTTON STYLES
   ============================================ */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    min-height: 44px !important;
    transition: all 0.2s ease !important;
    border: none !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25) !important;
}

.stButton > button:active {
    transform: translateY(0);
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    color: white !important;
}

/* Secondary button (in sidebar - needs contrast on dark background) */
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
    background: white !important;
    color: #134E4A !important;
    border: 1px solid #E2E8F0 !important;
}

[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) p,
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) span,
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) div {
    color: #134E4A !important;
}

[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
    background: #F0FDFA !important;
}

[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover p,
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover span,
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover div {
    color: #0F766E !important;
}

/* ============================================
   S-TIER CARD STYLES
   ============================================ */
.s-tier-card {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
    border-radius: 20px;
    padding: 2rem;
    color: white;
    box-shadow: 0 20px 40px rgba(245, 158, 11, 0.3);
    animation: s-tier-glow 2s ease-in-out infinite;
    margin: 1.5rem 0;
}

@keyframes s-tier-glow {
    0%, 100% {
        box-shadow: 0 20px 40px rgba(245, 158, 11, 0.3);
    }
    50% {
        box-shadow: 0 25px 50px rgba(245, 158, 11, 0.5);
    }
}

.s-tier-card h2 {
    color: white !important;
    margin-bottom: 1rem;
}

.s-tier-card p {
    color: rgba(255, 255, 255, 0.95);
    font-size: 1.1rem;
    line-height: 1.6;
}

.s-tier-card .cta-button {
    display: inline-block;
    background: white;
    color: var(--accent-dark);
    padding: 0.875rem 1.75rem;
    border-radius: 10px;
    font-weight: 600;
    text-decoration: none;
    margin-top: 1rem;
    transition: all 0.2s ease;
}

.s-tier-card .cta-button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* ============================================
   RESULT CARD STYLES
   ============================================ */
.result-card {
    background: var(--bg-card);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid var(--border);
    margin: 1rem 0;
}

.result-card.pass {
    border-left: 4px solid var(--success);
}

.result-card.fail {
    border-left: 4px solid var(--error);
}

.tier-badge {
    display: inline-block;
    padding: 0.375rem 0.875rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.875rem;
}

.tier-badge.s { background: var(--accent); color: white; }
.tier-badge.a { background: var(--success); color: white; }
.tier-badge.b { background: var(--warning); color: white; }
.tier-badge.c { background: var(--text-muted); color: white; }

/* ============================================
   THINKING INDICATOR
   ============================================ */
.thinking-indicator {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text-secondary);
    font-style: italic;
    padding: 1rem;
}

.thinking-dots {
    display: flex;
    gap: 4px;
}

.thinking-dots span {
    width: 8px;
    height: 8px;
    background: var(--primary);
    border-radius: 50%;
    animation: thinking-bounce 1.4s ease-in-out infinite;
}

.thinking-dots span:nth-child(1) { animation-delay: 0s; }
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes thinking-bounce {
    0%, 80%, 100% {
        transform: scale(0.6);
        opacity: 0.5;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}

/* ============================================
   SCORE DISPLAY
   ============================================ */
.score-display {
    font-family: 'DM Sans', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    color: var(--primary);
    line-height: 1;
}

.score-label {
    color: var(--text-secondary);
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ============================================
   PROGRESS BAR
   ============================================ */
.interview-progress {
    height: 6px;
    background: var(--bg-secondary);
    border-radius: 3px;
    overflow: hidden;
    margin: 1rem 0;
}

.interview-progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
    border-radius: 3px;
    transition: width 0.3s ease;
}

/* ============================================
   RESPONSIVE ADJUSTMENTS
   ============================================ */
@media (max-width: 768px) {
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        margin-left: 5% !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        margin-right: 5% !important;
    }

    .s-tier-card {
        padding: 1.5rem;
        border-radius: 16px;
    }
}

/* ============================================
   ACCESSIBILITY
   ============================================ */
@media (prefers-reduced-motion: reduce) {
    * {
        animation: none !important;
        transition: none !important;
    }
}

/* Focus styles for keyboard navigation */
*:focus-visible {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}
</style>
"""

# =============================================================================
# COMPONENT HTML TEMPLATES
# =============================================================================

THINKING_INDICATOR_HTML = """
<div class="thinking-indicator">
    <div class="thinking-dots">
        <span></span>
        <span></span>
        <span></span>
    </div>
    <span>AI 正在评估您的回答...</span>
</div>
"""

S_TIER_CARD_HTML = """
<div class="s-tier-card">
    <h2 style="display: flex; align-items: center; gap: 0.5rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        恭喜！您被评为 S 级人才！
    </h2>
    <p>{notification_text}</p>
    <p><strong>{invitation}</strong></p>
    {link_html}
</div>
"""

RESULT_CARD_HTML = """
<div class="result-card {status_class}">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
            <span class="score-display">{score}</span>
            <span class="score-label">/ 100 分</span>
        </div>
        <span class="tier-badge {tier_class}">{tier_label}</span>
    </div>
    <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">{summary}</p>
</div>
"""

PROGRESS_BAR_HTML = """
<div class="interview-progress">
    <div class="interview-progress-bar" style="width: {progress}%;"></div>
</div>
<p style="text-align: center; color: var(--text-muted); font-size: 0.875rem;">
    对话进度: {current} / {max} 轮
</p>
"""


def get_s_tier_card(
    notification_text: str,
    invitation: str,
    link: str = ""
) -> str:
    """Generate S-tier celebration card HTML"""
    arrow_icon = '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>'''
    link_html = f'<a href="{link}" class="cta-button" target="_blank">{arrow_icon} 点击预约面试时间</a>' if link else ""

    return S_TIER_CARD_HTML.format(
        notification_text=notification_text,
        invitation=invitation,
        link_html=link_html
    )


def get_result_card(
    score: int,
    tier: str,
    summary: str,
    is_pass: bool
) -> str:
    """Generate result card HTML"""
    tier_labels = {
        "S": "S 级 - 卓越",
        "A": "A 级 - 优秀",
        "B": "B 级 - 合格",
        "C": "C 级 - 淘汰"
    }

    return RESULT_CARD_HTML.format(
        score=score,
        tier_label=tier_labels.get(tier, tier),
        tier_class=tier.lower(),
        summary=summary,
        status_class="pass" if is_pass else "fail"
    )


def get_progress_bar(current: int, max_turns: int) -> str:
    """Generate progress bar HTML"""
    progress = min(100, (current / max_turns) * 100)
    return PROGRESS_BAR_HTML.format(
        progress=progress,
        current=current,
        max=max_turns
    )
