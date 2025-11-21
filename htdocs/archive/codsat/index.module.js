/**
 * MTArchive + COD Satellite Browser
 *
 * Provides cascading selection UI and animation controls for GOES satellite imagery
 * from the Iowa State MTArchive powered by College of DuPage NEXLAB
 */

const BASE_URL = "https://mtarchive.geol.iastate.edu";

// State management
const state = {
    date: null,
    satellite: null,
    sectorType: null,
    sector: null,
    plotType: null,
    images: [],
    currentIndex: 0,
    currentTimestamp: null,
    isPlaying: false,
    animationInterval: null,
    speed: 500,
    skipFrames: 1,
    loop: true
};

// DOM elements
const elements = {
    dateSelect: null,
    satelliteSelect: null,
    sectorTypeSelect: null,
    sectorSelect: null,
    plotTypeSelect: null,
    satelliteImage: null,
    playBtn: null,
    stopBtn: null,
    speedSlider: null,
    speedValue: null,
    skipSlider: null,
    skipValue: null,
    loopCheck: null,
    currentFrame: null,
    totalFrames: null,
    currentTime: null,
    timeline: null,
    imageWrapper: null,
    noImageMessage: null,
    animationCard: null,
    imageCount: null,
    loadingRow: null,
    imagesLoadedRow: null,
    shareBtn: null
};

/**
 * Initialize the application
 */
function init() {
    // Cache DOM elements
    elements.dateSelect = document.getElementById("dateSelect");
    elements.satelliteSelect = document.getElementById("satelliteSelect");
    elements.sectorTypeSelect = document.getElementById("sectorTypeSelect");
    elements.sectorSelect = document.getElementById("sectorSelect");
    elements.plotTypeSelect = document.getElementById("plotTypeSelect");
    elements.satelliteImage = document.getElementById("satelliteImage");
    elements.playBtn = document.getElementById("playBtn");
    elements.stopBtn = document.getElementById("stopBtn");
    elements.speedSlider = document.getElementById("speedSlider");
    elements.speedValue = document.getElementById("speedValue");
    elements.skipSlider = document.getElementById("skipSlider");
    elements.skipValue = document.getElementById("skipValue");
    elements.loopCheck = document.getElementById("loopCheck");
    elements.currentFrame = document.getElementById("currentFrame");
    elements.totalFrames = document.getElementById("totalFrames");
    elements.currentTime = document.getElementById("currentTime");
    elements.timeline = document.getElementById("timeline");
    elements.imageWrapper = document.getElementById("imageWrapper");
    elements.noImageMessage = document.getElementById("noImageMessage");
    elements.animationCard = document.getElementById("animationCard");
    elements.imageCount = document.getElementById("imageCount");
    elements.loadingRow = document.getElementById("loadingRow");
    elements.imagesLoadedRow = document.getElementById("imagesLoadedRow");
    elements.shareBtn = document.getElementById("shareBtn");

    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    elements.dateSelect.value = today;
    elements.dateSelect.max = today;

    // Attach event listeners
    attachEventListeners();

    // Load state from URL parameters if present
    loadStateFromURL();
}

/**
 * Load state from URL parameters
 */
async function loadStateFromURL() {
    const params = new URLSearchParams(window.location.search);

    const urlState = {
        date: params.get('date'),
        satellite: params.get('satellite'),
        sectorType: params.get('sectorType'),
        sector: params.get('sector'),
        plotType: params.get('plotType'),
        speed: params.get('speed'),
        skipFrames: params.get('skip'),
        loop: params.get('loop'),
        timestamp: params.get('timestamp')
    };

    // Apply speed and loop settings if present
    if (urlState.speed) {
        state.speed = parseInt(urlState.speed);
        elements.speedSlider.value = urlState.speed;
        elements.speedValue.textContent = urlState.speed;
    }

    if (urlState.skipFrames) {
        state.skipFrames = parseInt(urlState.skipFrames);
        elements.skipSlider.value = urlState.skipFrames;
        elements.skipValue.textContent = urlState.skipFrames;
    }

    if (urlState.loop !== null) {
        state.loop = urlState.loop === 'true';
        elements.loopCheck.checked = state.loop;
    }

    // Store timestamp for later use
    if (urlState.timestamp) {
        state.currentTimestamp = urlState.timestamp;
    }

    // If no date parameter, we're done
    if (!urlState.date) return;

    // Set date and trigger cascade
    elements.dateSelect.value = urlState.date;
    state.date = urlState.date;

    try {
        await loadCascadingSelections(urlState);
    } catch {
        // Silently fail - user can manually select options
    }
}

