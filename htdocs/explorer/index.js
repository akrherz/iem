/* global windowFactory, Highcharts, ol, bootstrap */
let epoch = 0;
let olMap = null;
let overviewMap = null;
let popup = null;
let stationLayer = null;
let dockPosition = 0;

const airportStyle = new ol.style.Style({
    zIndex: 99,
    image: new ol.style.Icon({
        src: "img/airport.svg",
        scale: [0.2, 0.2]
    })
});
airportStyle.enabled = true;
const isusmStyle = new ol.style.Style({
    zIndex: 99,
    image: new ol.style.Icon({
        src: "img/isu.svg",
        scale: [0.2, 0.2]
    })
});
isusmStyle.enabled = true;
const climateStyle = new ol.style.Style({
    zIndex: 100,
    image: new ol.style.Circle({
        fill: new ol.style.Fill({color: '#00ff00'}),
        stroke: new ol.style.Stroke({
            color: '#008800',
            width: 2.25
        }),
        radius: 7
    })
});
climateStyle.enabled = true;
const climodistrictStyle = new ol.style.Style({
    zIndex: 101,
    text: new ol.style.Text({
        text: '',
        font: 'bold 14pt serif',
        fill: new ol.style.Fill({
          color: [255, 255, 255, 1],
        }),
        backgroundFill: new ol.style.Fill({
          color: [0, 0, 255, 1],
        }),
        padding: [2, 2, 2, 2],
    })
});
climodistrictStyle.enabled = true;
const stateStyle = new ol.style.Style({
    zIndex: 102,
    text: new ol.style.Text({
        text: '',
        font: 'bold 14pt serif',
        fill: new ol.style.Fill({
          color: [255, 255, 255, 1],
        }),
        backgroundFill: new ol.style.Fill({
          color: [255, 0, 0, 1],
        }),
        padding: [2, 2, 2, 2],
    })
});
stateStyle.enabled = true;

function make_iem_tms(title, layername, visible, type) {
    return new ol.layer.Tile({
        title,
        visible,
        type,
        source: new ol.source.XYZ({
            url: `/c/tile.py/1.0.0/${layername}/{z}/{x}/{y}.png`
        })
    })
}

/**
 * Replace HTML special characters with their entity equivalents
 * @param string val 
 * @returns string converted string
 */
function escapeHTML(val) {
    return val.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}

function mapClickHandler(event){
    const feature = olMap.forEachFeatureAtPixel(event.pixel,
        (feature2) => {
            return feature2;
        });
    if (feature === undefined) {
        return;
    }
    // TODO prevent two windows opening for same station?
    // Create new div to hold window content
    const div = document.createElement("div");
    div.classList.add("datadiv");
    const station = feature.get("sid");
    div.setAttribute("data-station", station);
    const network = feature.get("network");
    div.setAttribute("data-network", network);
    div.setAttribute("title", `${station} ${feature.get("sname")}`);
    let prefix = (network.endsWith("ASOS") ? "asos": "coop");
    prefix = (network === "ISUSM") ? "isusm": prefix;
    // Rule: jQuery removal - replace template cloning with vanilla JS
    const template = document.querySelector(`.${prefix}-data-template`);
    const newdiv = template.cloneNode(true);
    newdiv.style.display = "block";
    div.appendChild(newdiv);
    
    // Update all anchor href attributes
    const links = newdiv.querySelectorAll("a");
    links.forEach(a => {
        a.href = a.href.replaceAll("{station}", station).replaceAll("{network}", network);
    });
    newdiv.classList.remove(`${prefix}-data-template`);
    const classID = `${station}_${epoch}`;
    epoch += 1;
    windowFactory(div, classID);
}

