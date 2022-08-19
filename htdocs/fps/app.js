var epoch = 0;
var olMap;
var overviewMap;
var stationLayer;

var airportStyle = new ol.style.Style({
    zindex: 99,
    image: new ol.style.Icon({
        src: "img/airport.svg",
        scale: [0.2, 0.2]
    })
});
airportStyle.enabled = true;
var isusmStyle = new ol.style.Style({
    zindex: 99,
    image: new ol.style.Icon({
        src: "img/isu.svg",
        scale: [0.2, 0.2]
    })
});
isusmStyle.enabled = true;
var climateStyle = new ol.style.Style({
    zindex: 100,
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
var climodistrictStyle = new ol.style.Style({
    zindex: 101,
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
var stateStyle = new ol.style.Style({
    zindex: 102,
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
    var network = feature.get("network");
    div.setAttribute("data-network", network);
    div.setAttribute("title", feature.get("sid") + " " + feature.get("sname"));
    var prefix = (network.endsWith("ASOS") ? "asos": "coop");
    prefix = (network == "ISUSM") ? "isusm": prefix;
    var $newdiv = $(`.${prefix}-data-template`).clone().css("display", "block").appendTo($(div));
    $newdiv.removeClass(`${prefix}-data-template`);
    var classID = feature.get("sid") + "_" + epoch;
    epoch += 1;
    windowFactory(div, classID);
}

function stationLayerStyleFunc(feature, resolution){
    var network = feature.get("network");
    if (network.search("ASOS") > 0){
        return airportStyle.enabled ? airportStyle: null;
    }
    if (network == "ISUSM"){
        return isusmStyle.enabled ? isusmStyle: null;
    }
    var sid = feature.get("sid");
    if (sid.substr(2, 1) == "C"){
        climodistrictStyle.getText().setText(sid.substr(0, 2) + parseInt(sid.substr(3, 3)));
        return climodistrictStyle.enabled ? climodistrictStyle: null;
    }
    if (sid.substr(2, 4) == "0000"){
        stateStyle.getText().setText(sid.substr(0, 2));
        return stateStyle.enabled ? stateStyle: null;
    }
    return climateStyle.enabled ? climateStyle: null;
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
        ],
        collapseLabel: '\u00BB',
        collapsible: false,
        label: '\u00AB',
        collapsed: false,
      });
    olMap = new ol.Map({
        target: 'olmap',
        controls: ol.control.defaults().extend([overviewMap]),
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
        width: 800,
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
    if (uri.endsWith("js")){
        // Create a div to append into that target
        var datadiv = document.createElement("div");
        datadiv.id = divid;
        datadiv.classList.add("viz");
        $(datadiv).appendTo($target);
        $.getScript(uri);
    } else {
        var img = document.createElement("img");
        img.classList.add("img");
        img.classList.add("img-responsive");
        img.src = uri;
        $(img).appendTo($target);
    }

}
function changeStations(elem){
    var netclass = $(elem).attr("id");
    if (netclass == "asos"){
        airportStyle.enabled = elem.checked;
    }
    if (netclass == "isusm"){
        isusmStyle.enabled = elem.checked;
    }
    if (netclass == "coop"){
        climateStyle.enabled = elem.checked;
    }
    if (netclass == "cd"){
        climodistrictStyle.enabled = elem.checked;
    }
    if (netclass == "state"){
        stateStyle.enabled = elem.checked;
    }
    stationLayer.changed();
}
function loaderClicked(elem){
    var $elem = $(elem);
    var container = $elem.closest(".datadiv");
    var station = $(container).data("station");
    var network = $(container).data("network");
    var tpl = $elem.data("url-template");
    var divid = "d" + station + network;
    var month = container.find("select[name=coop_trends_month]").val();
    var type = container.find("select[name=coop_trends_type]").val();
    var uri = tpl
        .replace("{station}", station)
        .replace("{network}", network)
        .replace("{elem}", divid)
        .replace("{month}", month)
        .replace("{type}", type);
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
            var pday = data.last_ob["precip_today[in]"].toFixed(2);
            $("#pday").text(pday);
        }
    });

}

$(document).ready(function() {
    initMap();
    wxCurrents();
    window.setInterval(wxCurrents, 120000);
});