/* global defaultdt, ol, $ */
let map = null;
let gj = null;
let invgj = null;
let dtpicker = null;
let n0q = null;
let varname = 'tmpf';
let currentdt = new Date(defaultdt);
let timeChanged = false;

function pad(number) {
    let r = String(number);
    if (r.length === 1) {
        r = `0${r}`;
    }
    return r;
};


Date.prototype.toIEMString = function () {
    return this.getUTCFullYear()
        + pad(this.getUTCMonth() + 1)
        + pad(this.getUTCDate())
        + pad(this.getUTCHours())
        + pad(this.getUTCMinutes());
};

if (!Date.prototype.toISOString) {
    (function () {

        Date.prototype.toISOString = function () { // this
            return this.getUTCFullYear()
                + '-' + pad(this.getUTCMonth() + 1)
                + '-' + pad(this.getUTCDate())
                + 'T' + pad(this.getUTCHours())
                + ':' + pad(this.getUTCMinutes())
                + 'Z';
        };

    }());
}
function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

function logic() {
    timeChanged = true;
    currentdt = dtpicker.datetimepicker('getDate'); // toISOString()
    updateMap();
}
function updateTitle() {
    $('#maptitle').text(`The map is displaying ${$('#varpicker :selected').text()} valid at ${currentdt}`);
    if (timeChanged) {
        window.location.href = `#${varname}/${currentdt.toISOString()}`;
    } else {
        window.location.href = `#${varname}`;
    }
}

function updateMap() {
    if (currentdt && typeof currentdt != "string") {
        const dt = currentdt.toISOString();
        const uristamp = timeChanged ? `dt=${dt}` : "";
        gj.setSource(new ol.source.Vector({
            url: `/geojson/agclimate.py?${uristamp}`,
            format: new ol.format.GeoJSON()
        })
        );
        invgj.setSource(new ol.source.Vector({
            url: `/geojson/agclimate.py?inversion&${uristamp}`,
            format: new ol.format.GeoJSON()
        })
        );
    }
    n0q.setSource(new ol.source.XYZ({
        url: `/cache/tile.py/1.0.0/ridge::USCOMP-N0Q-${currentdt.toIEMString()}/{z}/{x}/{y}.png`
    })
    );
    updateTitle();
}


var mystyle = new ol.style.Style({
    text: new ol.style.Text({
        font: '16px Calibri,sans-serif',
        fill: new ol.style.Fill({
            color: '#000',
            width: 3
        }),
        stroke: new ol.style.Stroke({
            color: '#ff0',
            width: 5
        })
    })
});
var greenArrow = new ol.style.Style({
    image: new ol.style.Icon({
        crossOrigin: 'anonymous',
        scale: 0.04,
        src: '/images/green_arrow_up.svg',
    })
});
var redArrow = new ol.style.Style({
    image: new ol.style.Icon({
        crossOrigin: 'anonymous',
        scale: 0.04,
        src: '/images/red_arrow_down.svg',
    })
});

$().ready(() => {
    gj = new ol.layer.Vector({
        title: 'ISUSM Data',
        source: new ol.source.Vector({
            url: "/geojson/agclimate.py",
            format: new ol.format.GeoJSON()
        }),
        style(feature) {
            mystyle.getText().setText(feature.get(varname).toString());
            return [mystyle];
        }
    });
    invgj = new ol.layer.Vector({
        title: 'ISUSM Inversion Data',
        source: new ol.source.Vector({
            url: "/geojson/agclimate.py?inversion",
            format: new ol.format.GeoJSON()
        }),
        style(feature) {
            // Update the img src to the appropriate arrow
            $(`#${feature.getId()}_arrow`).attr(
                "src",
                feature.get("is_inversion") ? "/images/red_arrow_down.svg" : "/images/green_arrow_up.svg"
            );
            $(`#${feature.getId()}_15`).text(feature.get('tmpf_15'));
            $(`#${feature.getId()}_5`).text(feature.get('tmpf_5'));
            $(`#${feature.getId()}_10`).text(feature.get('tmpf_10'));
            return [feature.get("is_inversion") ? redArrow : greenArrow];
        }
    });
    n0q = new ol.layer.Tile({
        title: 'NEXRAD Base Reflectivity',
        source: new ol.source.XYZ({
            url: `/cache/tile.py/1.0.0/ridge::USCOMP-N0Q-${currentdt.toIEMString()}/{z}/{x}/{y}.png`
        })
    });
    map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
        }), n0q, invgj, gj],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
        })
    });

    // Popup showing the position the user clicked
    var popup = new ol.Overlay({
        element: document.getElementById('popup')
    });
    map.addOverlay(popup);
    // Support clicking on the map to get more details on the station
    map.on('click', (evt) => {
        const element = popup.getElement();
        $(element).popover('destroy');
        const pixel = map.getEventPixel(evt.originalEvent);
        const feature = map.forEachFeatureAtPixel(pixel, (feature2) => {
            return feature2;
        });
        if (feature) {
            popup.setPosition(evt.coordinate);
            let content = [
                `<p>Site ID: <code>${feature.getId()}</code>`,
                `Name: ${feature.get('name')}`,
                `Air Temp: ${feature.get('tmpf')}`,
                '</p>'
            ].join('<br/>');
            if (feature.get("tmpf_15")) {
                content = [
                    `<p>Site ID: <code>${feature.getId()}</code>`,
                    `Name: ${feature.get('name')}`,
                    `Inversion: ${feature.get("is_inversion") ? "Likely" : "Unlikely"}`,
                    `Air Temp @1.5ft: ${feature.get('tmpf_15')}`,
                    `Air Temp @5ft: ${feature.get('tmpf_5')}`,
                    `Air Temp @10ft: ${feature.get('tmpf_10')}`,
                    '</p>'
                ].join('<br/>');
            }
            $(element).popover({
                'placement': 'top',
                'animation': false,
                'html': true,
                'content': content
            });
            $(element).popover('show');
        }
    });

    const layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    dtpicker = $('#datetimepicker');
    dtpicker.datetimepicker({
        showMinute: true,
        showSecond: false,
        onSelect: logic,
        minDateTime: (new Date(2013, 1, 1, 0, 0)),
        maxDateTime: (new Date()),
        timeFormat: 'h:mm TT'
    });

    try {
        const tokens = window.location.href.split('#');
        if (tokens.length == 2) {
            const tokens2 = tokens[1].split("/");
            varname = text(tokens2[0]);
            $('#varpicker').val(varname);
            if (tokens2.length == 2) {
                currentdt = (new Date(Date.parse(text(tokens2[1]))));
                timeChanged = true;
            }
            gj.setStyle(gj.getStyle());
        }
    } catch {
        varname = 'tmpf';
        currentdt = new Date(defaultdt);
    }

    setDate();
    updateMap();
});

function setDate() {
    dtpicker.datepicker("disable")
        .datetimepicker('setDate', currentdt)
        .datepicker("enable");
}

function setupUI() {
    $(".dt").click(function () {
        timeChanged = true;
        $(this).removeClass('focus');
        currentdt = new Date(currentdt.valueOf() + parseInt($(this).data('delta')));
        setDate();
        updateMap();
    });


    $('#varpicker').change(() => {
        varname = text($('#varpicker').val());
        gj.setStyle(gj.getStyle());
        updateTitle();
    });
};

$(document).ready(() => {
    setupUI();
});