/**
 * Load cascading selections from URL state
 */
async function loadCascadingSelections(urlState) {
    // Load satellites
    showRow("satelliteRow");
    const satellites = await fetchAvailableSatellites(urlState.date);
    populateSelect(elements.satelliteSelect, satellites, "Select satellite...");
    elements.satelliteSelect.disabled = false;

    if (!urlState.satellite || !satellites.includes(urlState.satellite)) return;

    elements.satelliteSelect.value = urlState.satellite;
    state.satellite = urlState.satellite;

    // Continue loading sector types and beyond
    await loadSectorTypesAndBeyond(urlState);
}

/**
 * Load sector types and subsequent selections
 */
async function loadSectorTypesAndBeyond(urlState) {
    hideFromRow("sectorTypeRow");
    showRow("sectorTypeRow");
    const sectorTypes = await fetchAvailableSectorTypes(urlState.date, urlState.satellite);
    populateSelect(elements.sectorTypeSelect, sectorTypes, "Select sector type...");
    elements.sectorTypeSelect.disabled = false;

    if (!urlState.sectorType || !sectorTypes.includes(urlState.sectorType)) return;

    elements.sectorTypeSelect.value = urlState.sectorType;
    state.sectorType = urlState.sectorType;

    // Continue loading sectors and beyond
    await loadSectorsAndBeyond(urlState);
}

/**
 * Load sectors and subsequent selections
 */
async function loadSectorsAndBeyond(urlState) {
    hideFromRow("sectorRow");
    showRow("sectorRow");
    const sectors = await fetchAvailableSectors(urlState.date, urlState.satellite, urlState.sectorType);
    populateSelect(elements.sectorSelect, sectors, "Select sector...");
    elements.sectorSelect.disabled = false;

    if (!urlState.sector || !sectors.includes(urlState.sector)) return;

    elements.sectorSelect.value = urlState.sector;
    state.sector = urlState.sector;

    // Continue loading plot types and images
    await loadPlotTypesAndImages(urlState);
}

/**
 * Load plot types and images
 */
async function loadPlotTypesAndImages(urlState) {
    hideFromRow("plotTypeRow");
    showRow("plotTypeRow");
    const plotTypes = await fetchAvailablePlotTypes(urlState.date, urlState.satellite, urlState.sectorType, urlState.sector);
    populateSelect(elements.plotTypeSelect, plotTypes, "Select plot type...");
    elements.plotTypeSelect.disabled = false;

    if (!urlState.plotType || !plotTypes.includes(urlState.plotType)) return;

    elements.plotTypeSelect.value = urlState.plotType;
    state.plotType = urlState.plotType;

    // Load images
    await loadImagesForSelection();
}

/**
 * Load images for current selection
 */
async function loadImagesForSelection() {
    elements.loadingRow.style.display = "block";
    const images = await fetchAvailableImages(
        state.date,
        state.satellite,
        state.sectorType,
        state.sector,
        state.plotType
    );
    state.images = images;
    elements.loadingRow.style.display = "none";

    if (images.length > 0) {
        elements.imagesLoadedRow.style.display = "block";
        elements.imageCount.textContent = images.length;
        elements.totalFrames.textContent = images.length;
        elements.animationCard.style.display = "block";

        // Check if we have a timestamp from URL to load specific frame
        let initialIndex = 0;
        if (state.currentTimestamp) {
            const timestampIndex = images.findIndex(img => img.timestamp === state.currentTimestamp);
            if (timestampIndex !== -1) {
                initialIndex = timestampIndex;
            }
        }

        // Set current index before rendering timeline
        state.currentIndex = initialIndex;

        // Show wrapper first so timeline can measure correctly
        elements.imageWrapper.style.display = "block";
        elements.noImageMessage.style.display = "none";

        // Use requestAnimationFrame to ensure layout is updated before measuring
        requestAnimationFrame(() => {
            // Render the timeline with correct index and width
            renderTimeline();

            // Load the image
            loadImage(initialIndex);
        });
    }
}

/**
 * Update URL with current state
 */
