import { requireElement } from '/js/iemjs/domUtils.js';

/**
 * Toggle visibility of date range selector.
 */
function showHide() {
    const d2 = document.getElementById('d2');
    const cb = document.getElementById('drange');
    if (!d2 || !cb) return;
    const expanded = cb.checked;
    d2.style.display = expanded ? 'block' : 'none';
    cb.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    d2.setAttribute('aria-hidden', expanded ? 'false' : 'true');
}

/**
 * Smooth scroll to section by name.
 */
function scrollToSection(name) {
    const target = document.getElementById(`sect${name}`);
    if (!target) return;
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    target.scrollIntoView({
        behavior: prefersReduced ? 'auto' : 'smooth',
        block: 'start'
    });
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Date range checkbox listener
    const drangeCheckbox = requireElement('drange');
    drangeCheckbox.addEventListener('change', showHide);

    document.querySelectorAll('button[data-jump]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const name = btn.getAttribute('data-jump');
            if (name) scrollToSection(name);
        });
    });
});
