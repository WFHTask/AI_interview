"""
Voice Input Guide Component

Displays guidance for using Doubao voice input method.
Implements keyboard blocking with paste allowed for voice-to-text input.

Business Logic:
1. Candidate sees voice input guidance on interview page
2. Keyboard direct input is disabled (paste still works for voice-to-text)
3. Candidate uses Doubao voice input, content auto-fills input box
4. Click send button to submit
"""
import streamlit as st
from components.styles import icon


def render_voice_input_guide():
    """
    Render the voice input guidance section for candidates.

    Shows:
    - Clear indication that ONLY voice input is supported
    - Download links for Doubao input method
    - Usage instructions
    """
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border: 2px solid #F59E0B;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
            <div style="color: #D97706; flex-shrink: 0;">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" x2="12" y1="19" y2="22"/>
                </svg>
            </div>
            <div style="flex: 1;">
                <h4 style="margin: 0 0 0.75rem 0; color: #92400E; font-size: 1.1rem; font-weight: 700;">
                    本系统仅支持语音输入
                </h4>
                <p style="margin: 0 0 1rem 0; color: #78350F; font-size: 0.95rem; line-height: 1.6;">
                    请安装语音输入工具后使用语音回答问题：
                </p>
                <ul style="margin: 0; padding-left: 1.25rem; color: #78350F; font-size: 0.9rem; line-height: 1.8;">
                    <li><strong>iOS：</strong>App Store 搜索"豆包输入法"</li>
                    <li><strong>Android：</strong>各应用商店搜索"豆包输入法"</li>
                    <li><strong>电脑端：</strong>使用「闪电说」<a href="https://shandianshuo.cn/" target="_blank" rel="noopener noreferrer" style="color: #0D9488;">https://shandianshuo.cn/</a></li>
                </ul>
                <div style="
                    background: rgba(255,255,255,0.6);
                    border-radius: 8px;
                    padding: 0.75rem;
                    margin-top: 1rem;
                ">
                    <p style="color: #92400E; margin: 0; font-size: 0.9rem;">
                        <strong>使用方法：</strong>安装后，在输入框长按说话，语音将自动转为文字。
                    </p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_voice_input_setup():
    """
    Render detailed setup instructions for Doubao voice input method.

    Shows download links and step-by-step instructions.
    """
    html_content = """<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;"><h4 style="margin: 0 0 1rem 0; color: #1E293B; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>语音输入设置指南</h4><div style="margin-bottom: 1rem;"><p style="color: #64748B; margin: 0 0 0.75rem 0; font-size: 0.9rem; font-weight: 500;">手机端：下载豆包输入法</p><div style="display: flex; flex-wrap: wrap; gap: 0.5rem;"><span style="background: #F1F5F9; color: #475569; padding: 0.375rem 0.75rem; border-radius: 6px; font-size: 0.85rem;">iOS: App Store 搜索「豆包输入法」</span><span style="background: #F1F5F9; color: #475569; padding: 0.375rem 0.75rem; border-radius: 6px; font-size: 0.85rem;">Android: 应用商店搜索「豆包输入法」</span></div></div><div style="margin-bottom: 1rem;"><p style="color: #64748B; margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: 500;">电脑端：使用闪电说</p><a href="https://shandianshuo.cn/" target="_blank" rel="noopener noreferrer" style="color: #0D9488; text-decoration: none; font-size: 0.9rem;">https://shandianshuo.cn/</a></div><div style="margin-bottom: 1rem;"><p style="color: #64748B; margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: 500;">设置为默认输入法</p><p style="color: #475569; margin: 0; font-size: 0.85rem;">手机：在设置中将豆包输入法设为默认<br>电脑：安装闪电说后按快捷键激活语音输入</p></div><div style="background: #F0FDFA; border-radius: 8px; padding: 0.75rem; margin-top: 1rem;"><p style="color: #0F766E; margin: 0; font-size: 0.85rem; line-height: 1.6;"><strong>开始语音输入</strong><br>点击输入框，然后点击麦克风图标或长按说话，语音将自动转为文字。<br>支持普通话、粤语、四川话等多种方言。</p></div></div>"""
    st.markdown(html_content, unsafe_allow_html=True)


