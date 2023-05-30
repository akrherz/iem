// Map select widget that can appear

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


function stationLayerStyleFunc(feature, _resolution) {
    const network = feature.get("network");
    if (network.search("CLIMATE") > 0) {
        const sid = feature.get("sid");
        if (sid.substr(2, 1) == "C") {
            climodistrictStyle.getText().setText(sid.substr(0, 2) + parseInt(sid.substr(3, 3)));
            return climodistrictStyle;
        }
        if (sid.substr(2, 4) === "0000") {
            stateStyle.getText().setText(sid.substr(0, 2));
            return stateStyle;
        }
    }
    return climateStyle;
}

function mapFactory(network, formname) {
    // Check the state of our button
    const state = parseInt($(`#button_${network}_${formname}`).data("state"), 10);
    if (state === 0) {
        // first time to open
        $(`#button_${network}_${formname}`).data("state", 1);
        $(`#button_${network}_${formname}`).text("Hide Map");
    } else if (state === 1) {
        // Should hide me
        $(`#button_${network}_${formname}`).data("state", 2);
        $(`#button_${network}_${formname}`).text("Show Map");
        $(`#map_${network}_${formname}`).css("display", "none");
        return;
    } else {
        // Should show me
        $(`#button_${network}_${formname}`).data("state", 1);
        $(`#button_${network}_${formname}`).text("Hide Map");
        $(`#map_${network}_${formname}`).css("display", "block");
        return;
    }

    $(`#map_${network}_${formname}`).css("display", "block");

    var olMap = new ol.Map({
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
    stationLayer.getSource().on('change', (_e) => {
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
    var popup = new ol.Overlay({
        element: document.getElementById(`popup_${network}_${formname}`),
        offset: [7, 7]
    });
    olMap.addOverlay(popup);

    olMap.on('pointermove', (event) => {
        if (event.dragging) { return; }
        var feature = olMap.forEachFeatureAtPixel(event.pixel,
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
        $(`#popup_${network}_${formname}`).html(html.join(""));
    });
    olMap.on("click", (event) => {
        var feature = olMap.forEachFeatureAtPixel(event.pixel,
            (feature2) => {
                return feature2;
            });
        if (feature === undefined) {
            return;
        }
        const station = feature.get("sid");
        $(`select[name="${formname}"]`).select2().val(station).trigger("change");
    });
    // Fix responsive issues
    olMap.updateSize();

};
