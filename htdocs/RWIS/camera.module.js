
import { escapeHTML, getElement, getInputElement, requireInputElement } from '/js/iemjs/domUtils.js';

/**
 * Format date for display
 * @param {Date} date 
 * @returns {string} formatted date string
 */
function formatDateForDisplay(date) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const month = months[date.getMonth()];
    const day = date.getDate().toString().padStart(2, '0');
    return `${month} ${day} `;
}

/**
 * Parse ISO date string
 * @param {string} val ISO date string
 * @returns {Date|null} parsed date or null
 */
function parseISODate(val) {
    if (typeof val !== 'string') return null;
    const reIsoDate = /^(\d{4})-(\d{2})-(\d{2})((T)(\d{2}):(\d{2})(:(\d{2})(\.\d*)?)?)?(Z)?$/;
    const mm = val.match(reIsoDate);
    if (mm) {
        return new Date(Date.UTC(
            Number(mm[1]), 
            Number(mm[2]) - 1, 
            Number(mm[3]), 
            Number(mm[6]) || 0, 
            Number(mm[7]) || 0, 
            Number(mm[9]) || 0, 
            parseInt((Number(mm[10])) * 1000, 10) || 0
        ));
    }
    return null;
}

/**
 * Set up date picker functionality
 */
function setupDatePicker() {
    const datePicker = requireInputElement('datepicker');
    const realDateInput = requireInputElement('realdate');
    
    // Set up HTML5 date input
    datePicker.type = 'date';
    datePicker.min = '2009-12-19'; // Minimum date from PHP
    
    // Set default date to today
    const today = new Date();
    const todayString = today.toISOString().split('T')[0];
    datePicker.value = todayString;
    
    // Set real date field for backend - use 4-digit year format (YYYYMMDD)
    // Parse date string directly to avoid timezone drift issues
    const formatDateForBackend = (dateStr) => {
        const [year, month, day] = dateStr.split('-');
        return `${year}${month.padStart(2, '0')}${day.padStart(2, '0')}`;
    };
    
    realDateInput.value = formatDateForBackend(todayString);
    
    // Add event listener for date changes
    datePicker.addEventListener('change', () => {
        realDateInput.value = formatDateForBackend(datePicker.value);
        fetchTimes(false);
    });
}

/**
 * Fetch available times for selected camera and date
 * @param {string|boolean} findTime specific time to select after loading
 */
function fetchTimes(findTime) {
    const cidSelect = document.querySelector('select[name=cid]');
    const realDateInput = getInputElement('realdate');
    const timesSelect = document.querySelector('select[name=times]');
    
    const cid = cidSelect.value;
    const myDate = realDateInput.value;
    
    timesSelect.innerHTML = "<option value='-1'>Loading...</option>";
    
    fetch(`/json/webcam.py?cid=${cid}&date=${myDate}`)
        .then(response => response.json())
        .then(data => {
            let html = '';
            const len = data.images.length;
            
            for (let i = 0; i < len; i++) {
                const ts = parseISODate(data.images[i].valid);
                if (!ts) continue;
                
                const dateStr = formatDateForDisplay(ts);
                let hour = ts.getHours();
                const period = hour >= 12 ? ' PM' : ' AM';
                
                if (hour > 12) {
                    hour = hour - 12;
                } else if (hour === 0) {
                    hour = 12;
                }
                
                const minutes = ts.getMinutes().toString().padStart(2, '0');
                const timeStr = `${dateStr}${hour}:${minutes}${period}`;
                
                html += `<option ts="${data.images[i].valid}" value="${data.images[i].href}">${timeStr}</option>`;
            }
            
            if (len === 0) {
                html += "<option value='-1'>No Images Found!</option>";
            }
            
            timesSelect.innerHTML = html;
            
            if (findTime) {
                const targetOption = timesSelect.querySelector(`option[ts="${findTime}"]`);
                if (targetOption) {
                    targetOption.selected = true;
                    getImage();
                }
            }
        })
        .catch(() => {
            // Handle error by showing appropriate message to user
            timesSelect.innerHTML = "<option value='-1'>Error loading times</option>";
        });
}

/**
 * Update URL with URLSearchParams instead of hash
 * @param {string} filename current image filename
 */
function updateURL(filename) {
    const url = new URL(window.location);
    url.searchParams.set('image', filename);
    window.history.replaceState({}, '', url);
}

/**
 * Get URL parameters from current location
 * @returns {URLSearchParams} current URL search parameters
 */
