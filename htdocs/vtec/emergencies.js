/* global moment, ol */
let olmap = null;
let elayer = null;
let element = null;

const sbwStyle = [new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#FFF',
        width: 4.5
    })
}), new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#319FD3',
        width: 3
    }),
    fill: new ol.style.Fill({
        color: '#319FD330'
    })
})
];
const sbwLookup = {
    "TO": '#FF0000',
    "FF": '#00FF00'
};


function load_data() {
    $.ajax({
        url: "/api/1/nws/emergencies.geojson",
        method: "GET",
        dataType: "json",
        success: (geodata) => {
            const format = new ol.format.GeoJSON({
                featureProjection: "EPSG:3857"
            });
            const vectorSource = new ol.source.Vector({
                features: format.readFeatures(geodata)
            });
            elayer.setSource(vectorSource);
            $.each(geodata.features, (_idx, feat) => {
                const prop = feat.properties;
                const lbl = (prop.phenomena === "TO") ? "Tornado" : "Flash Flood";
                $('#thetable tbody').append(
                    `<tr><td>${prop.year}</td><td>${prop.wfo}</td><td>${prop.states}</td><td><a href="${prop.uri}">${prop.eventid}</a></td><td>${lbl} Warning</td><td>${prop.utc_issue}</td><td>${prop.utc_expire}</td></tr>`);
            });

        }
    })
}
function featureHTML(features, lalo) {
    const html = ['<div class="panel panel-default">',
        '<div class="panel-heading">',
        `<h3 class="panel-title">Emergencies List @${lalo[0].toFixed(3)}E ${lalo[1].toFixed(3)}N</h3>`,
        '</div>',
        '<div class="panel-body">'];
    $.each(features, (_i, feature) => {
        const dt = moment.utc(feature.get('utc_issue')).format('MMM Do, YYYY');
        const lbl = (feature.get("phenomena") === "TO") ? "Tornado" : "Flash Flood";
        html.push(
            `<strong>${dt}<strong> <a href="${feature.get('uri')}">${lbl} #${feature.get('eventid')}</a><br />`
        );
    });
    html.push('</div></div>');
    return html.join('\n');
}
function init_map() {
    element = document.getElementById('popup');
    elayer = new ol.layer.Vector({
        title: 'Emergencies',
        style: (feature) => {
            sbwStyle[1].getStroke().setColor(sbwLookup[feature.get('phenomena')]);
            sbwStyle[1].getFill().setColor(`${sbwLookup[feature.get('phenomena')]}30`);
            return sbwStyle;
        },
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        })
    });
    olmap = new ol.Map({
        target: 'map',
        view: new ol.View({
            enableRotation: false,
            center: ol.proj.transform([-94.5, 37.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 4
        }),
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                source: new ol.source.OSM()
            }),
            elayer
        ]
    });
    const popup = new ol.Overlay({
        element,
        positioning: 'bottom-center',
        stopEvent: false,
        offset: [0, -5]
    });
    olmap.addOverlay(popup);

    olmap.on('click', (evt) => {
        const features = [];
        olmap.forEachFeatureAtPixel(evt.pixel, (feature2) => {
            features.push(feature2);
        });
        if (features.length > 0) {
            const coordinates = features[0].getGeometry().getFirstCoordinate();
            const lalo = ol.proj.transform(coordinates, 'EPSG:3857', 'EPSG:4326')
            popup.setPosition(coordinates);
            $(element).popover({
                'placement': 'top',
                'html': true,
                'content': featureHTML(features, lalo)
            });
            $(element).popover('show');
        } else {
            $(element).popover('destroy');
        }
    });


}
function init_ui() {
    $('#makefancy').click(() => {
        $("#thetable table").DataTable();
    });
}

$(document).ready(() => {
    init_map();
    init_ui();
    load_data();
});