function updateURL() {
    const params = new URLSearchParams();

    // Add parameters that exist
    const paramMap = {
        date: state.date,
        satellite: state.satellite,
        sectorType: state.sectorType,
        sector: state.sector,
        plotType: state.plotType
    };

    Object.entries(paramMap).forEach(([key, value]) => {
        if (value) params.set(key, value);
    });

    // Add current timestamp if available
    if (state.currentTimestamp) {
        params.set('timestamp', state.currentTimestamp);
    }

    // Add non-default settings
    if (state.speed !== 500) params.set('speed', state.speed);
    if (state.skipFrames !== 1) params.set('skip', state.skipFrames);
    if (!state.loop) params.set('loop', 'false');

    const queryString = params.toString();
    const newURL = queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
    window.history.replaceState({}, '', newURL);
}

/**
 * Attach all event listeners
 */
function attachEventListeners() {
    elements.dateSelect.addEventListener("change", handleDateChange);
    elements.satelliteSelect.addEventListener("change", handleSatelliteChange);
    elements.sectorTypeSelect.addEventListener("change", handleSectorTypeChange);
    elements.sectorSelect.addEventListener("change", handleSectorChange);
    elements.plotTypeSelect.addEventListener("change", handlePlotTypeChange);

    elements.playBtn.addEventListener("click", playAnimation);
    elements.stopBtn.addEventListener("click", stopAnimation);

    elements.speedSlider.addEventListener("input", (e) => {
        state.speed = parseInt(e.target.value);
        elements.speedValue.textContent = state.speed;
        updateURL();
        if (state.isPlaying) {
            stopAnimation();
            playAnimation();
        }
    });

    elements.skipSlider.addEventListener("input", (e) => {
        state.skipFrames = parseInt(e.target.value);
        elements.skipValue.textContent = state.skipFrames;
        updateURL();
    });

    elements.loopCheck.addEventListener("change", (e) => {
        state.loop = e.target.checked;
        updateURL();
    });

    elements.shareBtn.addEventListener("click", copyShareLink);

    // Keyboard shortcuts
    document.addEventListener("keydown", handleKeyboardInput);

    // Re-render timeline on window resize
    let resizeTimeout = null;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (state.images.length > 0) {
                renderTimeline();
            }
        }, 250);
    });
}

/**
 * Handle date selection change
 */
async function handleDateChange() {
    const date = elements.dateSelect.value;
    if (!date) return;

    state.date = date;
    state.satellite = null;
    state.sectorType = null;
    state.sector = null;
    state.plotType = null;
    state.images = [];

    resetUI();
    showRow("satelliteRow");
    updateURL();

    try {
        const satellites = await fetchAvailableSatellites(date);
        populateSelect(elements.satelliteSelect, satellites, "Select satellite...");
        elements.satelliteSelect.disabled = false;
    } catch {
        showError(elements.satelliteSelect, "Failed to load satellites");
    }
}

/**
 * Handle satellite selection change
 */
async function handleSatelliteChange() {
    const satellite = elements.satelliteSelect.value;
    if (!satellite) return;

    state.satellite = satellite;
    state.sectorType = null;
    state.sector = null;
    state.plotType = null;
    state.images = [];

    hideFromRow("sectorTypeRow");
    showRow("sectorTypeRow");
    updateURL();

    try {
        const sectorTypes = await fetchAvailableSectorTypes(state.date, satellite);
        populateSelect(elements.sectorTypeSelect, sectorTypes, "Select sector type...");
        elements.sectorTypeSelect.disabled = false;
    } catch {
        showError(elements.sectorTypeSelect, "Failed to load sector types");
    }
}

/**
 * Handle sector type selection change
 */
async function handleSectorTypeChange() {
    const sectorType = elements.sectorTypeSelect.value;
    if (!sectorType) return;

    state.sectorType = sectorType;
    state.sector = null;
    state.plotType = null;
    state.images = [];

    hideFromRow("sectorRow");
    showRow("sectorRow");
    updateURL();

    try {
        const sectors = await fetchAvailableSectors(state.date, state.satellite, sectorType);
        populateSelect(elements.sectorSelect, sectors, "Select sector...");
        elements.sectorSelect.disabled = false;
    } catch {
        showError(elements.sectorSelect, "Failed to load sectors");
    }
}

/**
 * Handle sector selection change
 */