function stationLayerStyleFunc(feature){
    const network = feature.get("network");
    if (network.search("ASOS") > 0){
        return airportStyle.enabled ? airportStyle: null;
    }
    if (network === "ISUSM"){
        return isusmStyle.enabled ? isusmStyle: null;
    }
    const sid = feature.get("sid");
    if (sid.substring(2, 1) === "C"){
        climodistrictStyle.getText().setText(sid.substring(0, 2) + parseInt(sid.substring(3, 3)));
        return climodistrictStyle.enabled ? climodistrictStyle: null;
    }
    if (sid.substring(2, 4) === "0000"){
        stateStyle.getText().setText(sid.substring(0, 2));
        return stateStyle.enabled ? stateStyle: null;
    }
    return climateStyle.enabled ? climateStyle: null;
}
function displayFeature(evt){
    const features = olMap.getFeaturesAtPixel(olMap.getEventPixel(evt.originalEvent));
    if (features.length > 0){
        const feature = features[0];
        popup.element.hidden = false;
        popup.setPosition(evt.coordinate);
        // Rule: jQuery removal - replace simple HTML content update
        document.getElementById('info-name').innerHTML = `[${feature.get("sid")}] ${escapeHTML(feature.get('sname'))}`;
    } else {
        popup.element.hidden = true;
    }
}

function initMap(){
    stationLayer = new ol.layer.Vector({
        title: "Stations",
        source: new ol.source.Vector({
            url: "/geojson/network.py?network=FPS",
            format: new ol.format.GeoJSON()
        }),
        style: stationLayerStyleFunc
    });
    overviewMap = new ol.control.OverviewMap({
        target: document.querySelector('#overviewmap'),
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                type: 'base',
                source: new ol.source.OSM()
            }),
            make_iem_tms('US States', 'usstates', true, '')
        ],
        collapseLabel: '\u00BB',
        collapsible: false,
        label: '\u00AB',
        collapsed: false,
      });
    olMap = new ol.Map({
        target: 'olmap',
        controls: ol.control.defaults.defaults().extend([overviewMap]),
        view: new ol.View({
            enableRotation: false,
            center: ol.proj.transform([-94.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7,
            maxZoom: 16,
            minZoom: 6
        }),
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                type: 'base',
                source: new ol.source.OSM()
            }),
            make_iem_tms('US States', 'usstates', true, ''),
            make_iem_tms('US Counties', 'uscounties', false, ''),
            stationLayer
        ]
    });

    const ls = new ol.control.LayerSwitcher();
    olMap.addControl(ls);
    olMap.on("click", mapClickHandler);
    olMap.on("pointermove", (evt) => {
        if (evt.dragging){
            return;
        }
        displayFeature(evt);
    });
    //  showing the position the user clicked
    popup = new ol.Overlay({
        element: document.getElementById('popover'),
        offset: [7, 7]
    });
    olMap.addOverlay(popup);
}
function loadImage(elem){
    const div = document.createElement("div");
    div.title = elem.title;
    // Rule: jQuery removal - replace data attribute access
    const tgt = elem.dataset.target;
    const pp = document.createElement("p");
    const ahref = document.createElement("a");
    ahref.href = tgt;
    ahref.target = "_blank";
    ahref.text = "IEM Website Link";
    ahref.classList.add("btn");
    ahref.classList.add("btn-secondary");
    pp.appendChild(ahref);
    div.appendChild(pp);
    const img = document.createElement("img");
    img.classList.add("img");
    img.classList.add("img-fluid");
    img.src = elem.src;
    div.appendChild(img);
    
    // Rule: jQuery removal - replace jQuery UI dialog with Bootstrap modal
    const modalId = `modal-${Date.now()}`;
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = modalId;
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-hidden', 'true');
    
    modal.innerHTML = `
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${escapeHTML(div.title)}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center">
                </div>
            </div>
        </div>
    `;
    
    // Add content to modal body
    const modalBody = modal.querySelector('.modal-body');
    modalBody.appendChild(div);
    
    // Add modal to DOM
    document.body.appendChild(modal);
    
    // Show modal using Bootstrap (with fallback)
    let bootstrapModal = null;
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    } else {
        // Fallback: show modal manually
        modal.classList.add('show');
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
        
        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
        
        // Clean up function
        modal._cleanup = () => {
            backdrop.remove();
            document.body.classList.remove('modal-open');
        };
    }
    
    // Clean up when modal is hidden
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
    
    // Fallback cleanup for manual modal
    const closeBtn = modal.querySelector('.btn-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            if (bootstrapModal) {
                bootstrapModal.hide();
            } else {
                modal.classList.remove('show');
                modal.style.display = 'none';
                if (modal._cleanup) modal._cleanup();
                setTimeout(() => modal.remove(), 300);
            }
        });
    }

}