def render_voice_input_reminder():
    """
    Render a compact reminder about voice input above the chat input.

    This is displayed during active interview to remind users.
    """
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border: 1px solid #F59E0B;
        border-radius: 8px;
        padding: 0.625rem 0.875rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    ">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" x2="12" y1="19" y2="22"/>
        </svg>
        <span style="color: #92400E; font-size: 0.85rem; font-weight: 500;">
            仅支持语音输入 - 手机用豆包输入法，电脑用闪电说
        </span>
    </div>
    """, unsafe_allow_html=True)


# Voice input CSS and JavaScript for comprehensive keyboard blocking
# Multi-layer protection:
# 1. keydown event - block key presses
# 2. keypress event - block character input
# 3. beforeinput event - block input before it happens
# 4. input event - revert unauthorized changes
# 5. composition events - handle IME input
# Allows: Paste (Ctrl+V/Cmd+V), Backspace, Delete, Arrow keys, Enter
VOICE_INPUT_CSS = """
<style>
/* Style chat input to indicate voice-only mode */
[data-testid="stChatInputTextArea"] textarea {
    background-color: #FFFBEB !important;
    border-color: #F59E0B !important;
    caret-color: #D97706 !important;
}

[data-testid="stChatInputTextArea"] textarea::placeholder {
    color: #92400E !important;
}

[data-testid="stChatInputTextArea"] textarea:focus {
    border-color: #D97706 !important;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2) !important;
}

/* Visual indicator for voice-only mode */
[data-testid="stChatInputTextArea"]::before {
    content: '';
    position: absolute;
    top: -2px;
    right: -2px;
    width: 10px;
    height: 10px;
    background: #F59E0B;
    border-radius: 50%;
    animation: voice-pulse 1.5s ease-in-out infinite;
    z-index: 1000;
}

@keyframes voice-pulse {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.2); }
}
</style>