async function handleSectorChange() {
    const sector = elements.sectorSelect.value;
    if (!sector) return;

    state.sector = sector;
    state.plotType = null;
    state.images = [];

    hideFromRow("plotTypeRow");
    showRow("plotTypeRow");
    updateURL();

    try {
        const plotTypes = await fetchAvailablePlotTypes(state.date, state.satellite, state.sectorType, sector);
        populateSelect(elements.plotTypeSelect, plotTypes, "Select plot type...");
        elements.plotTypeSelect.disabled = false;
    } catch {
        showError(elements.plotTypeSelect, "Failed to load plot types");
    }
}

/**
 * Handle plot type selection change
 */
async function handlePlotTypeChange() {
    const plotType = elements.plotTypeSelect.value;
    if (!plotType) return;

    state.plotType = plotType;
    state.images = [];
    state.currentIndex = 0;

    elements.loadingRow.style.display = "block";
    elements.imagesLoadedRow.style.display = "none";
    updateURL();

    try {
        const images = await fetchAvailableImages(
            state.date,
            state.satellite,
            state.sectorType,
            state.sector,
            plotType
        );

        state.images = images;
        elements.loadingRow.style.display = "none";

        if (images.length > 0) {
            elements.imagesLoadedRow.style.display = "block";
            elements.imageCount.textContent = images.length;
            elements.totalFrames.textContent = images.length;
            elements.animationCard.style.display = "block";

            // Set current index
            state.currentIndex = 0;

            // Show wrapper first so timeline can measure correctly
            elements.imageWrapper.style.display = "block";
            elements.noImageMessage.style.display = "none";

            // Use requestAnimationFrame to ensure layout is updated before measuring
            requestAnimationFrame(() => {
                // Render timeline with correct width
                renderTimeline();

                // Load first image
                loadImage(0);
            });
        } else {
            showError(null, "No images found for this selection");
        }
    } catch {
        elements.loadingRow.style.display = "none";
        showError(null, "Failed to load images");
    }
}

/**
 * Fetch available satellites for a date
 */
async function fetchAvailableSatellites(date) {
    const [year, month, day] = date.split('-');
    const url = `${BASE_URL}/${year}/${month}/${day}/cod/sat/`;

    const dirs = await fetchDirectoryListing(url);
    return dirs.filter(d => d.startsWith('goes')).sort();
}

/**
 * Fetch available sector types for a satellite
 */
async function fetchAvailableSectorTypes(date, satellite) {
    const [year, month, day] = date.split('-');
    const url = `${BASE_URL}/${year}/${month}/${day}/cod/sat/${satellite}/`;

    return await fetchDirectoryListing(url);
}

/**
 * Fetch available sectors for a sector type
 */
async function fetchAvailableSectors(date, satellite, sectorType) {
    const [year, month, day] = date.split('-');
    const url = `${BASE_URL}/${year}/${month}/${day}/cod/sat/${satellite}/${sectorType}/`;

    return await fetchDirectoryListing(url);
}

/**
 * Fetch available plot types for a sector
 */
async function fetchAvailablePlotTypes(date, satellite, sectorType, sector) {
    const [year, month, day] = date.split('-');
    const url = `${BASE_URL}/${year}/${month}/${day}/cod/sat/${satellite}/${sectorType}/${sector}/`;

    return await fetchDirectoryListing(url);
}

/**
 * Fetch available images from 000index.txt
 */
async function fetchAvailableImages(date, satellite, sectorType, sector, plotType) {
    const [year, month, day] = date.split('-');
    const url = `${BASE_URL}/${year}/${month}/${day}/cod/sat/${satellite}/${sectorType}/${sector}/${plotType}/000index.txt`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const text = await response.text();
        const lines = text.split('\n').filter(line => line.trim() && line.endsWith('.jpg'));

        // Build full URLs and extract timestamps
        return lines.map(filename => {
            const fullUrl = `${BASE_URL}/${year}/${month}/${day}/cod/sat/${satellite}/${sectorType}/${sector}/${plotType}/${filename.trim()}`;
            const timestamp = extractTimestamp(filename);
            return { url: fullUrl, filename: filename.trim(), timestamp };
        });
    } catch {
        return [];
    }
}

/**
 * Extract timestamp from filename
 * Format: sector_band_YYYYMMDDHHmmss.jpg
 */
