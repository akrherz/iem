// AFOS Text Product Finder - ES Module
import { escapeHTML } from '/js/iemjs/domUtils.js';

// Legacy anchors looked like PIL-LIMIT, now are PIL:(LIMIT * ORDER)
const NO_DATE_SET = 'No Limit';

let tabCounter = 0;

/**
 * Cookie utility functions (replacing js-cookie dependency)
 */
const Cookies = {
    set: (name, value, options = {}) => {
        let cookieString = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
        
        if (options.expires) {
            const date = new Date();
            date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
            cookieString += `; expires=${date.toUTCString()}`;
        }
        
        if (options.path) {
            cookieString += `; path=${options.path}`;
        }
        
        document.cookie = cookieString;
    },
    
    get: (name) => {
        const nameEQ = `${encodeURIComponent(name)}=`;
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let cc = ca[i];
            while (cc.charAt(0) === ' ') cc = cc.substring(1, cc.length);
            if (cc.indexOf(nameEQ) === 0) {
                return decodeURIComponent(cc.substring(nameEQ.length, cc.length));
            }
        }
        return undefined;
    }
};

/**
 * Safe XSS prevention for text content
 */
function text(str) {
    return escapeHTML(str);
}

/**
 * Parse a token and add the corresponding tab
 */
function dealWithToken(token) {
    let tokens2 = token.split("."); // URL-safe delimiter (dot doesn't get encoded)
    if (tokens2.length !== 2) {
        // Fall back to legacy colon format (from previous migration)
        tokens2 = token.split(":");
        if (tokens2.length !== 2) {
            // Fall back to legacy pipe format
            tokens2 = token.split("|");
            if (tokens2.length !== 2) {
                // Even older legacy format
                tokens2 = token.split("-");
            }
        }
    }
    if (tokens2.length === 1) {
        tokens2.push(1);
    }
    // Last value indicates the order
    const order = (parseInt(tokens2[1], 10) < 0) ? "asc" : "desc";
    const limit = Math.abs(parseInt(tokens2[1], 10));
    addTab(text(tokens2[0]), "", "", limit, NO_DATE_SET, NO_DATE_SET, false, order);
}

/**
 * Read URL parameters for PIL tabs (modern URLSearchParams approach)
 */
function readURLParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const pilParam = urlParams.get('pil');
    
    if (pilParam) {
        const tokenList = pilParam.split("~"); // URL-safe delimiter
        tokenList.forEach(token => {
            if (token.trim()) {
                dealWithToken(token);
            }
        });
        return true; // Found URL params
    }
    return false; // No URL params found
}

/**
 * Read anchor tags from URL hash (legacy support)
 */
function readAnchorTags() {
    const tokens = window.location.href.split("#");
    if (tokens.length !== 2 || !tokens[1]) {
        return false;
    }
    const tokenList = text(tokens[1]).split(",");
    tokenList.forEach(token => {
        if (token.trim()) {
            dealWithToken(token);
        }
    });
    return true; // Found hash params
}

/**
 * Read saved cookies
 */
function readCookies() {
    const afospils = Cookies.get('afospils');
    if (afospils === undefined || afospils === '') {
        return;
    }
    // Handle both new URL-safe format and legacy format
    const delimiter = afospils.includes('~') ? '~' : ',';
    const tokenList = afospils.split(delimiter);
    tokenList.forEach(token => {
        if (token.trim()) {
            dealWithToken(token);
        }
    });
}

/**
 * Save current tabs to cookies and update URL
 */
function saveCookies() {
    const afospils = [];
    const tabs = document.querySelectorAll(".nav-tabs li[data-pil]");
    
    tabs.forEach(li => {
        // Skip temporary tabs with date restrictions for COOKIES only
        if (li.dataset.sdate !== NO_DATE_SET) {
            return;
        }
        const multi = (li.dataset.order === "desc") ? 1 : -1;
        const val = parseInt(li.dataset.limit, 10) * multi;
        afospils.push(`${li.dataset.pil}.${val}`); // URL-safe delimiter (dot doesn't get encoded)
    });

    // Save to cookies (only persistent tabs)
    Cookies.set('afospils', afospils.join("~"), { // URL-safe delimiter
        'path': '/wx/afos/',
        'expires': 3650
    });
    
    // Always update URL with ALL current tabs (including temporary ones)
    updateURLFromCurrentTabs();
}

/**
 * Update URL with current PIL tabs using URLSearchParams
 */
function updateURL(pilTokens = []) {
    const url = new URL(window.location);
    
    if (pilTokens.length > 0) {
        url.searchParams.set('pil', pilTokens.join("~")); // URL-safe delimiter
    } else {
        url.searchParams.delete('pil');
    }
    
    // Clear legacy hash
    url.hash = '';
    
    // Update URL without page reload
    window.history.replaceState({}, '', url);
}

/**
 * Update URL from all current tabs (including those with date restrictions)
 */
