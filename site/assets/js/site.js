/* Shared page utilities. WIRING: HTML onclick handlers call these global names.
 * Keep behavior here rather than copying these functions into individual pages.
 */
(function (global) {
    'use strict';

    global.toggleSpoiler = function (id) {
        var panel = document.getElementById(id);
        if (!panel) return;
        var wasOpen = panel.classList.contains('show');
        document.querySelectorAll('.spoiler-content').forEach(function (other) {
            other.classList.remove('show');
        });
        if (!wasOpen) panel.classList.add('show');
    };

    global.copyText = async function (id) {
        var field = document.getElementById(id);
        if (!field) return false;
        var value = 'value' in field ? field.value : field.textContent;
        var copied = false;
        if (global.isSecureContext && global.navigator && global.navigator.clipboard) {
            try {
                await global.navigator.clipboard.writeText(value);
                copied = true;
            } catch (_) { /* Fall through to the local-preview fallback. */ }
        }
        if (!copied && typeof field.select === 'function') {
            field.select();
            try { copied = document.execCommand('copy'); } catch (_) { copied = false; }
        }
        var button = field.nextElementSibling;
        if (copied && button && button.tagName === 'BUTTON') {
            var original = button.textContent;
            button.textContent = 'Copied!';
            global.setTimeout(function () { button.textContent = original; }, 1500);
        }
        return copied;
    };
    global.copyLink = global.copyText;
})(window);