function extractTimestamp(filename) {
    const match = filename.match(/(\d{14})/);
    if (match) {
        const ts = match[1];
        const year = ts.substring(0, 4);
        const month = ts.substring(4, 6);
        const day = ts.substring(6, 8);
        const hour = ts.substring(8, 10);
        const minute = ts.substring(10, 12);
        const second = ts.substring(12, 14);

        return `${year}-${month}-${day} ${hour}:${minute}:${second} UTC`;
    }
    return "Unknown";
}

/**
 * Fetch directory listing by parsing HTML
 */
async function fetchDirectoryListing(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const links = doc.querySelectorAll('a');

        const dirs = [];
        links.forEach(link => {
            const href = link.getAttribute('href');
            const dirName = extractValidDirectoryName(href);
            if (dirName) {
                dirs.push(dirName);
            }
        });

        return dirs.sort();
    } catch {
        return [];
    }
}

/**
 * Extract valid directory name from href
 * Returns null if href is not a valid local directory
 */
function extractValidDirectoryName(href) {
    if (!href || !href.endsWith('/')) return null;

    // Match simple directory names: alphanumeric, underscores, hyphens, followed by /
    // This excludes ../, /, paths with slashes, and URLs
    const match = href.match(/^([a-zA-Z0-9_-]+)\/$/);
    return match ? match[1] : null;
}

/**
 * Populate select element with options
 */
function populateSelect(selectElement, options, placeholder) {
    selectElement.innerHTML = `<option value="">${placeholder}</option>`;

    options.forEach(option => {
        const optElement = document.createElement('option');
        optElement.value = option;
        optElement.textContent = formatOptionText(option);
        selectElement.appendChild(optElement);
    });
}

/**
 * Format option text for display
 */
function formatOptionText(text) {
    // Capitalize and format common patterns
    const formatted = text
        .replace(/^abi(\d+)$/, 'ABI Band $1')
        .replace(/^goes(\d+)$/, 'GOES-$1')
        .replace(/natcolor/, 'Natural Color')
        .replace(/natcolorfire/, 'Natural Color + Fire')
        .replace(/truecolor/, 'True Color')
        .replace(/airmass/, 'Air Mass')
        .replace(/dcphase/, 'Day Cloud Phase')
        .replace(/ntmicro/, 'Night Microphysics')
        .replace(/sandwich/, 'Sandwich')
        .replace(/simplewv/, 'Simple Water Vapor');

    return formatted;
}

/**
 * Load and display an image
 */
function loadImage(index) {
    if (index < 0 || index >= state.images.length) return;

    state.currentIndex = index;
    const imageData = state.images[index];

    elements.satelliteImage.src = imageData.url;
    elements.currentFrame.textContent = index + 1;
    elements.currentTime.textContent = imageData.timestamp;

    // Update state and URL with current timestamp
    state.currentTimestamp = imageData.timestamp;
    updateURL();

    // Update timeline visualization
    updateTimelinePosition();

    // Preload next few images for smoother playback
    preloadImages(index);
}

/**
 * Preload next few images for smoother animation
 */
function preloadImages(startIndex) {
    const preloadCount = 5;
    for (let i = 1; i <= preloadCount; i++) {
        const nextIndex = startIndex + (i * state.skipFrames);
        if (nextIndex < state.images.length && state.images[nextIndex]) {
            const img = new Image();
            img.src = state.images[nextIndex].url;
        }
    }
}

/**
 * Render interactive timeline with clickable dots for each frame
 */