function updateURLFromCurrentTabs() {
    const afospils = [];
    const tabs = document.querySelectorAll(".nav-tabs li[data-pil]");
    
    tabs.forEach(li => {
        const multi = (li.dataset.order === "desc") ? 1 : -1;
        const val = parseInt(li.dataset.limit, 10) * multi;
        afospils.push(`${li.dataset.pil}.${val}`); // URL-safe delimiter (dot doesn't get encoded)
    });
    
    updateURL(afospils);
}

/**
 * Load content for a tab using fetch API
 */
async function loadTabContent(div, pil, center, ttaaii, limit, sdate, edate, order) {
    div.innerHTML = '<img src="/images/wait24trans.gif"> Searching the database ...';
    
    const urlParams = new URLSearchParams({
        fmt: 'html',
        pil,
        center: center || '',
        limit: limit.toString(),
        sdate: sdate === NO_DATE_SET ? '' : sdate,
        edate: edate === NO_DATE_SET ? '' : edate,
        ttaaii: ttaaii || '',
        order
    });
    
    const url = `/cgi-bin/afos/retrieve.py?${urlParams.toString()}`;
    
    try {
        const response = await fetch(url);
        const responseText = await response.text();
        div.innerHTML = responseText;
    } catch (error) {
        div.innerHTML = `Error loading content: ${error.message}`;
    }
}

/**
 * Refresh the currently active tab
 */
function refreshActiveTab() {
    const activeLink = document.querySelector(".nav-tabs .nav-link.active");
    if (!activeLink) {
        return;
    }
    
    const activeTab = activeLink.closest('li');
    const pil = activeTab.dataset.pil;
    const limit = parseInt(activeTab.dataset.limit, 10);
    const center = activeTab.dataset.center;
    const ttaaii = activeTab.dataset.ttaaii;
    const sdate = activeTab.dataset.sdate;
    const edate = activeTab.dataset.edate;
    const order = activeTab.dataset.order;
    
    if (pil === undefined) {
        return;
    }
    
    const tabid = activeLink.getAttribute('href');
    const tabDiv = document.querySelector(tabid);
    
    if (tabDiv) {
        loadTabContent(tabDiv, pil, center, ttaaii, limit, sdate, edate, order);
    }
}

/**
 * Add a new tab for AFOS data
 */
function addTab(pil, center, ttaaii, limit, sdate, edate, doCookieSave, order) {
    // Make sure the pil is something
    if (pil === null || pil === "") {
        return;
    }
    
    // Make sure this isn't a duplicate
    const existingTab = document.querySelector(`#thetabs .nav-tabs li[data-pil='${pil}']`);
    if (existingTab) {
        return;
    }
    
    const navTabs = document.querySelector(".nav-tabs");
    const tabContent = document.querySelector('.tab-content');
    
    if (!navTabs || !tabContent) {
        return;
    }
    
    const pos = tabCounter++;
    const tabId = `tab${pos}`;
    
    // Create new tab
    const li = document.createElement('li');
    li.className = 'nav-item';
    li.setAttribute('role', 'presentation');
    li.dataset.center = text(center);
    li.dataset.sdate = text(sdate);
    li.dataset.edate = text(edate);
    li.dataset.ttaaii = text(ttaaii);
    li.dataset.limit = text(limit.toString());
    li.dataset.pil = text(pil);
    li.dataset.order = text(order);
    
    const link = document.createElement('a');
    link.className = 'nav-link';
    link.href = `#${tabId}`;
    link.setAttribute('data-bs-toggle', 'tab');
    link.setAttribute('data-bs-target', `#${tabId}`);
    link.setAttribute('role', 'tab');
    link.setAttribute('aria-controls', tabId);
    link.setAttribute('aria-selected', 'false');
    link.textContent = text(pil);
    link.addEventListener('click', (e) => {
        e.preventDefault();
        activateTab(li);
    });
    
    li.appendChild(link);
    navTabs.appendChild(li);
    
    // Create new tab content
    const tabPane = document.createElement('div');
    tabPane.className = 'tab-pane fade';
    tabPane.id = tabId;
    tabPane.setAttribute('role', 'tabpanel');
    tabPane.setAttribute('aria-labelledby', `${tabId}-tab`);
    tabContent.appendChild(tabPane);
    
    // Activate the new tab
    activateTab(li);
    
    // Load content
    loadTabContent(tabPane, pil, center, ttaaii, limit, sdate, edate, order);
    
    if (doCookieSave) {
        saveCookies();
    } else {
        // Still update URL even if not saving to cookies
        updateURLFromCurrentTabs();
    }
}

/**
 * Activate a specific tab
 */
function activateTab(targetTab) {
    // Remove active class from all nav-links and tab-panes
    document.querySelectorAll('.nav-tabs .nav-link').forEach(link => {
        link.classList.remove('active');
        link.setAttribute('aria-selected', 'false');
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active', 'show');
    });
    
    // Add active class to target tab link
    const link = targetTab.querySelector('.nav-link');
    if (link) {
        link.classList.add('active');
        link.setAttribute('aria-selected', 'true');
        
        const tabId = link.getAttribute('href');
        const tabPane = document.querySelector(tabId);
        if (tabPane) {
            tabPane.classList.add('active', 'show');
        }
    }
}
 
/**
 * Download button handler
 */
