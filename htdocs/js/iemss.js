/* global ol, bootstrap */
const htmlInterface = ['<div class="card iemss-container">',
    '<div class="card-header">',
    '<a class="btn btn-secondary float-end" href="/" id="iemss-metadata-link" target="_new">',
    '<i class="fa fa-info"></i> Station Metadata</a>',
    '<h3 class="card-title"><span id="iemss-network"></span> Station Selector</h3> ',
    '<br class="clearfix" />',
    '</div>',
    '<div class="card-body">',
    '<div class="row">',
    '<div class="col-sm-6">',

    '<div class="d-flex gap-2 mb-2">',
    '<div class="btn-group">',
    '<button class="btn btn-secondary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">',
    'Sort Available Stations: <span class="caret"></span>',
    '</button>',
    '<ul class="dropdown-menu" role="menu">',
    '<li id="iemss-sortbyid"><a class="dropdown-item" href="#">Sort by Identifier</a></li>',
    '<li id="iemss-sortbyname"><a class="dropdown-item" href="#">Sort by Name</a></li>',
    '</ul>',
    '</div>',
    '<input type="text" class="form-control flex-fill" id="stationfilter" ',
    'placeholder="Filter stations...">',
    '</div>',

    '<select multiple id="stations_in" class="form-control">',
    '</select>',
    '<div class="iemss-station-count text-muted small" id="available-count">Available: 0 stations</div>',
    '<div class="mb-3 iemss-button-group">',
    '<button type="button" id="stations_add" class="btn btn-secondary"><i class="fa fa-plus"></i> Add Selected</button>',
    '<button type="button" id="stations_addall" class="btn btn-secondary">Add All</button>',
    '</div>',
    '</div>',
    '<div class="col-sm-6">',
    '<div class="d-flex align-items-center mb-2" style="height: 38px;">',
    '<label for="stations_out" class="mb-0">Selected Stations:</label>',
    '</div>',
    '<input type="checkbox" name="stations" value="_ALL" class="iemss-hidden">',
    '<select multiple id="stations_out" class="form-control" name="stations">',
    '</select>',
    '<div class="iemss-station-count text-muted small" id="selected-count">Selected: 0 stations</div>',
    '<div class="mb-3 iemss-button-group">',
    '<button type="button" id="stations_del" class="btn btn-secondary"><i class="fa fa-minus"></i> Remove Selected</button>',
    '<button type="button" id="stations_delall" class="btn btn-secondary">Remove All</button>',
    '</div>',
    '</div>',
    '</div>',
    '<br />',
    '<div class="row"><div class="col-sm-12">',
    '<div id="map"></div>',
    '<div class="iemss-map-legend">',
    '<div class="iemss-legend-item">',
    '<span class="iemss-legend-dot online"></span>',
    '<span>Online stations with current data</span>',
    '</div>',
    '<div class="iemss-legend-item">',
    '<span class="iemss-legend-dot offline"></span>',
    '<span>Offline stations or no recent data</span>',
    '</div>',
    '</div>',
    '</div></div>',
    '</div><!-- End of card-body -->',
    '</div><!-- End of card -->'];

const iemssApp = {
    map: null,
    geojson: null,
    geojsonSource: null,
    network: null
};

// Vanilla JS replacement for jQuery filterByText functionality
function setupFilterByText(selectElement, textboxElement, selectSingleMatch = false) {
    const options = Array.from(selectElement.options).map(option => ({
        value: option.value,
        text: option.textContent
    }));
    
    // Store original options on the element
    selectElement.dataset.originalOptions = JSON.stringify(options);
    
    const handleFilter = () => {
        const search = textboxElement.value.trim();
        const regex = new RegExp(search, 'gi');
        
        // Clear current options
        selectElement.innerHTML = '';
        
        // Filter and add matching options
        options.forEach(optionData => {
            if (optionData.text.match(regex) !== null) {
                const option = document.createElement('option');
                option.value = optionData.value;
                option.textContent = optionData.text;
                selectElement.appendChild(option);
            }
        });
        
        // Auto-select if single match
        if (selectSingleMatch && selectElement.options.length === 1) {
            selectElement.options[0].selected = true;
        }
        
        // Update counts after filtering
        updateStationCounts();
    };
    
    textboxElement.addEventListener('input', handleFilter);
    textboxElement.addEventListener('change', handleFilter);
}