function renderTimeline() {
    if (!state.images || state.images.length === 0) return;

    const svg = elements.timeline;
    const width = svg.clientWidth || 800;
    const height = 50;
    const margin = { left: 30, right: 30, top: 10, bottom: 20 };
    const chartWidth = width - margin.left - margin.right;

    // Clear existing content
    svg.innerHTML = '';
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    // Draw timeline line
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', margin.left);
    line.setAttribute('y1', height / 2);
    line.setAttribute('x2', width - margin.right);
    line.setAttribute('y2', height / 2);
    line.setAttribute('class', 'timeline-line');
    svg.appendChild(line);

    // Calculate positions for dots
    const dotSpacing = chartWidth / (state.images.length - 1 || 1);

    // For large datasets, we need to sample dots to avoid overcrowding
    // Show max ~100 dots, but always include first, last, and current
    const maxDots = 100;
    const shouldSample = state.images.length > maxDots;
    const sampleRate = shouldSample ? Math.ceil(state.images.length / maxDots) : 1;

    // Track which indices have dots rendered (for updateTimelinePosition)
    const renderedIndices = new Set();    // Draw dots for each frame
    // eslint-disable-next-line complexity
    state.images.forEach((image, index) => {
        // Always show first, last, and current frame
        const isFirst = index === 0;
        const isLast = index === state.images.length - 1;
        const isCurrent = index === state.currentIndex;
        const isSampled = index % sampleRate === 0;

        if (!isFirst && !isLast && !isCurrent && !isSampled) {
            return; // Skip this dot
        }

        renderedIndices.add(index);        const x = margin.left + (index * dotSpacing);
        const y = height / 2;

        // Check if this is the current/active frame
        const isActive = index === state.currentIndex;

        // Create dot with larger size for active frame
        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', x);
        dot.setAttribute('cy', y);
        dot.setAttribute('r', isActive ? 6 : 3);
        dot.setAttribute('fill', isActive ? '#dc3545' : '#0d6efd');
        dot.setAttribute('stroke', '#fff');
        dot.setAttribute('stroke-width', isActive ? 2 : 1);
        dot.setAttribute('class', isActive ? 'timeline-dot active' : 'timeline-dot');
        dot.setAttribute('data-index', index);
        dot.setAttribute('data-timestamp', image.timestamp);

        // Add click handler
        dot.addEventListener('click', () => {
            if (state.isPlaying) {
                stopAnimation();
            }
            loadImage(index);
        });

        // Add hover title
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = image.timestamp;
        dot.appendChild(title);

        svg.appendChild(dot);

        // Add time labels for first, middle, and last frames
        const shouldShowLabel = index === 0 ||
                               index === Math.floor(state.images.length / 2) ||
                               index === state.images.length - 1;

        if (shouldShowLabel) {
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', x);
            label.setAttribute('y', height - 5);
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('class', 'timeline-label');
            label.textContent = image.timestamp.substring(11, 16); // HH:mm
            svg.appendChild(label);
        }
    });

    // Update the active position
    updateTimelinePosition();
}

/**
 * Update timeline to highlight current position
 */
function updateTimelinePosition() {
    if (!elements.timeline) return;

    // Get all existing dots
    const dots = elements.timeline.querySelectorAll('.timeline-dot');

    // Check if current index has a dot
    let currentDotExists = false;    // Update existing dots
    dots.forEach((dot) => {
        const dotIndex = parseInt(dot.getAttribute('data-index'));
        const isCurrent = dotIndex === state.currentIndex;

        if (isCurrent) {
            currentDotExists = true;
            dot.setAttribute('fill', '#dc3545');
            dot.setAttribute('r', 6);
            dot.setAttribute('stroke-width', 2);
            dot.classList.add('active');
        } else {
            dot.setAttribute('fill', '#0d6efd');
            dot.setAttribute('r', 3);
            dot.setAttribute('stroke-width', 1);
            dot.classList.remove('active');
        }
    });

    // If current frame doesn't have a dot, add one
    if (!currentDotExists && state.images.length > 0) {
        const svg = elements.timeline;
        const width = svg.clientWidth || 800;
        const height = 50;
        const margin = { left: 30, right: 30, top: 10, bottom: 20 };
        const chartWidth = width - margin.left - margin.right;
        const dotSpacing = chartWidth / (state.images.length - 1 || 1);

        const x = margin.left + (state.currentIndex * dotSpacing);
        const y = height / 2;

        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', x);
        dot.setAttribute('cy', y);
        dot.setAttribute('r', 6);
        dot.setAttribute('fill', '#dc3545');
        dot.setAttribute('stroke', '#fff');
        dot.setAttribute('stroke-width', 2);
        dot.setAttribute('class', 'timeline-dot active current-indicator');
        dot.setAttribute('data-index', state.currentIndex);
        dot.setAttribute('data-timestamp', state.images[state.currentIndex].timestamp);

        // Add click handler
        dot.addEventListener('click', () => {
            if (state.isPlaying) {
                stopAnimation();
            }
            loadImage(state.currentIndex);
        });

        // Add hover title
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = state.images[state.currentIndex].timestamp;
        dot.appendChild(title);

        svg.appendChild(dot);
    }
}/**
 * Handle keyboard shortcuts
 */
