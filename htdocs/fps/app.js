var epoch = 0;
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
    // TODO prevent two windows opening for same station?
    // Create new div to hold window content
    var div = document.createElement("div");
    div.classList.add("datadiv");
    div.setAttribute("data-station", feature.get("sid"));
    div.setAttribute("data-network", feature.get("network"));
    div.setAttribute("title", feature.get("sid") + " " + feature.get("sname"));
    var $newdiv = $(".coop-data-template").clone().css("display", "block").appendTo($(div));
    $newdiv.removeClass("coop-data-template");
    var classID = feature.get("sid") + "_" + epoch;
    epoch += 1;
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
function createQRDialog(qrurl){
    var div = document.createElement("div");
    div.title = "Scan QR Code for IEM Website Link";
    var img = document.createElement("img");
    img.src = qrurl;
    div.appendChild(img);
    var dlg = $(div).dialog({
        draggable: true,
        autoOpen: true,
        classes: {
            "ui-dialog": "ui-window-options",
            "ui-dialog-titlebar": "ui-window-bar"
        },
        modal: true,
        responsive: true,
        width: 600,
        height: 600,
        close: function() {
            $(this).dialog('destroy').remove();
        }
    });
    $(dlg).dialog("open");
}

function loadAutoplot(container, qrurl, uri, divid){
    var $target = $(container).find(".data-display");
    // Remove any previous content
    $target.empty();
    // Create a QR code icon for usage
    var button = document.createElement("button");
    button.classList.add("qrbutton");
    button.innerHTML = '<i class="fa fa-qrcode"></i> QR';
    button.onclick = function(){
        createQRDialog(qrurl);
    }
    $(button).appendTo($target);
    // Create a div to append into that target
    var datadiv = document.createElement("div");
    datadiv.id = divid;
    datadiv.classList.add("viz");
    $(datadiv).appendTo($target);
    $.getScript(uri);

}
function loaderClicked(elem){
    var $elem = $(elem);
    var container = $elem.closest(".datadiv");
    var station = $(container).data("station");
    var network = $(container).data("network");
    var tpl = $elem.data("url-template");
    var divid = "d" + station + network;
    var uri = tpl
        .replace("{station}", station)
        .replace("{network}", network)
        .replace("{elem}", divid)
        .replace("{month}", $("select[name=coop_trends_month]").val())
        .replace("{type}", $("select[name=coop_trends_type]").val());
    var qrurl = uri.replace("/plot/", "/qrcode/").replace(".js", ".png");
    loadAutoplot(container, qrurl, uri, divid);
}

function wxCurrents(){
    // Show Weather
    $.ajax({
        url: "/json/current.py?network=ISUSM&station=BOOI4",
        dataType: "json",
        success: function(data) {
            var valid = data.last_ob.local_valid;
            $("#wxtime").text(valid);
            var tmpf = data.last_ob["airtemp[F]"].toFixed(1);
            $("#tmpf").text(tmpf);
        }
    });

}

$(document).ready(function() {
    initMap();
    wxCurrents();
    window.setInterval(wxCurrents, 120000);
});