function sortListing(option) {
    const stationsIn = document.getElementById('stations_in');
    const options = Array.from(stationsIn.options);
    
    options.sort((a, b) => {
        let at = a.textContent;
        let bt = b.textContent;
        if (option === 'name') {
            at = at.slice(at.indexOf(' ') + 1);
            bt = bt.slice(bt.indexOf(' ') + 1);
        }
        return (at > bt) ? 1 : ((at < bt) ? -1 : 0);
    });
    
    // Clear and re-add sorted options
    stationsIn.innerHTML = '';
    options.forEach(opt => stationsIn.appendChild(opt));
    
    // Update counts after sorting
    updateStationCounts();
}

// Helper functions to replace jQuery functionality
function moveSelectedOptions(fromSelect, toSelect) {
    const selected = Array.from(fromSelect.selectedOptions);
    selected.forEach(option => {
        option.selected = false;
        toSelect.appendChild(option);
    });
    
    // If moving to stations_out (right side), select all options there
    if (toSelect.id === 'stations_out') {
        selectAllOptions(toSelect);
    }
    
    updateStationCounts();
    return false;
}

function moveAllOptions(fromSelect, toSelect) {
    const options = Array.from(fromSelect.options);
    options.forEach(option => {
        toSelect.appendChild(option);
    });
    
    // If moving to stations_out (right side), select all options there
    if (toSelect.id === 'stations_out') {
        selectAllOptions(toSelect);
    }
    
    updateStationCounts();
    return false;
}

function selectAllOptions(selectElement) {
    Array.from(selectElement.options).forEach(option => {
        option.selected = true;
    });
}

// Update station count displays
function updateStationCounts() {
    const stationsIn = document.getElementById('stations_in');
    const stationsOut = document.getElementById('stations_out');
    const availableCount = document.getElementById('available-count');
    const selectedCount = document.getElementById('selected-count');
    
    if (availableCount && stationsIn) {
        const count = stationsIn.options.length;
        availableCount.textContent = `Available: ${count.toLocaleString()} station${count !== 1 ? 's' : ''}`;
    }
    
    if (selectedCount && stationsOut) {
        const count = stationsOut.options.length;
        selectedCount.textContent = `Selected: ${count.toLocaleString()} station${count !== 1 ? 's' : ''}`;
    }
}

function setupIemssDom(iemssElement, networkParam, select_name) {
    if (select_name) {
        document.getElementById('stations_out').setAttribute('name', select_name);
    }
    document.getElementById('iemss-network').textContent = networkParam;
    document.getElementById('iemss-metadata-link').setAttribute('href', `/sites/networks.php?network=${networkParam}`);
    if (iemssElement.getAttribute('data-supports-all') === '0') {
        const addAllBtn = document.getElementById('stations_addall');
        if (addAllBtn) addAllBtn.style.display = 'none';
    }
}

function setupIemssFormSubmission(iemssElement) {
    const form = document.querySelector("form[name='iemss']");
    const submitButtons = form ? Array.from(form.elements).filter(
    el => (el.tagName === "BUTTON" || el.tagName === "INPUT") &&
            (el.type === "submit" || el.type === "image")
    ) : [];
    submitButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const stationsOut = document.getElementById('stations_out');
            const stationsCheckbox = document.querySelector("input[type='checkbox'][name='stations']");
            if (iemssElement.getAttribute('data-supports-all') !== '0') {
                if (stationsOut && iemssApp.geojsonSource && stationsOut.options.length >= iemssApp.geojsonSource.getFeatures().length) {
                    Array.from(stationsOut.options).forEach(opt => { opt.selected = false; });
                    if (stationsCheckbox) stationsCheckbox.checked = true;
                    return true;
                } else {
                    if (stationsCheckbox) stationsCheckbox.checked = false;
                }
            }
            if (stationsOut) {
                selectAllOptions(stationsOut);
                if (stationsOut.options.length === 0) {
                    alert("No stations listed in 'Selected Stations'!");
                    event.preventDefault();
                    return false;
                }
            }
            return true;
        });
    });
}

