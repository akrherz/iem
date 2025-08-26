// auto documentation for a HTML form to show an example curl request

function buildCurlCommand(form, queryString) {
    const baseUrl = form.action || window.location.href;
    
    if (queryString.length > 2000) {
        const stationSelectOut = form.querySelector('select[name="station"], select[name="stations"]');
        const stationCount = stationSelectOut ? stationSelectOut.selectedOptions.length : 0;
        
        return `# URL too long (${queryString.length} chars) with ${stationCount} stations selected
# Option 1: Use POST instead of GET
curl -X POST '${baseUrl}' \\
     -H 'Content-Type: application/x-www-form-urlencoded' \\
     -d '${queryString}' \\
     -o changeme.txt

# Option 2: Use fewer stations in your selection`;
    }
    
    const url = new URL(baseUrl);
    url.search = queryString;
    return `curl '${url}' -o changeme.txt`;
}

function form2url(form) {
    // Handle dynamic station selection from iemss module
    // All options in the right-side select should already be selected by iemss.js
    // We don't modify user selections - show exactly what they selected
    
    const formData = new FormData(form);
    const queryString = new URLSearchParams(formData).toString();
    
    return buildCurlCommand(form, queryString);
}

function copyToClipboard(button) {
    const command = button.getAttribute('data-command');
    
    // Use the modern Clipboard API if available
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(command).then(() => {
            showCopyFeedback(button, 'Copied!');
        }).catch(() => {
            fallbackCopyToClipboard(command, button);
        });
    } else {
        fallbackCopyToClipboard(command, button);
    }
}

function fallbackCopyToClipboard(text, button) {
    // Fallback for older browsers or non-HTTPS contexts
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback(button, 'Copied!');
    } catch {
        showCopyFeedback(button, 'Copy failed');
    }
    
    document.body.removeChild(textArea);
}

function showCopyFeedback(button, message) {
    const originalText = button.innerHTML;
    button.innerHTML = `<i class="bi bi-check-lg"></i> ${message}`;
    button.classList.remove('btn-outline-primary');
    button.classList.add('btn-success');
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-primary');
    }, 2000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateForm2UrlDisplay(div) {
    const form = div.closest('form');
    if (form) {
        const curlCommand = escapeHtml(form2url(form));
        div.innerHTML = `<div class="alert alert-info">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h5 class="mb-0"><i class="bi bi-terminal"></i> Automation Example with Curl</h5>
                <button type="button" class="btn btn-sm btn-outline-primary copy-curl-btn" data-command="${curlCommand}">
                    <i class="bi bi-clipboard"></i> Copy
                </button>
            </div>
            <p class="mb-2">This command and URL should replicate your current form selections:</p>
            <pre class="mb-0"><code>${curlCommand}</code></pre>
        </div>`;
    }
}

function attachFormListeners(div, form) {
    // Use event delegation to handle both existing and future form elements
    form.addEventListener('input', () => {
        updateForm2UrlDisplay(div);
    });
    
    form.addEventListener('change', () => {
        updateForm2UrlDisplay(div);
    });
    
    // Listen for clicks on station movement buttons (iemss interface)
    form.addEventListener('click', (event) => {
        if (event.target.matches('#stations_add, #stations_addall, #stations_del, #stations_delall')) {
            // Delay slightly to allow the DOM to update
            setTimeout(() => updateForm2UrlDisplay(div), 100);
        }
    });
    
    // Listen for double-clicks on station select elements
    form.addEventListener('dblclick', (event) => {
        if (event.target.matches('#stations_in, #stations_out')) {
            setTimeout(() => updateForm2UrlDisplay(div), 100);
        }
    });
}

function observeStationChanges(div, form) {
    // Watch for the iemss station selector to be created
    const observer = new MutationObserver((mutations) => {
        let stationElementAdded = false;
        
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    // Check if station select elements were added
                    if (node.matches && (
                        node.matches('select[name="station"], select[name="stations"]') ||
                        node.querySelector && node.querySelector('select[name="station"], select[name="stations"]')
                    )) {
                        stationElementAdded = true;
                    }
                    
                    // Also check for iemss container being populated
                    if (node.matches && node.matches('.iemss-container')) {
                        stationElementAdded = true;
                    }
                }
            });
        });
        
        if (stationElementAdded) {
            updateForm2UrlDisplay(div);
        }
    });
    
    // Observe the form for changes
    observer.observe(form, {
        childList: true,
        subtree: true
    });
    
    // Also watch for when the iemss module loads stations (after AJAX)
    const checkForStations = setInterval(() => {
        const stationSelect = form.querySelector('select[name="station"], select[name="stations"]');
        if (stationSelect && stationSelect.options.length > 0) {
            updateForm2UrlDisplay(div);
            clearInterval(checkForStations);
        }
    }, 500);
    
    // Clear the interval after 10 seconds to avoid infinite checking
    setTimeout(() => clearInterval(checkForStations), 10000);
    
    return observer;
}

document.addEventListener('DOMContentLoaded', () => {
    const form2urlDivs = document.querySelectorAll('div.form2url');
    
    form2urlDivs.forEach(div => {
        const form = div.closest('form');
        if (form) {
            // Initial display
            updateForm2UrlDisplay(div);
            
            // Attach event listeners for form changes
            attachFormListeners(div, form);
            
            // Watch for dynamic station selection elements
            observeStationChanges(div, form);
        }
    });
    
    // Event delegation for copy buttons
    document.addEventListener('click', (event) => {
        if (event.target.matches('.copy-curl-btn, .copy-curl-btn *')) {
            const button = event.target.closest('.copy-curl-btn');
            if (button) {
                copyToClipboard(button);
            }
        }
    });
});
