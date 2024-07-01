/* global $, ol */
let renderattr = "high";
let vectorLayer = null;
let map = null;
let element = null;
let fontSize = 14;

function text(str){
    // XSS shim
    return $("<p>").text(str).html();
}

function updateURL() {
    const tt = $.datepicker.formatDate("yymmdd",
        $("#datepicker").datepicker('getDate'));
    window.location.href = `#${tt}/${renderattr}`;
}

 
function updateMap() {
    renderattr = text($('#renderattr').val());
    vectorLayer.setStyle(vectorLayer.getStyle());
    updateURL();
}

function updateDate() {
    const fullDate = $.datepicker.formatDate("yy-mm-dd",
        $("#datepicker").datepicker('getDate'));
    map.removeLayer(vectorLayer);
    vectorLayer = makeVectorLayer(fullDate);
    map.addLayer(vectorLayer);
    updateURL();
}

var vectorStyleFunction = function (feature) {
    let style = null;
    const value = feature.get(renderattr);
    let color = "#FFFFFF";
    const outlinecolor = "#000000";
    if (value != "M") {
        if (renderattr.indexOf("depart") > -1) {
            if (renderattr.indexOf("high") > -1 || renderattr.indexOf("low") > -1) {
                if (value > 0) {
                    color = "#FF0000";
                } else if (value < 0) {
                    color = "#00FFFF";
                }
            } else {
                if (value < 0) {
                    color = "#FF0000";
                } else if (value > 0) {
                    color = "#00FFFF";
                }
            }
        }
        style = [new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.6)'
            }),
            text: new ol.style.Text({
                font: fontSize + 'px Calibri,sans-serif',
                text: value.toString(),
                fill: new ol.style.Fill({
                    color,
                    width: 1
                }),
                stroke: new ol.style.Stroke({
                    color: outlinecolor,
                    width: 3
                })
            })
        })];
    } else {
        style = [new ol.style.Style({
            image: new ol.style.Circle({
                fill: new ol.style.Fill({
                    color: 'rgba(255,255,255,0.4)'
                }),
                stroke: new ol.style.Stroke({
                    color: '#3399CC',
                    width: 1.25
                }),
                radius: 5
            }),
            fill: new ol.style.Fill({
                color: 'rgba(255,255,255,0.4)'
            }),
            stroke: new ol.style.Stroke({
                color: '#3399CC',
                width: 1.25
            })
        })
        ];
    }
    return style;
}


function makeVectorLayer(dt) {
    return new ol.layer.Vector({
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON(),
            projection: ol.proj.get('EPSG:3857'),
            url: `/geojson/cf6.py?dt=${dt}`
        }),
        style: vectorStyleFunction
    });
}

$(document).ready(() => {

    $("#datepicker").datepicker({
        dateFormat: "DD, d MM, yy",
        minDate: new Date(2001, 1, 1),
        maxDate: new Date()
    });
    $("#datepicker").datepicker('setDate', new Date());
    $("#datepicker").change(function () {
        updateDate();
    });

    vectorLayer = makeVectorLayer($.datepicker.formatDate("yy-mm-dd", new Date()));
    const key = 'AsgbmE8m-iBbkypiCOE23M0qElHUfEQtaTvPdDPdM0p7s0N7pJcgrjo70FXjX6bY';
    map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
            title: 'Global Imagery',
            source: new ol.source.BingMaps({ key: key, imagerySet: 'Aerial' })
        }),
        new ol.layer.Tile({
            title: 'State Boundaries',
            source: new ol.source.XYZ({
                url: '/c/tile.py/1.0.0/usstates/{z}/{x}/{y}.png'
            })
        }),
            vectorLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: [-10575351, 5160979],
            zoom: 3
        })
    });

    const layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    element = document.getElementById('popup');

    const popup = new ol.Overlay({
        element: element,
        positioning: 'bottom-center',
        stopEvent: false
    });
    map.addOverlay(popup);

    $(element).popover({
        'placement': 'top',
        'html': true,
        content: function () { return $('#popover-content').html(); }
    });

    // display popup on click
    map.on('click', (evt) => {
        const feature = map.forEachFeatureAtPixel(evt.pixel,
            (feature2) => {
                return feature2;
            });
        if (feature) {
            const geometry = feature.getGeometry();
            const coord = geometry.getCoordinates();
            popup.setPosition(coord);
            const content = `<p><strong>${feature.get('name')}</strong><br />High: ${feature.get('high')}<br />Low: ${feature.get('low')}<br />Precip: ${feature.get('precip')}<br />Snow: ${feature.get('snow')}</p>`;
            $('#popover-content').html(content);
            $(element).popover('show');

            $('#cf6report').html("<h3>Loading text, one moment please...</h3>");
            $.get(feature.get('link'), (data) => {
                $('#cf6report').html(`<pre>${data}</pre>`);
            });

        } else {
            $(element).popover('hide');
        }

    });

    // Figure out if we have anything specified from the window.location
    var tokens = window.location.href.split("#");
    if (tokens.length == 2) {
        // #YYYYmmdd/variable
        tokens = tokens[1].split("/");
        if (tokens.length == 2) {
            const tpart = tokens[0];
            renderattr = tokens[1];
            $('select[id=renderattr] option[value=' + renderattr + ']').attr("selected", "selected");
            const dstr = `${tpart.substr(4, 2)}/${tpart.substr(6, 2)}/${tpart.substr(0, 4)}`;
            $("#datepicker").datepicker("setDate", new Date(dstr));
            updateDate();
        }
    }

    // Font size buttons
    $('#fplus').click(() => {
        fontSize += 2;
        vectorLayer.setStyle(vectorStyleFunction);
    });
    $('#fminus').click(() => {
        fontSize -= 2;
        vectorLayer.setStyle(vectorStyleFunction);
    });

});