<script>
// Comprehensive keyboard blocking for voice-only input mode
// Strategy: Only allow paste operations, block everything else including IME
(function() {
    // Global state per textarea (using WeakMap to avoid memory leaks)
    const textareaStates = new WeakMap();

    function getState(textarea) {
        if (!textareaStates.has(textarea)) {
            textareaStates.set(textarea, {
                lastValidValue: textarea.value || '',
                isPasting: false,
                isComposing: false,
                valueBeforeComposition: ''
            });
        }
        return textareaStates.get(textarea);
    }

    function isAllowedKey(e) {
        // Navigation and control keys
        const allowedKeys = [
            'Backspace', 'Delete',
            'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Enter', 'Tab', 'Escape',
            'Home', 'End', 'PageUp', 'PageDown'
        ];

        if (allowedKeys.includes(e.key)) {
            return true;
        }

        // Allow Ctrl/Cmd combinations for paste, copy, select all, cut, undo
        const isCtrlCmd = e.ctrlKey || e.metaKey;
        const allowedWithCtrl = ['v', 'V', 'a', 'A', 'c', 'C', 'x', 'X', 'z', 'Z'];

        if (isCtrlCmd && allowedWithCtrl.includes(e.key)) {
            return true;
        }

        return false;
    }

    function setupVoiceOnlyInput() {
        const textareas = document.querySelectorAll('[data-testid="stChatInputTextArea"] textarea');

        textareas.forEach(function(textarea) {
            if (textarea.dataset.voiceOnlySetup === 'v3') return;
            textarea.dataset.voiceOnlySetup = 'v3';

            const state = getState(textarea);
            state.lastValidValue = textarea.value || '';

            // === PASTE EVENT: Mark as pasting ===
            textarea.addEventListener('paste', function(e) {
                const s = getState(textarea);
                s.isPasting = true;
                // Clear the flag after paste is processed
                setTimeout(() => {
                    s.isPasting = false;
                    s.lastValidValue = textarea.value;
                }, 100);
            }, true);

            // === COMPOSITION EVENTS: Handle IME input ===
            textarea.addEventListener('compositionstart', function(e) {
                const s = getState(textarea);
                s.isComposing = true;
                s.valueBeforeComposition = textarea.value;
            }, true);

            textarea.addEventListener('compositionend', function(e) {
                const s = getState(textarea);
                s.isComposing = false;
                // Revert IME input - restore to value before composition
                if (!s.isPasting) {
                    textarea.value = s.valueBeforeComposition;
                    // Trigger input event for Streamlit to sync
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }, true);

            // === KEYDOWN: Block most keys ===
            textarea.addEventListener('keydown', function(e) {
                const s = getState(textarea);

                // Allow during paste operation
                if (s.isPasting) return;

                // Block IME trigger keys (Process key on Windows)
                if (e.key === 'Process' || e.keyCode === 229) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }

                if (!isAllowedKey(e)) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }, true);

            // === KEYPRESS: Block character input ===
            textarea.addEventListener('keypress', function(e) {
                const s = getState(textarea);
                if (s.isPasting) return;

                // Only allow Enter key
                if (e.key !== 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }, true);

            // === BEFOREINPUT: Block before input happens ===
            textarea.addEventListener('beforeinput', function(e) {
                const s = getState(textarea);

                // Allow paste operations
                if (e.inputType === 'insertFromPaste' || e.inputType === 'insertFromDrop') {
                    s.isPasting = true;
                    setTimeout(() => {
                        s.isPasting = false;
                        s.lastValidValue = textarea.value;
                    }, 100);
                    return;
                }

                // Allow delete operations
                const deleteTypes = [
                    'deleteByCut',
                    'deleteContentBackward',
                    'deleteContentForward',
                    'deleteWordBackward',
                    'deleteWordForward',
                    'deleteSoftLineBackward',
                    'deleteSoftLineForward',
                    'deleteHardLineBackward',
                    'deleteHardLineForward'
                ];
                if (deleteTypes.includes(e.inputType)) {
                    return;
                }

                // Allow line breaks and history
                const allowedTypes = [
                    'insertLineBreak',
                    'insertParagraph',
                    'historyUndo',
                    'historyRedo'
                ];
                if (allowedTypes.includes(e.inputType)) {
                    return;
                }

                // Block all text insertion (including IME)
                if (e.inputType === 'insertText' ||
                    e.inputType === 'insertCompositionText' ||
                    e.inputType === 'insertReplacementText') {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }, true);

            // === INPUT: Final safety net - revert unauthorized changes ===
            textarea.addEventListener('input', function(e) {
                const s = getState(textarea);

                // Allow if pasting
                if (s.isPasting) {
                    s.lastValidValue = textarea.value;
                    return;
                }

                // Allow delete operations
                const allowedTypes = [
                    'deleteByCut',
                    'deleteContentBackward',
                    'deleteContentForward',
                    'deleteWordBackward',
                    'deleteWordForward',
                    'insertLineBreak',
                    'insertParagraph',
                    'historyUndo',
                    'historyRedo',
                    'insertFromPaste',
                    'insertFromDrop'
                ];

                if (e.inputType && allowedTypes.includes(e.inputType)) {
                    s.lastValidValue = textarea.value;
                    return;
                }

                // If during composition, let compositionend handle it
                if (s.isComposing) {
                    return;
                }

                // Check for unauthorized input (including no inputType)
                if (e.inputType === 'insertText' ||
                    e.inputType === 'insertCompositionText' ||
                    e.inputType === 'insertReplacementText' ||
                    !e.inputType ||
                    (e.inputType && !allowedTypes.includes(e.inputType) && e.inputType.startsWith('insert'))) {
                    // Revert if new chars were added
                    if (textarea.value.length > s.lastValidValue.length) {
                        textarea.value = s.lastValidValue;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    return;
                }

                // Update last valid value for allowed operations
                s.lastValidValue = textarea.value;
            }, true);

            // === FOCUS: Reset state ===
            textarea.addEventListener('focus', function() {
                const s = getState(textarea);
                s.lastValidValue = textarea.value;
                s.isPasting = false;
                s.isComposing = false;
            });
        });
    }

    // Run immediately
    setupVoiceOnlyInput();

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupVoiceOnlyInput);
    }

    // MutationObserver for Streamlit's dynamic content
    const observer = new MutationObserver(function(mutations) {
        // Debounce
        clearTimeout(window.voiceOnlyDebounce);
        window.voiceOnlyDebounce = setTimeout(setupVoiceOnlyInput, 50);
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Also run on visibility change (tab switch back)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            setupVoiceOnlyInput();
        }
    });

    // Periodic check as backup (every 2 seconds)
    setInterval(setupVoiceOnlyInput, 2000);
})();
</script>
"""


def inject_voice_only_mode():
    """
    Inject CSS and JavaScript to enable voice-only input mode.

    This should be called in the candidate view to:
    1. Style the input box to indicate voice-only mode
    2. Block keyboard direct input (except navigation keys)
    3. Allow paste for receiving voice-to-text content
    """
    import streamlit.components.v1 as components

    # Inject CSS via st.markdown
    st.markdown("""
<style>
/* Style chat input to indicate voice-only mode */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] textarea,
.stChatInput textarea {
    background-color: #FFFBEB !important;
    border-color: #F59E0B !important;
    caret-color: #D97706 !important;
}

