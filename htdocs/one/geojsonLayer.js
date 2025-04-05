function createGeoJSONLayer(map, tableElement, currentTime) {
    const colorLookup = {
        "TO": 'red',
        "MA": 'purple',
        "EW": 'green',
        "FF": 'blue',
        "SV": 'yellow',
        "SQ": "#C71585",
        "DS": "#FFE4C4",
        "FL": "#00CED1" // Add color for Flood
    };

    const activePhenomena = new Set(["TO", "SV", "FF", "EW", "SQ", "DS"]); // Default active phenomena (FL excluded)

    const geojsonSource = new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        url: () => `/geojson/sbw.py?valid=${currentTime.toISOString()}`, // Fetch warnings
    });

    const geojsonLayer = new ol.layer.Vector({
        source: geojsonSource,
        style: (feature) => {
            const phenomena = feature.get('phenomena');

            // Exclude features not in the active phenomena set
            if (!activePhenomena.has(phenomena)) {
                return null;
            }

            const color = colorLookup[phenomena] || 'gray';
            return new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: color,
                    width: 3
                })
            });
        }
    });

    map.addLayer(geojsonLayer);

    // Add a popup overlay for feature clicks
    const popupElement = document.createElement('div');
    popupElement.id = 'popup';
    popupElement.style.position = 'absolute';
    popupElement.style.background = 'white';
    popupElement.style.border = '1px solid black';
    popupElement.style.padding = '10px';
    popupElement.style.display = 'none';
    popupElement.style.zIndex = '1000';
    popupElement.style.width = '300px'; // Increased width for better content fit
    popupElement.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)'; // Added shadow for better visibility
    document.body.appendChild(popupElement);

    const popupOverlay = new ol.Overlay({
        element: popupElement,
        positioning: 'bottom-center',
        stopEvent: true
    });
    map.addOverlay(popupOverlay);

    // Helper function to format timestamps
    function formatTimestamp(date) {
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
            timeZoneName: 'short'
        };
        return date.toLocaleString(undefined, options);
    }

    // Handle map clicks to show popup
    map.on('singleclick', (event) => {
        const features = map.getFeaturesAtPixel(event.pixel);
        if (features && features.length > 0) {
            const feature = features[0];
            const issueUTC = new Date(feature.get('issue'));
            const expireUTC = new Date(feature.get('expire_utc'));

            // Format timestamps
            const issueLocal = formatTimestamp(issueUTC);
            const expireLocal = formatTimestamp(expireUTC);

            // Placeholder content for the popup
            popupElement.innerHTML = `
                <strong>WFO:</strong> ${feature.get('wfo')}<br>
                <strong>Event:</strong> ${feature.get('ps')} ${feature.get('eventid')}<br>
                <strong>Issue:</strong> ${issueLocal} (${issueUTC.toISOString().slice(11, 16)} UTC)<br>
                <strong>Expires:</strong> ${expireLocal} (${expireUTC.toISOString().slice(11, 16)} UTC)<br>
                <a href="${feature.get('href')}" target="_new">VTEC App Link</a>
            `;
            popupElement.style.display = 'block';
            popupOverlay.setPosition(event.coordinate);
        } else {
            popupElement.style.display = 'none'; // Hide popup if no feature is clicked
        }
    });

    // Update the HTML table with GeoJSON features and count phenomena
    function updateTableAndCounts(features) {
        const tbody = tableElement.querySelector('tbody');
        tbody.innerHTML = ''; // Clear existing rows

        const phenomenaCounts = {}; // Track counts for each phenomena

        features.forEach((feature) => {
            const phenomena = feature.get('phenomena');

            // Increment the count for this phenomena
            phenomenaCounts[phenomena] = (phenomenaCounts[phenomena] || 0) + 1;

            // Skip adding rows for features not in the active phenomena set
            if (!activePhenomena.has(phenomena)) {
                return;
            }

            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.textContent = feature.get('wfo');
            row.appendChild(cell);
            const cell3 = document.createElement('td');
            const expireUTC = new Date(feature.get('expire_utc'));
            const expireLocal = formatTimestamp(expireUTC);
            cell3.textContent = `${expireLocal} (${expireUTC.toISOString().slice(11, 16)} UTC)`;
            row.appendChild(cell3);
            const cell4 = document.createElement('td');
            cell4.innerHTML = `<a href="${feature.get('href')}" target="_new">${feature.get('ps')} ${feature.get('eventid')}</a>`;
            row.appendChild(cell4);
            tbody.appendChild(row);
        });

        // Update the toggle labels with counts
        const phenomenaToggles = document.querySelectorAll('.phenomena-toggle');
        phenomenaToggles.forEach((toggle) => {
            const phenomena = toggle.dataset.phenomena;
            const count = phenomenaCounts[phenomena] || 0;
            toggle.textContent = `${phenomena} (${count})`;
        });
    }

    // Listen for source updates and refresh the table and counts
    geojsonSource.on('change', () => {
        if (geojsonSource.getState() === 'ready') {
            const features = geojsonSource.getFeatures();
            updateTableAndCounts(features);
        }
    });

    // Handle toggling of the warnings layer
    const warningsLayerToggle = document.getElementById('toggle-warnings-layer');
    if (warningsLayerToggle) {
        warningsLayerToggle.addEventListener('change', (event) => {
            geojsonLayer.setVisible(event.target.checked);
        });
    }

    // Handle toggling of individual phenomena
    const phenomenaToggles = document.querySelectorAll('.phenomena-toggle');
    phenomenaToggles.forEach((toggle) => {
        const phenomena = toggle.dataset.phenomena;

        // Initialize the FL toggle as untoggled
        if (phenomena === "FL") {
            toggle.classList.remove('active');
        }

        toggle.addEventListener('click', (event) => {
            if (activePhenomena.has(phenomena)) {
                activePhenomena.delete(phenomena);
                event.target.classList.remove('active'); // Visually indicate toggle is off
                event.target.style.background = '#ccc'; // Gray background for untoggled
            } else {
                activePhenomena.add(phenomena);
                event.target.classList.add('active'); // Visually indicate toggle is on
                event.target.style.background = ''; // Reset background for toggled
            }
            geojsonLayer.changed(); // Trigger a re-render of the layer
        });
    });

    return geojsonLayer;
}