function setupStationMovementHandlers() {
    const stationsIn = document.getElementById('stations_in');
    const stationsOut = document.getElementById('stations_out');
    if (stationsIn && stationsOut) {
        stationsIn.addEventListener('dblclick', () => moveSelectedOptions(stationsIn, stationsOut));
        stationsOut.addEventListener('dblclick', () => moveSelectedOptions(stationsOut, stationsIn));
    }
    const addBtn = document.getElementById('stations_add');
    if (addBtn) addBtn.addEventListener('click', () => moveSelectedOptions(stationsIn, stationsOut));
    const addAllBtn = document.getElementById('stations_addall');
    if (addAllBtn) addAllBtn.addEventListener('click', () => {
        moveAllOptions(stationsIn, stationsOut);
        return false;
    });
    const delAllBtn = document.getElementById('stations_delall');
    if (delAllBtn) delAllBtn.addEventListener('click', () => moveAllOptions(stationsOut, stationsIn));
    const delBtn = document.getElementById('stations_del');
    if (delBtn) delBtn.addEventListener('click', () => {
        moveSelectedOptions(stationsOut, stationsIn);
        return false;
    });
}

function setupSortAndFilterHandlers() {
    const sortById = document.getElementById('iemss-sortbyid');
    if (sortById) sortById.addEventListener('click', (event) => { event.preventDefault(); sortListing("id"); });
    const sortByName = document.getElementById('iemss-sortbyname');
    if (sortByName) sortByName.addEventListener('click', (event) => { event.preventDefault(); sortListing("name"); });
}

function setupIemssMapAndData(iemssElement, networkParam) {
    const onlyOnline = (iemssElement.getAttribute('data-only-online') === '1');
    iemssApp.geojsonSource = new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        projection: ol.proj.get('EPSG:3857'),
        url: `/geojson/network/${networkParam}.geojson?only_online=${onlyOnline ? "1" : "0"}`
    });
    iemssApp.map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({ source: new ol.source.OSM() })],
        view: new ol.View({
            projection: ol.proj.get('EPSG:3857'),
            center: [-10575351, 5160979],
            zoom: 3
        })
    });
    iemssApp.geojson = new ol.layer.Vector({
        source: iemssApp.geojsonSource,
        style(feature) {
            const online = feature.get('online');
            const isOnline = online === true || online === 1 || online === '1';
            return new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 7,
                    fill: new ol.style.Fill({ color: isOnline ? 'rgba(0, 128, 0, 1)' : 'rgba(255, 0, 0, 1)' })
                })
            });
        },
        renderBuffer: 200,
        updateWhileAnimating: false,
        updateWhileInteracting: false
    });
    iemssApp.map.addLayer(iemssApp.geojson);
}

