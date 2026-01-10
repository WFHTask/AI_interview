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
                    请安装「豆包语音输入法」后使用语音回答问题：
                </p>
                <ul style="margin: 0; padding-left: 1.25rem; color: #78350F; font-size: 0.9rem; line-height: 1.8;">
                    <li><strong>iOS 下载：</strong>App Store 搜索"豆包输入法"</li>
                    <li><strong>Android 下载：</strong>各应用商店搜索"豆包输入法"</li>
                    <li><strong>电脑端：</strong>访问 <a href="https://www.doubao.com/" target="_blank" rel="noopener noreferrer" style="color: #0D9488;">https://www.doubao.com/</a></li>
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
    html_content = """<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;"><h4 style="margin: 0 0 1rem 0; color: #1E293B; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>语音输入设置指南</h4><div style="margin-bottom: 1rem;"><p style="color: #64748B; margin: 0 0 0.75rem 0; font-size: 0.9rem; font-weight: 500;">第一步：下载豆包输入法</p><div style="display: flex; flex-wrap: wrap; gap: 0.5rem;"><span style="background: #F1F5F9; color: #475569; padding: 0.375rem 0.75rem; border-radius: 6px; font-size: 0.85rem;">iOS: App Store 搜索「豆包输入法」</span><span style="background: #F1F5F9; color: #475569; padding: 0.375rem 0.75rem; border-radius: 6px; font-size: 0.85rem;">Android: 应用商店搜索「豆包输入法」</span></div></div><div style="margin-bottom: 1rem;"><p style="color: #64748B; margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: 500;">电脑端访问：</p><a href="https://www.doubao.com/" target="_blank" rel="noopener noreferrer" style="color: #0D9488; text-decoration: none; font-size: 0.9rem;">https://www.doubao.com/</a></div><div style="margin-bottom: 1rem;"><p style="color: #64748B; margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: 500;">第二步：设为默认输入法</p><p style="color: #475569; margin: 0; font-size: 0.85rem;">在手机设置中将豆包输入法设为默认，或在电脑上切换到豆包输入法。</p></div><div style="background: #F0FDFA; border-radius: 8px; padding: 0.75rem; margin-top: 1rem;"><p style="color: #0F766E; margin: 0; font-size: 0.85rem; line-height: 1.6;"><strong>第三步：开始语音输入</strong><br>点击输入框，然后点击键盘上的麦克风图标或长按说话，语音将自动转为文字填入输入框。<br>支持普通话、粤语、四川话等多种方言。</p></div></div>"""
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
            仅支持语音输入 - 请使用豆包输入法长按说话
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
                const deleteTypes = [
                    'deleteByCut',
                    'deleteContentBackward',
                    'deleteContentForward',
                    'deleteWordBackward',
                    'deleteWordForward',
                    'insertLineBreak',
                    'insertParagraph',
                    'historyUndo',
                    'historyRedo'
                ];

                if (e.inputType && deleteTypes.includes(e.inputType)) {
                    s.lastValidValue = textarea.value;
                    return;
                }

                // If during composition, let compositionend handle it
                if (s.isComposing) {
                    return;
                }

                // Check for unauthorized input
                if (e.inputType === 'insertText' ||
                    e.inputType === 'insertCompositionText' ||
                    e.inputType === 'insertReplacementText' ||
                    (e.inputType && !deleteTypes.includes(e.inputType) && e.inputType.startsWith('insert'))) {
                    // Revert to last valid value
                    textarea.value = s.lastValidValue;
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
    components.html("""
<script>
// Comprehensive keyboard blocking for voice-only input mode
// Strategy: Only allow paste operations, block everything else including IME
(function() {
    // Target the parent window (Streamlit's main frame)
    const targetDoc = window.parent.document;

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
        // Try multiple selectors for different Streamlit versions
        const selectors = [
            '[data-testid="stChatInput"] textarea',
            '[data-testid="stChatInputTextArea"] textarea',
            '.stChatInput textarea',
            'textarea[data-testid="stChatInputTextArea"]',
            '.stChatFloatingInputContainer textarea',
            'form textarea'
        ];

        let textareas = [];
        for (const selector of selectors) {
            const found = targetDoc.querySelectorAll(selector);
            if (found.length > 0) {
                textareas = found;
                break;
            }
        }

        if (textareas.length === 0) {
            // Fallback: find any textarea that looks like a chat input
            textareas = targetDoc.querySelectorAll('textarea');
        }

        textareas.forEach(function(textarea) {
            if (textarea.dataset.voiceOnlySetup === 'v4') return;
            textarea.dataset.voiceOnlySetup = 'v4';

            const state = getState(textarea);
            state.lastValidValue = textarea.value || '';

            // === PASTE EVENT: Mark as pasting ===
            textarea.addEventListener('paste', function(e) {
                const s = getState(textarea);
                s.isPasting = true;
                setTimeout(() => {
                    s.isPasting = false;
                    s.lastValidValue = textarea.value;
                }, 200);
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
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }, true);

            // === KEYDOWN: Block most keys ===
            textarea.addEventListener('keydown', function(e) {
                const s = getState(textarea);

                if (s.isPasting) return;

                // Block IME trigger keys
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
                    }, 200);
                    return;
                }

                // Allow delete operations
                const deleteTypes = [
                    'deleteByCut', 'deleteContentBackward', 'deleteContentForward',
                    'deleteWordBackward', 'deleteWordForward',
                    'deleteSoftLineBackward', 'deleteSoftLineForward',
                    'deleteHardLineBackward', 'deleteHardLineForward'
                ];
                if (deleteTypes.includes(e.inputType)) return;

                // Allow line breaks and history
                const allowedTypes = ['insertLineBreak', 'insertParagraph', 'historyUndo', 'historyRedo'];
                if (allowedTypes.includes(e.inputType)) return;

                // Block all text insertion (including IME)
                if (e.inputType === 'insertText' ||
                    e.inputType === 'insertCompositionText' ||
                    e.inputType === 'insertReplacementText') {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }, true);

            // === INPUT: Final safety net ===
            textarea.addEventListener('input', function(e) {
                const s = getState(textarea);

                if (s.isPasting) {
                    s.lastValidValue = textarea.value;
                    return;
                }

                const allowedTypes = [
                    'deleteByCut', 'deleteContentBackward', 'deleteContentForward',
                    'deleteWordBackward', 'deleteWordForward',
                    'insertLineBreak', 'insertParagraph', 'historyUndo', 'historyRedo',
                    'insertFromPaste', 'insertFromDrop'
                ];

                if (e.inputType && allowedTypes.includes(e.inputType)) {
                    s.lastValidValue = textarea.value;
                    return;
                }

                if (s.isComposing) return;

                // Revert unauthorized input
                if (e.inputType === 'insertText' ||
                    e.inputType === 'insertCompositionText' ||
                    e.inputType === 'insertReplacementText') {
                    textarea.value = s.lastValidValue;
                    return;
                }

                s.lastValidValue = textarea.value;
            }, true);

            // === FOCUS: Reset state ===
            textarea.addEventListener('focus', function() {
                const s = getState(textarea);
                s.lastValidValue = textarea.value;
                s.isPasting = false;
                s.isComposing = false;
            });

            // === BLUR: Force revert any pending IME input ===
            textarea.addEventListener('blur', function() {
                const s = getState(textarea);
                // If there was uncommitted composition, revert
                if (s.isComposing || textarea.value !== s.lastValidValue) {
                    if (!s.isPasting) {
                        textarea.value = s.lastValidValue;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }
                s.isComposing = false;
            });

            // === FOCUSOUT: Double check on focus out ===
            textarea.addEventListener('focusout', function() {
                const s = getState(textarea);
                if (!s.isPasting && textarea.value !== s.lastValidValue) {
                    textarea.value = s.lastValidValue;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });

            console.log('[VoiVerse] Voice-only mode enabled for textarea');
        });
    }

    // Run setup
    setupVoiceOnlyInput();

    // MutationObserver for dynamic content
    const observer = new MutationObserver(function() {
        clearTimeout(window.voiceOnlyDebounce);
        window.voiceOnlyDebounce = setTimeout(setupVoiceOnlyInput, 100);
    });

    observer.observe(targetDoc.body, { childList: true, subtree: true });

    // Periodic check as backup
    setInterval(setupVoiceOnlyInput, 1000);

    // Run on visibility change
    targetDoc.addEventListener('visibilitychange', function() {
        if (!targetDoc.hidden) setupVoiceOnlyInput();
    });

    console.log('[VoiVerse] Voice-only input blocking initialized');
})();
</script>
    """, height=0, width=0)
