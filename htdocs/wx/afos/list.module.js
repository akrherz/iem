import { requireElement } from '/js/iemjs/domUtils.js';

/**
 * Toggle visibility of date range selector
 * Called from PHP-generated onclick handler
 */
function showHide() {
    const d2 = document.getElementById("d2");
    if (document.getElementById("drange").checked) {
        d2.style.display = "block";
    } else {
        d2.style.display = "none";
    }
}

/**
 * Smooth scroll to section by name
 * Called from PHP-generated onclick handlers for navigation
 */
function j(name) {
    const target = document.getElementById(`sect${name}`);
    if (target) {
        target.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Add event listener for date range checkbox
    const drangeCheckbox = requireElement('#drange');
    drangeCheckbox.addEventListener('change', showHide);
});

// Export functions for global access (needed for PHP-generated onclick handlers)
window.showHide = showHide;
window.j = j;