function setupIemssMapPopups(mapInstance, geojsonInstance, geojsonSourceInstance, networkParam) {
    geojsonSourceInstance.on('change', () => {
        if (geojsonSourceInstance.getState() === 'ready') {
            const stationsInSelect = document.getElementById('stations_in');
            const iemssContainer = document.querySelector('.iemss-container');
            if (iemssContainer) iemssContainer.classList.remove('iemss-loading');
            geojsonSourceInstance.getFeatures().forEach(feat => {
                let lbl = `[${feat.get('sid')}] ${feat.get('sname')}`;
                if (networkParam !== 'TAF') lbl += ` ${feat.get('time_domain')}`;
                const option = document.createElement('option');
                option.value = feat.get('sid');
                option.textContent = lbl;
                stationsInSelect.appendChild(option);
            });
            sortListing("id");
            setupFilterByText(stationsInSelect, document.getElementById('stationfilter'), true);
            updateStationCounts();
            mapInstance.getView().fit(
                geojsonSourceInstance.getExtent(),
                { size: mapInstance.getSize(), padding: [50, 50, 50, 50] }
            );
        } else if (geojsonSourceInstance.getState() === 'loading') {
            const iemssContainer = document.querySelector('.iemss-container');
            if (iemssContainer) iemssContainer.classList.add('iemss-loading');
        }
    });
    // Create popup elements
    const mapElement = document.getElementById('map');
    const popupDiv = document.createElement('div');
    popupDiv.id = 'popup';
    mapElement.appendChild(popupDiv);
    const popoverContentDiv = document.createElement('div');
    popoverContentDiv.id = 'popover-content';
    mapElement.appendChild(popoverContentDiv);
    const element = document.getElementById('popup');
    const popup = new ol.Overlay({ element, positioning: 'bottom-center', stopEvent: false });
    mapInstance.addOverlay(popup);
    let popoverInstance = null;
    if (typeof bootstrap !== 'undefined' && bootstrap?.Popover) {
        popoverInstance = new bootstrap.Popover(element, {
            placement: 'top', html: true,
            content: () => document.getElementById('popover-content').innerHTML
        });
    }
    mapInstance.on('click', (evt) => {
        const feature = mapInstance.forEachFeatureAtPixel(evt.pixel, feat => feat);
        if (feature) {
            const geometry = feature.getGeometry();
            const coord = geometry.getCoordinates();
            const sid = feature.get('sid');
            popup.setPosition(coord);
            const content = `<p><strong>SID: </strong>${sid}`
                + `<br /><strong>Name:</strong> ${feature.get('sname')}`
                + `<br /><strong>Period:</strong> ${feature.get("time_domain")}</p>`;
            document.getElementById('popover-content').innerHTML = content;
            if (popoverInstance) popoverInstance.show();
            const stationsInSelect = document.getElementById('stations_in');
            const stationOption = Array.from(stationsInSelect.options).find(option => option.value === sid);
            if (stationOption) {
                Array.from(stationsInSelect.options).forEach(opt => { opt.selected = false; });
                stationOption.selected = true;
                stationOption.scrollIntoView({ block: 'nearest' });
            } else {
                const filterInput = document.getElementById('stationfilter');
                const originalFilter = filterInput.value;
                filterInput.value = '';
                filterInput.dispatchEvent(new Event('input'));
                const foundOption = Array.from(stationsInSelect.options).find(option => option.value === sid);
                if (foundOption) {
                    Array.from(stationsInSelect.options).forEach(opt => { opt.selected = false; });
                    foundOption.selected = true;
                    foundOption.scrollIntoView({ block: 'nearest' });
                }
                setTimeout(() => {
                    filterInput.value = originalFilter;
                    filterInput.dispatchEvent(new Event('input'));
                }, 100);
            }
        } else {
            if (popoverInstance) popoverInstance.hide();
        }
    });
}

// Main orchestration function (refactored)
document.addEventListener('DOMContentLoaded', () => {
    const iemssElement = document.getElementById('iemss');
    if (!iemssElement) return;
    iemssElement.innerHTML = htmlInterface.join('');
    iemssApp.network = iemssElement.getAttribute('data-network');
    const select_name = iemssElement.getAttribute('data-name');
    if (!iemssApp.network) return;
    setupIemssDom(iemssElement, iemssApp.network, select_name);
    setupIemssFormSubmission(iemssElement);
    setupStationMovementHandlers();
    setupSortAndFilterHandlers();
    setupIemssMapAndData(iemssElement, iemssApp.network);
    setupIemssMapPopups(iemssApp.map, iemssApp.geojson, iemssApp.geojsonSource, iemssApp.network);
});