function compute_href(uri){
    // Some magic here :/
    const tokens = uri.split("/");
    let res = "";
    if (tokens[1] === "plotting"){
        res = `/plotting/auto/?q=${escapeHTML(tokens[4])}&`;
        const tokens2 = escapeHTML(tokens[5]).split("::");
        tokens2.forEach((a) => {
            if (a.startsWith("_")){
                return;
            }
            const tokens3 = a.split(":");
            res += `${tokens3[0]}=${tokens3[1]}&`;
        });
    }
    return res;
}
function loadAutoplot(container, uri, divid){
    // Rule: jQuery removal - replace simple DOM selection
    let target = container.querySelector(".data-display");
    
    // If target is not found, try to find it in modal structure
    if (!target) {
        const modal = container.closest('.modal');
        if (modal) {
            target = modal.querySelector('.data-display');
        }
    }
    
    // If still not found, create a data display area
    if (!target) {
        target = document.createElement('div');
        target.className = 'data-display';
        container.appendChild(target);
    }
    
    // Remove any previous content
    target.innerHTML = '';
    const iemhref = compute_href(uri);
    const pp = document.createElement("p");
    const ahref = document.createElement("a");
    ahref.href = iemhref;
    ahref.target = "_blank";
    ahref.text = "IEM Website Link";
    ahref.classList.add("btn");
    ahref.classList.add("btn-secondary");
    ahref.classList.add("mb-3");
    pp.appendChild(ahref);
    // Rule: jQuery removal - replace appendTo with vanilla JS
    target.appendChild(pp);
    if (uri.endsWith("js")){
        // Create a div to append into that target
        const datadiv = document.createElement("div");
        datadiv.id = divid;
        datadiv.classList.add("viz");
        target.appendChild(datadiv);
        // Rule: jQuery removal - replace $.getScript with vanilla JS
        const script = document.createElement('script');
        script.src = uri;
        document.head.appendChild(script);
    } else {
        const img = document.createElement("img");
        img.classList.add("img");
        img.classList.add("img-fluid");
        img.src = uri;
        target.appendChild(img);
    }

}
function changeStations(elem){
    // Rule: jQuery removal - replace simple attribute access
    const netclass = elem.id;
    if (netclass === "asos"){
        airportStyle.enabled = elem.checked;
    }
    if (netclass === "isusm"){
        isusmStyle.enabled = elem.checked;
    }
    if (netclass === "coop"){
        climateStyle.enabled = elem.checked;
    }
    if (netclass === "cd"){
        climodistrictStyle.enabled = elem.checked;
    }
    if (netclass === "state"){
        stateStyle.enabled = elem.checked;
    }
    stationLayer.changed();
}
function loaderClicked(elem){
    // Rule: jQuery removal - replace jQuery element wrapping and closest()
    let container = elem.closest(".datadiv");
    
    // If not found, look for modal which should have the data attributes copied
    if (!container) {
        container = elem.closest(".modal");
    }
    
    if (!container || !container.dataset.station || !container.dataset.network) {
        return;
    }
    
    // Rule: jQuery removal - replace data attribute access
    const station = container.dataset.station;
    const network = container.dataset.network;
    const tpl = elem.dataset.urlTemplate;
    const divid = `d${station}${network}`;
    
    // Look for form elements in the container
    const monthSelect = container.querySelector("select[name=month]");
    const typeSelect = container.querySelector("select[name=type]");
    
    if (!monthSelect || !typeSelect) {
        return;
    }
    
    // Rule: jQuery removal - replace jQuery find() and val() with vanilla JS
    const month = escapeHTML(monthSelect.value);
    const type = escapeHTML(typeSelect.value);
    const uri = tpl
        .replaceAll("{station}", station)
        .replaceAll("{network}", network)
        .replaceAll("{elem}", divid)
        .replaceAll("{month}", month)
        .replaceAll("{type}", type);
    
    loadAutoplot(container, uri, divid);
}
function initUI(){
    // Add event delegation for maprow images - Rule: jQuery removal
    document.addEventListener('click', (event) => {
        if (event.target.matches('.maprow img')) {
            loadImage(event.target);
        }
    });
    
    // Add event delegation for checkboxes - Rule: jQuery removal
    document.addEventListener('click', (event) => {
        if (event.target.matches('.cs') || event.target.matches('.form-check-input.cs')) {
            changeStations(event.target);
        }
    });
}

