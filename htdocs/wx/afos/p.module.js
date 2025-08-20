// Copy-to-clipboard behavior for AFOS product <pre> blocks
// Avoid using `this`; rely on event targets. (Rule: avoid `this` confusion)

const copyText = async (text) => {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    }
    // Fallback: temporary textarea
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.top = '-9999px';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
        document.execCommand('copy');
    } finally {
        document.body.removeChild(ta);
    }
    return Promise.resolve();
};

const markCopied = (btn) => {
    btn.classList.add('copied');
    const orig = btn.dataset.label || btn.textContent;
    if (!btn.dataset.label) btn.dataset.label = orig;
    btn.textContent = 'Copied';
    setTimeout(() => {
        btn.classList.remove('copied');
        btn.textContent = btn.dataset.label;
    }, 2500);
};

const init = () => {
    const buttons = document.querySelectorAll('.afos-copy');
    if (buttons.length === 0) return;
    const status = document.getElementById('afos-status');
    buttons.forEach((btn) => {
        btn.addEventListener('click', async (ev) => {
            ev.preventDefault();
            // data-copy-target="next" means copy the sibling <pre>
            const pre = btn.closest('.afos-block')?.querySelector('.afos-pre');
            if (!pre) return;
            const text = pre.innerText.replace(/\s+$/, '');
            try {
                await copyText(text);
                markCopied(btn);
                if (status) status.textContent = 'Product text copied to clipboard.';
            } catch {
                // Silent failure; indicate error state briefly.
                btn.textContent = 'Error';
                setTimeout(() => {
                    if (!btn.classList.contains('copied')) {
                        btn.textContent = btn.dataset.label || 'Copy';
                    }
                }, 2000);
                if (status) status.textContent = 'Copy failed.';
            }
        });
    });
    // Help toggle for bulk download
    const helpToggle = document.querySelector('.afos-bulk-help-toggle');
    const helpPanel = document.getElementById('bulk-help');
    if (helpToggle && helpPanel) {
        helpToggle.addEventListener('click', () => {
            const isOpen = helpToggle.getAttribute('aria-expanded') === 'true';
            helpToggle.setAttribute('aria-expanded', String(!isOpen));
            if (isOpen) {
                helpPanel.hidden = true;
            } else {
                helpPanel.hidden = false;
                helpPanel.focus?.();
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', init);