function dlbtn(btn, fmt) {
    const activeLink = document.querySelector(".nav-tabs .nav-link.active");
    if (!activeLink) {
        return;
    }
    
    const activeTab = activeLink.closest('li');
    const pil = activeTab.dataset.pil;
    if (pil === undefined) {
        return;
    }
    
    const limit = activeTab.dataset.limit;
    const center = activeTab.dataset.center;
    const ttaaii = activeTab.dataset.ttaaii;
    const order = activeTab.dataset.order;
    let sdate = activeTab.dataset.sdate;
    let edate = activeTab.dataset.edate;
    sdate = (sdate === NO_DATE_SET) ? "" : sdate;
    edate = (edate === NO_DATE_SET) ? "" : edate;
    
    window.location = `/cgi-bin/afos/retrieve.py?dl=1&fmt=${fmt}&pil=${pil}` +
        `&center=${center}&limit=${limit}&sdate=${sdate}&edate=${edate}` +
        `&ttaaii=${ttaaii}&order=${order}`;
    btn.blur();
}
/**
 * Setup UI event handlers
 */
function buildUI() {
    // Download button
    const downloadBtn = document.getElementById("toolbar-download");
    if (downloadBtn) {
        downloadBtn.addEventListener('click', (event) => {
            dlbtn(event.target, "text");
        });
    }
    
    // ZIP download button
    const zipBtn = document.getElementById("toolbar-zip");
    if (zipBtn) {
        zipBtn.addEventListener('click', (event) => {
            dlbtn(event.target, "zip");
        });
    }
    
    // Refresh button
    const refreshBtn = document.getElementById("toolbar-refresh");
    if (refreshBtn) {
        refreshBtn.addEventListener('click', (event) => {
            refreshActiveTab();
            event.target.blur();
        });
    }
    
    // Print button
    const printBtn = document.getElementById("toolbar-print");
    if (printBtn) {
        printBtn.addEventListener('click', (event) => {
            event.target.blur();
            const activeLink = document.querySelector(".nav-tabs .nav-link.active");
            if (!activeLink) {
                return;
            }
            const activeTab = activeLink.closest('li');
            const pil = activeTab.dataset.pil;
            if (pil === undefined) {
                return;
            }
            const tabid = activeLink.getAttribute('href');
            const divToPrint = document.querySelector(tabid);
            
            if (divToPrint) {
                const newWin = window.open('', 'Print-Window');
                newWin.document.open();
                newWin.document.write(`<html><body onload="window.print()">${divToPrint.innerHTML}</body></html>`);
                newWin.document.close();
                setTimeout(() => { newWin.close(); }, 10);
            }
        });
    }
    
    // Close button
    const closeBtn = document.getElementById("toolbar-close");
    if (closeBtn) {
        closeBtn.addEventListener('click', (event) => {
            event.target.blur();
            const activeLink = document.querySelector(".nav-tabs .nav-link.active");
            if (!activeLink) {
                return;
            }
            const activeTab = activeLink.closest('li');
            const pil = activeTab.dataset.pil;
            if (pil === undefined) {
                return;
            }
            const tabid = activeLink.getAttribute('href');
            const tabPane = document.querySelector(tabid);
            
            // Remove tab and content
            activeTab.remove();
            if (tabPane) {
                tabPane.remove();
            }
            
            // Activate the last remaining tab
            const lastTab = document.querySelector(".nav-tabs li:last-child");
            if (lastTab) {
                activateTab(lastTab);
            }
            
            // Update both cookies and URL
            saveCookies();
        });
    }
    
    // Form submit button
    const submitBtn = document.getElementById("myform-submit");
    if (submitBtn) {
        submitBtn.addEventListener('click', (event) => {
            const pilInput = document.querySelector("#myform input[name='pil']");
            const centerInput = document.querySelector("#myform input[name='center']");
            const ttaaiiInput = document.querySelector("#myform input[name='ttaaii']");
            const limitInput = document.querySelector("#myform input[name='limit']");
            const sdateInput = document.getElementById("sdate");
            const edateInput = document.getElementById("edate");
            const orderInput = document.querySelector("#myform input[name='order']:checked");
            
            if (!pilInput || !limitInput || !orderInput) {
                return;
            }
            
            const pil = pilInput.value.toUpperCase();
            const center = centerInput ? centerInput.value.toUpperCase() : '';
            const ttaaii = ttaaiiInput ? ttaaiiInput.value.toUpperCase() : '';
            const limit = parseInt(limitInput.value, 10);
            const sdate = sdateInput ? sdateInput.value : '';
            const edate = edateInput ? edateInput.value : '';
            const order = orderInput.value;
            
            addTab(pil, center, ttaaii, limit, sdate, edate, true, order);
            event.target.blur();
        });
    }
}

/**
 * Initialize the application when DOM is ready
 */
function init() {
    buildUI();
    
    // Try modern URL params first, fall back to legacy hash, then cookies
    if (!readURLParams()) {
        if (!readAnchorTags()) {
            readCookies();
        }
    }
    
    // Always save to ensure URL is updated to modern format
    saveCookies();
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // DOM already loaded
    init();
}
