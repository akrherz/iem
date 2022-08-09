var olMap;
var stationLayer;

var airportStyle = new ol.style.Style({
    zindex: 99,
    image: new ol.style.Icon({
        src: "img/airport.svg",
        scale: [0.2, 0.2]
    })
});
var climateStyle = new ol.style.Style({
    zindex: 100,
    image: new ol.style.Circle({
        fill: new ol.style.Fill({color: '#0f0'}),
        stroke: new ol.style.Stroke({
            color: '#000000',
            width: 2.25
        }),
        radius: 7
    })
    
});

function mapClickHandler(event){
    var feature = olMap.forEachFeatureAtPixel(event.pixel,
        function (feature) {
            return feature;
        });
    if (feature === undefined) {
        return;
    }
    var div = document.createElement("div");
    div.setAttribute("title", feature.get("sid"));
    $(".airport-data-template").clone().css("display", "block").appendTo($(div));
    var classID = feature.get("sid");
    windowFactory(div, classID);
}

function stationLayerStyleFunc(feature, resolution){
    var network = feature.get("network");
    if (network.search("ASOS") > 0){
        return airportStyle;
    }
    return climateStyle;
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
    olMap = new ol.Map({
        target: 'olmap',
        controls: ol.control.defaults().extend([new ol.control.FullScreen()]),
        view: new ol.View({
            enableRotation: false,
            center: ol.proj.transform([-94.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7,
            maxZoom: 16
        }),
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                type: 'base',
                source: new ol.source.OSM()
            }),
            stationLayer
        ]
    });
    var ls = new ol.control.LayerSwitcher();
    olMap.addControl(ls);
    olMap.on("click", mapClickHandler);

}

$(document).ready(() => {
    initMap();
});