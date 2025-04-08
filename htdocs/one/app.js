// Remove the import statement and assume `createGeoJSONLayer` is globally available

document.addEventListener('DOMContentLoaded', () => {
    const map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            })
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([-98.5795, 39.8283]), // Center on the contiguous US
            zoom: 4 // Zoom level to cover the contiguous US
        })
    });

    let currentTime = new Date();

    function formatTimestamp(date) {
        const year = date.getUTCFullYear().toString();
        const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
        const day = date.getUTCDate().toString().padStart(2, '0');
        const hours = date.getUTCHours().toString().padStart(2, '0');
        const minutes = date.getUTCMinutes().toString().padStart(2, '0');
        return `${year}${month}${day}${hours}${minutes}`;
    }

    // Create a single TMS layer
    const tmsLayer = new ol.layer.Tile({
        source: new ol.source.XYZ({
            url: `https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/ridge::USCOMP-N0Q-${formatTimestamp(currentTime)}/{z}/{x}/{y}.png`,
            crossOrigin: 'anonymous'
        }),
        visible: true
    });
    map.addLayer(tmsLayer);

    function updateTMSLayer(radarTime = currentTime) {
        const timestamp = formatTimestamp(radarTime);
        tmsLayer.getSource().setUrl(`https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/ridge::USCOMP-N0Q-${timestamp}/{z}/{x}/{y}.png`);
    }

    function getQueryParams() {
        const params = new URLSearchParams(window.location.search);
        return {
            timestamp: params.get('timestamp'),
            center: params.get('center'),
            zoom: params.get('zoom'),
            realtime: params.get('realtime')
        };
    }

    function updateURL() {
        const center = map.getView().getCenter();
        const zoom = map.getView().getZoom();
        const queryParams = new URLSearchParams(window.location.search);

        if (!realTimeInterval) {
            queryParams.set('timestamp', formatTimestamp(currentTime));
        } else {
            queryParams.delete('timestamp');
        }

        queryParams.set('center', center ? ol.proj.toLonLat(center).map(coord => coord.toFixed(2)).join(',') : '');
        queryParams.set('zoom', zoom ? zoom.toFixed(2) : '');
        history.replaceState(null, '', `?${queryParams.toString()}`);
    }

    // Time control logic
    const timeStepBackwardButton = document.getElementById('time-step-backward');
    const timePlayPauseButton = document.getElementById('time-play-pause');
    const timeStepForwardButton = document.getElementById('time-step-forward');
    const realtimeModeButton = document.getElementById('realtime-mode');

    // Initialize the GeoJSON layer after declaring it
    const warningsTable = document.getElementById('warnings-table');
    const geojsonLayer = createGeoJSONLayer(map, warningsTable, currentTime);

    let animationInterval = null;

    function rectifyToFiveMinutes(date) {
        const minutes = date.getMinutes();
        const rectifiedMinutes = Math.floor(minutes / 5) * 5;
        date.setMinutes(rectifiedMinutes, 0, 0);
        return date;
    }

    function stepTime(minutes) {
        const now = new Date();
        currentTime.setMinutes(currentTime.getMinutes() + minutes);

        // Ensure radar layer uses rectified time
        const radarTime = new Date(currentTime);
        radarTime.setMinutes(Math.floor(radarTime.getMinutes() / 5) * 5, 0, 0);

        // Prevent selecting a timestamp from the future
        if (currentTime > now) {
            currentTime = new Date(now);
        }

        updateTimeInput(); // Update the timestamp in the input field
        updateTMSLayer(radarTime); // Update radar layer with rectified time
        updateGeoJSONLayer(); // Update warnings layer with 1-minute granularity
    }

    // Animation logic to toggle visibility
    function toggleAnimation() {
        let progressBar = document.querySelector('#animation-progress .progress');

        // Ensure the progress bar element exists
        if (!progressBar) {
            const progressContainer = document.getElementById('animation-progress');
            progressBar = document.createElement('div');
            progressBar.className = 'progress';
            progressContainer.appendChild(progressBar);
        }

        if (animationInterval) {
            clearInterval(animationInterval);
            animationInterval = null;
            timePlayPauseButton.textContent = '⏯';
            updateURL(); // Update the URL to reflect the final state after stopping the animation
            progressBar.style.width = '0%'; // Reset progress bar
        } else {
            const startTime = new Date();
            startTime.setMinutes(startTime.getMinutes() - 55); // Start 55 minutes ago
            currentTime = rectifyToFiveMinutes(startTime);
            updateTimeInput(); // Update the timestamp in the input field
            updateTMSLayer();

            let steps = 0;
            const totalSteps = 12; // 12 timesteps of 5 minutes each

            animationInterval = setInterval(() => {
                const now = rectifyToFiveMinutes(new Date()); // Current time rectified to 5-minute intervals
                if (steps >= totalSteps || currentTime >= now) {
                    steps = 0; // Reset steps
                    currentTime = rectifyToFiveMinutes(new Date(now.getTime() - 55 * 60 * 1000)); // Reset to 55 minutes ago
                } else {
                    currentTime.setMinutes(currentTime.getMinutes() + 5); // Advance by 5 minutes
                    currentTime = rectifyToFiveMinutes(currentTime);

                    // Prevent advancing into the future
                    if (currentTime > now) {
                        currentTime = now;
                    }

                    steps++;
                }

                updateTMSLayer(); // Update the TMS layer source with the new timestamp
                updateTimeInput(); // Update the timestamp in the input field

                // Update progress bar
                const progressPercentage = (steps / totalSteps) * 100;
                progressBar.style.width = `${progressPercentage}%`;
            }, 1000); // 1s per frame

            timePlayPauseButton.textContent = '⏸';
        }
    }

    let realTimeInterval = null;

    function updateBrandingOverlay(mode) {
        const brandingOverlay = document.getElementById('branding-overlay');
        if (brandingOverlay) {
            brandingOverlay.dataset.mode = mode;
            brandingOverlay.textContent = `IEM1: ${mode === 'realtime' ? 'Realtime' : 'Archive'}`;
        }
    }

    function toggleRealTimeMode() {
        const queryParams = new URLSearchParams(window.location.search);
        const timeInput = document.getElementById('current-time');
        const timeStepBackwardButton = document.getElementById('time-step-backward');
        const timeStepForwardButton = document.getElementById('time-step-forward');

        if (realTimeInterval) {
            clearInterval(realTimeInterval);
            realTimeInterval = null;
            realtimeModeButton.textContent = '⏱';
            realtimeModeButton.title = 'Enable Real-Time Mode';
            queryParams.delete('realtime');
            history.replaceState(null, '', `?${queryParams.toString()}`);
            updateBrandingOverlay('archive'); // Switch to archive mode

            // Enable time input and buttons
            timeInput.disabled = false;
            timeStepBackwardButton.disabled = false;
            timeStepBackwardButton.title = ''; // Clear tooltip
            timeStepForwardButton.disabled = false;
            timeStepForwardButton.title = ''; // Clear tooltip
        } else {
            // Advance currentTime to the most current possible timestamp
            const now = new Date();
            currentTime = new Date(now);
            updateTimeInput(); // Update the timestamp in the input field
            updateTMSLayer(new Date(Math.floor(now.getTime() / (5 * 60 * 1000)) * (5 * 60 * 1000))); // Rectified time for radar
            updateGeoJSONLayer(); // Update warnings layer

            realTimeInterval = setInterval(() => {
                const lnow = new Date();
                currentTime = new Date(lnow);
                updateTimeInput(); // Update the timestamp in the input field
                updateTMSLayer(new Date(Math.floor(lnow.getTime() / (5 * 60 * 1000)) * (5 * 60 * 1000))); // Rectified time for radar
                updateGeoJSONLayer(); // Update warnings layer
            }, 60000); // Update every minute
            realtimeModeButton.textContent = '🔴';
            realtimeModeButton.title = 'Disable Real-Time Mode';
            queryParams.set('realtime', '1');
            history.replaceState(null, '', `?${queryParams.toString()}`);
            updateBrandingOverlay('realtime'); // Switch to real-time mode

            // Disable time input and buttons
            timeInput.disabled = true;
            timeStepBackwardButton.disabled = true;
            timeStepBackwardButton.title = 'Disabled in Real-Time Mode'; // Add tooltip
            timeStepForwardButton.disabled = true;
            timeStepForwardButton.title = 'Disabled in Real-Time Mode'; // Add tooltip
        }
    }

    // Initialize app state from URL
    const queryParams = getQueryParams();
    if (queryParams.realtime === '1') {
        toggleRealTimeMode();
        updateBrandingOverlay('realtime');
    } else if (queryParams.timestamp) {
        const year = parseInt(queryParams.timestamp.slice(0, 4), 10);
        const month = parseInt(queryParams.timestamp.slice(4, 6), 10) - 1;
        const day = parseInt(queryParams.timestamp.slice(6, 8), 10);
        const hours = parseInt(queryParams.timestamp.slice(8, 10), 10);
        const minutes = parseInt(queryParams.timestamp.slice(10, 12), 10);
        currentTime = new Date(Date.UTC(year, month, day, hours, minutes));
        updateBrandingOverlay('archive');
    } else {
        // Default to real-time mode if no timestamp is provided
        toggleRealTimeMode();
        updateBrandingOverlay('realtime');
    }

    if (queryParams.center) {
        const [lon, lat] = queryParams.center.split(',').map(Number);
        map.getView().setCenter(ol.proj.fromLonLat([lon, lat]));
    }
    if (queryParams.zoom) {
        map.getView().setZoom(Number(queryParams.zoom));
    }

    // Event listeners for buttons
    timeStepBackwardButton.addEventListener('click', () => {
        stepTime(-5); // Step time backward by 5 minutes
        updateTimeInput(); // Update the timestamp in the input field
        updateTMSLayer(); // Uses default currentTime
        updateURL();  // Update the URL to reflect the new state
    });
    timePlayPauseButton.addEventListener('click', toggleAnimation);
    timeStepForwardButton.addEventListener('click', () => {
        stepTime(5);
        updateTimeInput(); // Update the timestamp in the input field
        updateTMSLayer(); // Uses default currentTime
        updateURL();
    }); // 5 minutes forward

    // Update URL whenever the app state changes
    map.getView().on('change:center', updateURL);
    map.getView().on('change:zoom', updateURL);

    // Initialize time display
    currentTime = rectifyToFiveMinutes(currentTime);
    updateTimeInput();

    // Layers drawer functionality
    const layersToggle = document.getElementById('layers-toggle');
    const layerControl = document.getElementById('layer-control');

    if (layersToggle && layerControl) {
        layersToggle.addEventListener('click', () => {
            layerControl.classList.toggle('open'); // Toggle the `open` class
        });
    } else {
        console.error('Layers toggle or layer control element not found.');
    }

    // Layer toggle functionality
    const tmsLayerToggle = document.getElementById('toggle-tms-layer');
    const tmsOpacitySlider = document.getElementById('tms-opacity-slider');

    if (tmsLayerToggle) {
        tmsLayerToggle.addEventListener('change', (event) => {
            if (event.target.checked) {
                // Enable the TMS layer
                tmsLayer.setVisible(true);
            } else {
                // Disable the TMS layer
                tmsLayer.setVisible(false);
            }
        });

        // Initialize the TMS layer visibility
        tmsLayer.setVisible(tmsLayerToggle.checked);
    }

    if (tmsOpacitySlider) {
        tmsOpacitySlider.addEventListener('input', (event) => {
            tmsLayer.setOpacity(parseFloat(event.target.value));
        });

        // Initialize the TMS layer opacity
        tmsLayer.setOpacity(parseFloat(tmsOpacitySlider.value));
    }

    function updateTimeInput() {
        const timeInput = document.getElementById('current-time');
        if (timeInput) {
            // Format the current time in the browser's local timezone
            const year = currentTime.getFullYear();
            const month = (currentTime.getMonth() + 1).toString().padStart(2, '0');
            const day = currentTime.getDate().toString().padStart(2, '0');
            const hours = currentTime.getHours().toString().padStart(2, '0');
            const minutes = currentTime.getMinutes().toString().padStart(2, '0');
            timeInput.value = `${year}-${month}-${day}T${hours}:${minutes}`; // Format as "YYYY-MM-DDTHH:mm"
        }
    }

    function handleTimeInputChange(event) {
        const newTime = new Date(event.target.value);
        if (!isNaN(newTime)) {
            currentTime = newTime;
            updateTimeInput(); // Update the timestamp in the input field
            updateTMSLayer();
            updateURL();
        }
    }

    // Event listener for the time input field
    const timeInput = document.getElementById('current-time');
    if (timeInput) {
        timeInput.addEventListener('change', handleTimeInputChange);
    }

    // Initialize the time input field
    updateTimeInput();



    // Function to update the GeoJSON layer
    function updateGeoJSONLayer() {
        if (geojsonLayer) {
            geojsonLayer.getSource().setUrl(`/geojson/sbw.py?ts=${currentTime.toISOString()}`);
            geojsonLayer.getSource().refresh();
        }
    }

    // Update GeoJSON layer when time changes
    timeStepBackwardButton.addEventListener('click', () => {
        stepTime(-5);
        updateTimeInput();
        updateGeoJSONLayer();
        updateURL();
    });

    timeStepForwardButton.addEventListener('click', () => {
        stepTime(5);
        updateTimeInput();
        updateGeoJSONLayer();
        updateURL();
    });

    realtimeModeButton.addEventListener('click', () => {
        toggleRealTimeMode();
        updateGeoJSONLayer(); // Ensure GeoJSON layer is updated when toggling real-time mode
        updateTMSLayer(); // Uses default currentTime
    });

    // Warnings modal functionality
    const warningsToggle = document.getElementById('warnings-toggle');
    const warningsModal = document.getElementById('warnings-modal');
    const warningsModalContent = document.getElementById('warnings-modal-content');
    const closeWarningsButton = document.getElementById('close-warnings');
    const collapseWarningsButton = document.getElementById('collapse-warnings');

    if (warningsToggle && warningsModal) {
        // Toggle warnings modal visibility
        warningsToggle.addEventListener('click', () => {
            warningsModal.classList.toggle('open');
        });

        // Collapse button functionality
        if (collapseWarningsButton) {
            collapseWarningsButton.style.display = window.innerWidth <= 768 ? 'block' : 'none';
            collapseWarningsButton.addEventListener('click', () => {
                warningsModal.classList.remove('open');
            });
        }

        // Close button functionality
        if (closeWarningsButton) {
            closeWarningsButton.addEventListener('click', () => {
                warningsModal.classList.remove('open');
            });
        }

        // Populate table with example data (replace with dynamic data as needed)
        if (warningsTable) {
            const exampleData = [
                { phenomena: 'Tornado', significance: 'Severe', eventId: '12345' },
                { phenomena: 'Flood', significance: 'Moderate', eventId: '67890' }
            ];

            exampleData.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.phenomena}</td>
                    <td>${row.significance}</td>
                    <td>${row.eventId}</td>
                `;
                warningsTable.querySelector('tbody').appendChild(tr);
            });
        }
    } else {
        console.error('Warnings toggle or warnings modal element not found.');
    }

    // Make modal draggable
    let isDragging = false;
    let offsetX, offsetY;

    warningsModalContent.addEventListener('mousedown', (e) => {
        isDragging = true;
        offsetX = e.clientX - warningsModal.offsetLeft;
        offsetY = e.clientY - warningsModal.offsetTop;
        warningsModal.style.transition = 'none'; // Disable transition during drag
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            warningsModal.style.left = `${e.clientX - offsetX}px`;
            warningsModal.style.top = `${e.clientY - offsetY}px`;
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        warningsModal.style.transition = ''; // Re-enable transition
    });

    // Add search functionality for warnings table
    const searchInput = document.getElementById('warnings-search');
    searchInput.addEventListener('input', (event) => {
        const filter = event.target.value.toLowerCase();
        const rows = document.querySelectorAll('#warnings-table tbody tr');
        rows.forEach((row) => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
});