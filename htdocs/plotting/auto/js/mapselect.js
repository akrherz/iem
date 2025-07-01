/* global ol */

const climateStyle = new ol.style.Style({
    zIndex: 100,
    image: new ol.style.Circle({
        fill: new ol.style.Fill({ color: '#00ff00' }),
        stroke: new ol.style.Stroke({
            color: '#008800',
            width: 2.25
        }),
        radius: 7
    })
});

const stationStyleOffline = new ol.style.Style({
    zIndex: 99,
    image: new ol.style.Circle({
        fill: new ol.style.Fill({ color: '#ff0000' }),
        stroke: new ol.style.Stroke({
            color: '#880000',
            width: 2.25
        }),
        radius: 7
    })
});

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


function stationLayerStyleFunc(feature) {
    const network = feature.get("network");
    if (network.search("CLIMATE") > 0) {
        const sid = feature.get("sid");
        if (sid.substring(2, 1) === "C") {
            climodistrictStyle.getText().setText(sid.substring(0, 2) + parseInt(sid.substring(3, 3)));
            return climodistrictStyle;
        }
        if (sid.substring(2, 4) === "0000") {
            stateStyle.getText().setText(sid.substring(0, 2));
            return stateStyle;
        }
    }
    if (feature.get("archive_end") !== null) return stationStyleOffline; 
    return climateStyle;
}

 
function mapFactory(network, formname) {
    // Check the state of our button
    const button = document.getElementById(`button_${network}_${formname}`);
    const state = parseInt(button.dataset.state || "0", 10);
    const mapWrap = document.getElementById(`map_${network}_${formname}_wrap`);
    
    if (state === 0) {
        // first time to open
        button.dataset.state = "1";
        button.textContent = "Hide Map";
    } else if (state === 1) {
        // Should hide me
        button.dataset.state = "2";
        button.textContent = "Show Map";
        mapWrap.style.display = "none";
        return;
    } else {
        // Should show me
        button.dataset.state = "1";
        button.textContent = "Hide Map";
        mapWrap.style.display = "block";
        return;
    }

    mapWrap.style.display = "block";

    const olMap = new ol.Map({
        target: `map_${network}_${formname}`,
        view: new ol.View({
            enableRotation: false,
            center: ol.proj.transform([-94.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7,
            maxZoom: 16,
            minZoom: 1
        }),
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                type: 'base',
                source: new ol.source.OSM()
            })
        ]
    });
    const stationLayer = new ol.layer.Vector({
        title: "Stations",
        source: new ol.source.Vector({
            url: `/geojson/network.py?network=${network}`,
            format: new ol.format.GeoJSON()
        }),
        style: stationLayerStyleFunc
    });
    stationLayer.getSource().on('change', () => {
        if (stationLayer.getSource().getState() === 'ready') {
            olMap.getView().fit(
                stationLayer.getSource().getExtent(),
                {
                    size: olMap.getSize(),
                    padding: [50, 50, 50, 50]
                }
            );
        }
    });
    olMap.addLayer(stationLayer);
    //  showing the position the user clicked
    const popup = new ol.Overlay({
        element: document.getElementById(`popup_${network}_${formname}`),
        offset: [7, 7]
    });
    olMap.addOverlay(popup);

    olMap.on('pointermove', (event) => {
        if (event.dragging) { return; }
        const feature = olMap.forEachFeatureAtPixel(event.pixel,
            (feature2) => {
                return feature2;
            });
        if (feature === undefined) {
            popup.element.hidden = true;
            return;
        }
        popup.element.hidden = false;
        popup.setPosition(event.coordinate);
        const html = [
            `<strong>ID:</strong> ${feature.get("sid")}`,
            `<br /><strong>Name:</strong> ${feature.get("sname")}`,
            `<br /><strong>POR:</strong> ${feature.get("time_domain")}`,
        ]
        document.getElementById(`popup_${network}_${formname}`).innerHTML = html.join("");
    });
    olMap.on("click", (event) => {
        const feature = olMap.forEachFeatureAtPixel(event.pixel,
            (feature2) => {
                return feature2;
            });
        if (feature === undefined) {
            return;
        }
        const station = feature.get("sid");
        const selectElement = document.querySelector(`select[name="${formname}"]`);
        if (selectElement?.tomselect) {
            // Use Tom Select API to update value and UI
            selectElement.tomselect.setValue(station, true);
        } else if (selectElement) {
            // Fallback for plain select
            selectElement.value = station;
            const changeEvent = new Event('change', { bubbles: true });
            selectElement.dispatchEvent(changeEvent);
        }
    });
    // Fix responsive issues
    olMap.updateSize();

};

document.addEventListener('DOMContentLoaded', () => {
    // appease linter
    const nonExistentElement = document.getElementById("doesnotexist");
    if (nonExistentElement) {
        nonExistentElement.addEventListener('click', () => {
            mapFactory("IACLIMATE", "station");
        });
    }
});