// eslint-disable-next-line complexity
function handleKeyboardInput(e) {
    // Ignore if focus is on an input or select
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

    if (state.images.length === 0) return;

    switch (e.key) {
        case 'ArrowLeft': {
            stopAnimation();
            let prevIndex = state.currentIndex - state.skipFrames;
            if (prevIndex < 0) {
                prevIndex = state.loop ? state.images.length - 1 : 0;
            }
            loadImage(prevIndex);
            break;
        }
        case 'ArrowRight': {
            stopAnimation();
            let nextIndex = state.currentIndex + state.skipFrames;
            if (nextIndex >= state.images.length) {
                nextIndex = state.loop ? 0 : state.images.length - 1;
            }
            loadImage(nextIndex);
            break;
        }
        case ' ': // Spacebar
            e.preventDefault(); // Prevent scrolling
            if (state.isPlaying) {
                stopAnimation();
            } else {
                playAnimation();
            }
            break;
        case 'Home':
            stopAnimation();
            loadImage(0);
            break;
        case 'End':
            stopAnimation();
            loadImage(state.images.length - 1);
            break;
        default:
            // No action for other keys
            break;
    }
}

/**
 * Play animation
 */
function playAnimation() {
    if (state.images.length === 0) return;

    state.isPlaying = true;
    elements.playBtn.disabled = true;
    elements.stopBtn.disabled = false;

    state.animationInterval = setInterval(() => {
        let nextIndex = state.currentIndex + state.skipFrames;

        if (nextIndex >= state.images.length) {
            if (state.loop) {
                nextIndex = 0;
            } else {
                stopAnimation();
                return;
            }
        }

        loadImage(nextIndex);
    }, state.speed);
}

/**
 * Stop animation and stay on current frame
 */
function stopAnimation() {
    state.isPlaying = false;
    clearInterval(state.animationInterval);

    elements.playBtn.disabled = false;
    elements.stopBtn.disabled = true;

    // Stay on current frame, don't reset to first frame
}

/**
 * Reset UI to initial state
 */
function resetUI() {
    hideFromRow("sectorTypeRow");
    elements.animationCard.style.display = "none";
    elements.imageWrapper.style.display = "none";
    elements.noImageMessage.style.display = "block";
    elements.loadingRow.style.display = "none";
    elements.imagesLoadedRow.style.display = "none";

    if (state.isPlaying) {
        stopAnimation();
    }
}

/**
 * Show a row and all subsequent rows
 */
function showRow(rowId) {
    document.getElementById(rowId).style.display = "block";
}

/**
 * Hide a row and all subsequent rows
 */
function hideFromRow(rowId) {
    const rows = ["sectorTypeRow", "sectorRow", "plotTypeRow", "loadingRow", "imagesLoadedRow"];
    const startIndex = rows.indexOf(rowId);

    if (startIndex !== -1) {
        for (let i = startIndex; i < rows.length; i++) {
            document.getElementById(rows[i]).style.display = "none";

            // Disable and reset corresponding select
            const selectId = rows[i].replace("Row", "Select");
            const select = document.getElementById(selectId);
            if (select) {
                select.disabled = true;
                select.innerHTML = '<option value="">Loading...</option>';
            }
        }
    }
}

/**
 * Show error message
 */
function showError(element, message) {
    if (element) {
        element.innerHTML = `<option value="">Error: ${message}</option>`;
    }
    // Could add a toast notification here
}

/**
 * Copy shareable link to clipboard
 */
async function copyShareLink(event) {
    event.preventDefault();
    const url = window.location.href;

    try {
        await navigator.clipboard.writeText(url);

        // Visual feedback
        const originalText = elements.shareBtn.innerHTML;
        elements.shareBtn.innerHTML = '<i class="bi bi-check"></i> Copied!';
        elements.shareBtn.classList.remove('btn-outline-success');
        elements.shareBtn.classList.add('btn-success');

        setTimeout(() => {
            elements.shareBtn.innerHTML = originalText;
            elements.shareBtn.classList.remove('btn-success');
            elements.shareBtn.classList.add('btn-outline-success');
        }, 2000);
    } catch {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = url;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();

        try {
            document.execCommand('copy');
            elements.shareBtn.innerHTML = '<i class="bi bi-check"></i> Copied!';
        } catch {
            elements.shareBtn.innerHTML = '<i class="bi bi-x"></i> Failed';
        }

        document.body.removeChild(textarea);

        setTimeout(() => {
            elements.shareBtn.innerHTML = '<i class="bi bi-share"></i> Share';
        }, 2000);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