function resizeCharts(container) {
    // Rule: jQuery removal - update resizeCharts to work with Bootstrap modals
    // console.log("resizeCharts called");
    
    // Find all charts within the container and resize them
    Highcharts.charts.forEach((chart) => {
        if (!chart) return; // Skip undefined/null charts
        
        // Check if this chart is within the current container
        const chartContainer = chart.renderTo;
        if (container.contains && container.contains(chartContainer)) {
            const height = chartContainer.clientHeight;
            const width = chartContainer.clientWidth;
            chart.setSize(width, height);
        }
    });
}

function windowFactory(initdiv, classID) {
    // Rule: jQuery removal - replace jQuery UI dialog with custom Bootstrap modal
    const modalId = `modal-${classID}-${Date.now()}`;
    const modal = document.createElement('div');
    modal.className = `modal fade ${classID}`;
    modal.id = modalId;
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-hidden', 'true');
    
    // Get title from initdiv
    const title = initdiv.getAttribute('title') || 'Data Window';
    
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header d-flex justify-content-between align-items-center">
                    <h5 class="modal-title">${title}</h5>
                    <div class="btn-group">
                        <button type="button" class="btn btn-sm btn-outline-secondary minimize-btn" title="Minimize">
                            <span aria-hidden="true">−</span>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary maximize-btn" title="Maximize">
                            <span aria-hidden="true">□</span>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary close-btn" title="Close" data-bs-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">×</span>
                        </button>
                    </div>
                </div>
                <div class="modal-body p-0 d-flex">
                    <div class="data-sidebar">
                        <div class="sidebar-content">
                        </div>
                    </div>
                    <div class="data-display-area">
                        <div class="data-display">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add content to modal body with improved layout
    const modalBody = modal.querySelector('.modal-body');
    const sidebarContent = modalBody.querySelector('.sidebar-content');
    const dataDisplay = modalBody.querySelector('.data-display');
    
    // Copy data attributes from initdiv to modal for reference
    modal.dataset.station = initdiv.dataset.station;
    modal.dataset.network = initdiv.dataset.network;
    
    // Move the form controls and buttons to sidebar
    const formElements = initdiv.querySelectorAll('select, input, button, .autoload');
    formElements.forEach(element => {
        sidebarContent.appendChild(element);
    });
    
    // Create or ensure data display area exists
    if (!dataDisplay.hasChildNodes()) {
        // If no content in data display, set up a placeholder
        const placeholder = document.createElement('div');
        placeholder.className = 'text-center text-muted p-4';
        placeholder.innerHTML = '<p>Select an option from the sidebar to display data</p>';
        dataDisplay.appendChild(placeholder);
    }
    
    // Add modal to DOM
    document.body.appendChild(modal);
    
    // Create Bootstrap modal instance
    let bootstrapModal = null;
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        bootstrapModal = new bootstrap.Modal(modal, {
            backdrop: false, // Allow multiple modals
            keyboard: true
        });
    }
    
    // Add custom minimize/maximize functionality
    const minimizeBtn = modal.querySelector('.minimize-btn');
    const maximizeBtn = modal.querySelector('.maximize-btn');
    const closeBtn = modal.querySelector('.close-btn');
    const modalDialog = modal.querySelector('.modal-dialog');
    const modalContent = modal.querySelector('.modal-content');
    
    let isMinimized = false;
    let isMaximized = false;
    let originalState = {};
    
    minimizeBtn.addEventListener('click', () => {
        if (!isMinimized) {
            originalState = {
                height: modalContent.style.height,
                position: modalDialog.style.position,
                top: modalDialog.style.top,
                left: modalDialog.style.left,
                width: modalDialog.style.width
            };
            modalContent.style.height = '40px';
            modalDialog.style.position = 'fixed';
            modalDialog.style.top = `${window.innerHeight - 50 - dockPosition}px`;
            modalDialog.style.left = '0px';
            modalDialog.style.width = '300px';
            modalBody.style.display = 'none';
            dockPosition += 50;
            isMinimized = true;
            minimizeBtn.innerHTML = '<span aria-hidden="true">□</span>';
            minimizeBtn.title = "Restore";
        } else {
            modalContent.style.height = originalState.height;
            modalDialog.style.position = originalState.position;
            modalDialog.style.top = originalState.top;
            modalDialog.style.left = originalState.left;
            modalDialog.style.width = originalState.width;
            modalBody.style.display = 'block';
            dockPosition -= 50;
            isMinimized = false;
            minimizeBtn.innerHTML = '<span aria-hidden="true">−</span>';
            minimizeBtn.title = "Minimize";
        }
    });
    
    maximizeBtn.addEventListener('click', () => {
        if (!isMaximized) {
            if (!isMinimized) {
                originalState = {
                    height: modalContent.style.height,
                    maxWidth: modalDialog.style.maxWidth
                };
            }
            modalContent.style.height = '100vh';
            modalDialog.style.maxWidth = '100vw';
            modalDialog.className = 'modal-dialog w-100 h-100 m-0';
            isMaximized = true;
            maximizeBtn.innerHTML = '<span aria-hidden="true">⧉</span>';
            maximizeBtn.title = "Restore";
        } else {
            modalContent.style.height = originalState.height || '80vh';
            modalDialog.style.maxWidth = originalState.maxWidth || '90vw';
            modalDialog.className = 'modal-dialog modal-xl';
            isMaximized = false;
            maximizeBtn.innerHTML = '<span aria-hidden="true">□</span>';
            maximizeBtn.title = "Maximize";
        }
        // Trigger chart resize after maximize/restore
        setTimeout(() => resizeCharts(modal), 200);
    });
    
    // Close button handler
    closeBtn.addEventListener('click', () => {
        if (bootstrapModal) {
            bootstrapModal.hide();
        } else {
            modal.classList.remove('show');
            modal.style.display = 'none';
            setTimeout(() => modal.remove(), 300);
        }
    });
    
    // Show modal
    if (bootstrapModal) {
        bootstrapModal.show();
    } else {
        // Fallback: show modal manually
        modal.classList.add('show');
        modal.style.display = 'block';
    }
    
    // Clean up when modal is hidden
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
    
    // Trigger chart resize when modal is shown
    modal.addEventListener('shown.bs.modal', () => {
        resizeCharts(modal);
    });
    
    // Fallback for manual modal show
    if (!bootstrapModal) {
        setTimeout(() => resizeCharts(modal), 300);
    }
    // Need to reattach the click handler as elements have been moved to modal
    // Rule: jQuery removal - replace jQuery selection and event handling
    const divs = modal.querySelectorAll(".autoload");
    divs.forEach(div => {
        div.addEventListener('click', (event) => {
            // Remove active class from all autoload divs in this modal
            divs.forEach(d => d.classList.remove('active'));
            // Add active class to clicked div
            event.target.classList.add('active');
            loaderClicked(event.target);
        });
    });
    
    // Also ensure form elements work properly
    const selectElements = modal.querySelectorAll('select');
    const inputElements = modal.querySelectorAll('input');
    const buttonElements = modal.querySelectorAll('button:not(.minimize-btn):not(.maximize-btn):not(.close-btn):not(.btn-close)');
    
    // Add event listeners for form interactions
    [...selectElements, ...inputElements].forEach(element => {
        element.addEventListener('change', () => {
            // Trigger any active autoload when form values change
            const activeAutoload = modal.querySelector('.autoload.active');
            if (activeAutoload) {
                loaderClicked(activeAutoload);
            }
        });
    });
    
    buttonElements.forEach(button => {
        if (!button.hasAttribute('data-listener-added')) {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                if (button.classList.contains('autoload')) {
                    // Remove active class from all autoload divs in this modal
                    divs.forEach(d => d.classList.remove('active'));
                    // Add active class to clicked div
                    button.classList.add('active');
                }
                loaderClicked(button);
            });
            button.setAttribute('data-listener-added', 'true');
        }
    });
    
    if (divs.length > 0) {
        divs[0].classList.add('active');
        divs[0].click();
    }

}

// Rule: jQuery removal - replace document ready
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initUI();
});