function getURLParams() {
    return new URLSearchParams(window.location.search);
}

/**
 * Migrate legacy hash URLs to URLSearchParams
 * This maintains backward compatibility with old bookmarked URLs
 */
function migrateLegacyHashURLs() {
    const hash = window.location.hash;
    if (hash && hash.length > 1) {
        const filename = hash.substring(1); // Remove the # character
        const url = new URL(window.location);
        
        // Clear the hash and set as URL parameter
        url.hash = '';
        url.searchParams.set('image', filename);
        
        // Replace the URL without adding to history
        window.history.replaceState({}, '', url);
        
        return filename;
    }
    return null;
}

/**
 * Load and display selected image
 */
function getImage() {
    const timesSelect = document.querySelector('select[name=times]');
    const theImage = getElement('theimage');
    
    const href = escapeHTML(timesSelect.value);
    if (href && href !== '-1') {
        // Show loading indicator
        showLoadingState(true);
        
        const fn = href.split('/');
        const filename = fn[fn.length - 1];
        
        // Update URL with URLSearchParams instead of hash
        updateURL(filename);
        
        // Preload image to handle loading states
        const newImage = new Image();
        newImage.onload = () => {
            theImage.src = newImage.src;
            showLoadingState(false);
            updateImageInfo(timesSelect.selectedOptions[0].textContent);
        };
        newImage.onerror = () => {
            theImage.alt = 'Failed to load image';
            showLoadingState(false);
            updateImageInfo('Error loading image');
        };
        newImage.src = href;
    }
}

/**
 * Show/hide loading state for image
 * @param {boolean} isLoading whether to show loading state
 */
function showLoadingState(isLoading) {
    const theImage = getElement('theimage');
    const container = theImage.parentElement;
    
    if (isLoading) {
        container.style.opacity = '0.6';
        container.style.cursor = 'wait';
    } else {
        container.style.opacity = '1';
        container.style.cursor = 'default';
    }
}

/**
 * Update image information display
 * @param {string} timeInfo time information to display
 */
function updateImageInfo(timeInfo) {
    let infoElement = getElement('image-info');
    if (!infoElement) {
        infoElement = document.createElement('div');
        infoElement.id = 'image-info';
        infoElement.style.cssText = 'margin-top: 10px; font-weight: bold; text-align: center; color: #666;';
        getElement('theimage').parentElement.appendChild(infoElement);
    }
    infoElement.textContent = `Current Image: ${timeInfo}`;
}

/**
 * Parse URL parameters to set initial state
 * Handles both URLSearchParams and legacy hash URLs (with migration)
 */
function parseURLParams() {
    // First, check for legacy hash URLs and migrate them
    const migratedFilename = migrateLegacyHashURLs();
    
    // Get current URL parameters (either from migration or existing params)
    const params = getURLParams();
    const imageParam = params.get('image') || migratedFilename;
    
    if (imageParam) {
        const fnTokens = imageParam.split("_");
        if (fnTokens.length === 2) {
            const cid = fnTokens[0];
            const tpart = fnTokens[1];
            
            // Set camera ID
            const cidSelect = document.querySelector('select[name=cid]');
            const cidOption = cidSelect.querySelector(`option[value="${cid}"]`);
            if (cidOption) {
                cidOption.selected = true;
            }
            
            // Set date
            const year = tpart.substring(0, 4);
            const month = tpart.substring(4, 6);
            const day = tpart.substring(6, 8);
            const dateStr = `${year}-${month}-${day}`;
            
            const datePicker = getInputElement('datepicker');
            const realDateInput = getInputElement('realdate');
            
            datePicker.value = dateStr;
            realDateInput.value = `${year}${month}${day}`; // YYYYMMDD format for backend
            
            // Create ISO time string for selection
            const hour = tpart.substring(8, 10);
            const minute = tpart.substring(10, 12);
            const isotime = `${year}-${month}-${day}T${hour}:${minute}:00Z`;
            
            fetchTimes(isotime);
        } else {
            fetchTimes(false);
        }
    } else {
        fetchTimes(false);
    }
}

/**
 * Handle browser back/forward navigation
 */
function handlePopState() {
    parseURLParams();
}

/**
 * Add navigation controls for easier image browsing
 */