[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInputTextArea"] textarea::placeholder,
.stChatInput textarea::placeholder {
    color: #92400E !important;
}

[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInputTextArea"] textarea:focus,
.stChatInput textarea:focus {
    border-color: #D97706 !important;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2) !important;
}
</style>
    """, unsafe_allow_html=True)

    # Inject JavaScript via components.html (bypasses CSP restrictions)
    # Simple and bulletproof approach: block ALL keypress, only allow Ctrl+V/Cmd+V
    components.html("""
<script>
(function() {
    const targetDoc = window.parent.document;

    function setupPasteOnly() {
        const selectors = [
            '[data-testid="stChatInput"] textarea',
            '[data-testid="stChatInputTextArea"] textarea',
            '.stChatInput textarea',
            '.stChatFloatingInputContainer textarea'
        ];

        let textareas = [];
        for (const selector of selectors) {
            const found = targetDoc.querySelectorAll(selector);
            if (found.length > 0) {
                textareas = Array.from(found);
                break;
            }
        }

        textareas.forEach(function(textarea) {
            if (textarea.dataset.pasteOnlyV6) return;
            textarea.dataset.pasteOnlyV6 = 'true';

            // State tracking
            let lastValue = textarea.value || '';
            let isPasting = false;

            // Track paste operations
            textarea.addEventListener('paste', function() {
                isPasting = true;
                setTimeout(() => {
                    isPasting = false;
                    lastValue = textarea.value;
                }, 300);
            }, true);

            // Block ALL keydown except: navigation, Ctrl+V/Cmd+V, Enter, Backspace, Delete
            textarea.addEventListener('keydown', function(e) {
                const isCtrlCmd = e.ctrlKey || e.metaKey;

                // Allow Ctrl/Cmd + V (paste)
                if (isCtrlCmd && (e.key === 'v' || e.key === 'V')) {
                    return true;
                }

                // Allow Ctrl/Cmd + A (select all), C (copy), X (cut), Z (undo)
                if (isCtrlCmd && ['a', 'A', 'c', 'C', 'x', 'X', 'z', 'Z'].includes(e.key)) {
                    return true;
                }

                // Allow navigation and editing keys
                const allowedKeys = [
                    'Backspace', 'Delete', 'Enter', 'Tab', 'Escape',
                    'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
                    'Home', 'End', 'PageUp', 'PageDown'
                ];
                if (allowedKeys.includes(e.key)) {
                    return true;
                }

                // Block everything else (including IME Process key)
                e.preventDefault();
                e.stopPropagation();
                return false;
            }, true);

            // Block keypress completely (catches remaining character input)
            textarea.addEventListener('keypress', function(e) {
                // Only allow Enter
                if (e.key === 'Enter') return true;
                e.preventDefault();
                e.stopPropagation();
                return false;
            }, true);

            // Handle IME composition - revert when composition ends
            textarea.addEventListener('compositionend', function(e) {
                if (!isPasting) {
                    // Revert to value before IME input
                    setTimeout(() => {
                        if (!isPasting && textarea.value !== lastValue && textarea.value.length > lastValue.length) {
                            textarea.value = lastValue;
                            textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }, 10);
                }
            }, true);

            // Block beforeinput for non-paste insertions
            textarea.addEventListener('beforeinput', function(e) {
                // Allow paste and drop
                if (e.inputType === 'insertFromPaste' || e.inputType === 'insertFromDrop') {
                    isPasting = true;
                    setTimeout(() => {
                        isPasting = false;
                        lastValue = textarea.value;
                    }, 300);
                    return true;
                }

                // Allow delete operations
                if (e.inputType && e.inputType.startsWith('delete')) {
                    return true;
                }

                // Allow line breaks, history
                const allowed = ['insertLineBreak', 'insertParagraph', 'historyUndo', 'historyRedo'];
                if (allowed.includes(e.inputType)) {
                    return true;
                }

                // Block all text insertion (including IME)
                if (e.inputType && e.inputType.startsWith('insert')) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }, true);

            // Final safety: revert any unauthorized changes in input event
            textarea.addEventListener('input', function(e) {
                if (isPasting) {
                    lastValue = textarea.value;
                    return;
                }

                // Allow deletions and line breaks
                const allowedTypes = [
                    'deleteContentBackward', 'deleteContentForward',
                    'deleteByCut', 'deleteWordBackward', 'deleteWordForward',
                    'insertLineBreak', 'insertParagraph',
                    'historyUndo', 'historyRedo',
                    'insertFromPaste', 'insertFromDrop'
                ];

                if (e.inputType && allowedTypes.includes(e.inputType)) {
                    lastValue = textarea.value;
                    return;
                }

                // Revert if chars were added (not by paste)
                if (textarea.value.length > lastValue.length) {
                    textarea.value = lastValue;
                }
            }, true);

            // Update lastValue on focus
            textarea.addEventListener('focus', function() {
                lastValue = textarea.value;
                isPasting = false;
            });

            // Double-check on blur
            textarea.addEventListener('blur', function() {
                if (!isPasting && textarea.value.length > lastValue.length) {
                    textarea.value = lastValue;
                }
            });

            console.log('[VoiVerse] Paste-only mode v6 enabled');
        });
    }

    // Run setup
    setupPasteOnly();

    // MutationObserver for dynamic content
    const observer = new MutationObserver(function() {
        clearTimeout(window._pasteOnlyTimer);
        window._pasteOnlyTimer = setTimeout(setupPasteOnly, 100);
    });
    observer.observe(targetDoc.body, { childList: true, subtree: true });

    // Periodic check as backup
    setInterval(setupPasteOnly, 2000);
})();
</script>
    """, height=0, width=0)