function addNavigationControls() {
    const timesSelect = document.querySelector('select[name=times]');
    const controlsDiv = document.createElement('div');
    controlsDiv.style.cssText = 'margin-top: 10px; text-align: center;';
    
    // Previous/Next buttons
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '← Previous';
    prevBtn.className = 'btn btn-sm btn-secondary';
    prevBtn.style.marginRight = '10px';
    prevBtn.onclick = () => navigateImage(-1);
    
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next →';
    nextBtn.className = 'btn btn-sm btn-secondary';
    nextBtn.onclick = () => navigateImage(1);
    
    // Auto-play toggle
    const autoPlayBtn = document.createElement('button');
    autoPlayBtn.textContent = 'Auto-play';
    autoPlayBtn.className = 'btn btn-sm btn-info';
    autoPlayBtn.style.marginLeft = '20px';
    autoPlayBtn.onclick = toggleAutoPlay;
    
    controlsDiv.appendChild(prevBtn);
    controlsDiv.appendChild(nextBtn);
    controlsDiv.appendChild(autoPlayBtn);
    
    timesSelect.parentElement.appendChild(controlsDiv);
}

/**
 * Navigate to previous/next image
 * @param {number} direction -1 for previous, 1 for next
 */
function navigateImage(direction) {
    const timesSelect = document.querySelector('select[name=times]');
    const currentIndex = timesSelect.selectedIndex;
    const maxIndex = timesSelect.options.length - 1;
    
    if (direction === -1 && currentIndex > 0) {
        timesSelect.selectedIndex = currentIndex - 1;
    } else if (direction === 1 && currentIndex < maxIndex) {
        timesSelect.selectedIndex = currentIndex + 1;
    }
    getImage();
}

let autoPlayInterval = null;

/**
 * Toggle auto-play functionality
 */
function toggleAutoPlay() {
    const autoPlayBtn = document.querySelector('button:nth-of-type(3)');
    
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
        autoPlayBtn.textContent = 'Auto-play';
        autoPlayBtn.className = 'btn btn-sm btn-info';
    } else {
        autoPlayInterval = setInterval(() => {
            const timesSelect = document.querySelector('select[name=times]');
            const currentIndex = timesSelect.selectedIndex;
            const maxIndex = timesSelect.options.length - 1;
            
            if (currentIndex < maxIndex) {
                navigateImage(1);
            } else {
                // Loop back to start
                timesSelect.selectedIndex = 0;
                getImage();
            }
        }, 2000); // 2 second intervals
        
        autoPlayBtn.textContent = 'Stop Auto-play';
        autoPlayBtn.className = 'btn btn-sm btn-warning';
    }
}

/**
 * Initialize the application
 */
function init() {
    setupDatePicker();
    addNavigationControls();
    
    // Set up event listeners
    const cidSelect = document.querySelector('select[name=cid]');
    const timesSelect = document.querySelector('select[name=times]');
    const datePicker = document.getElementById('datepicker');
    
    cidSelect.addEventListener('change', () => {
        // Stop auto-play when changing cameras
        if (autoPlayInterval) {
            toggleAutoPlay();
        }
        // Clear image parameter when changing cameras
        const url = new URL(window.location);
        url.searchParams.delete('image');
        window.history.replaceState({}, '', url);
        fetchTimes(false);
    });
    
    // Update URL when date changes
    datePicker.addEventListener('change', () => {
        const url = new URL(window.location);
        url.searchParams.delete('image'); // Clear image when date changes
        window.history.replaceState({}, '', url);
    });
    
    timesSelect.addEventListener('change', () => {
        getImage();
    });
    
    // Enhanced keyboard navigation
    document.addEventListener('keydown', (event) => {
        const timesSelectElement = document.querySelector('select[name=times]');
        
        // Allow keyboard navigation when focused on times select or image area
        if (document.activeElement === timesSelectElement || 
            event.target.id === 'theimage' ||
            event.target.tagName === 'SELECT' || 
            event.target.tagName === 'INPUT') {
            
            if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
                event.preventDefault();
                navigateImage(-1);
            } else if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
                event.preventDefault();
                navigateImage(1);
            } else if (event.key === ' ' || event.key === 'Spacebar') {
                event.preventDefault();
                toggleAutoPlay();
            }
        }
    });
    
    // Make image clickable for better UX
    document.addEventListener('click', (event) => {
        if (event.target.id === 'theimage') {
            event.target.focus();
        }
    });
    
    // Handle browser back/forward navigation
    window.addEventListener('popstate', handlePopState);
    
    // Parse URL parameters and initialize (handles both URLSearchParams and legacy hash migration)
    parseURLParams();
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
