/* global windowFactory, Highcharts, ol, $ */
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
    div.setAttribute("title", station + " " + feature.get("sname"));
    let prefix = (network.endsWith("ASOS") ? "asos": "coop");
    prefix = (network === "ISUSM") ? "isusm": prefix;
    const $newdiv = $(`.${prefix}-data-template`).clone().css("display", "block").appendTo($(div));
    $newdiv.find("a").each((_i, a) => {
        a.href = a.href.replaceAll("{station}", station).replaceAll("{network}", network);
    });
    $newdiv.removeClass(`${prefix}-data-template`);
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
    if (sid.substr(2, 1) === "C"){
        climodistrictStyle.getText().setText(sid.substr(0, 2) + parseInt(sid.substr(3, 3)));
        return climodistrictStyle.enabled ? climodistrictStyle: null;
    }
    if (sid.substr(2, 4) === "0000"){
        stateStyle.getText().setText(sid.substr(0, 2));
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
        $('#info-name').html(`[${feature.get("sid")}] ${feature.get('sname')}`);
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
    const tgt = $(elem).data("target");
    const pp = document.createElement("p");
    const ahref = document.createElement("a");
    ahref.href = tgt;
    ahref.target = "_blank";
    ahref.text = "IEM Website Link";
    ahref.classList.add("btn");
    ahref.classList.add("btn-default");
    pp.appendChild(ahref);
    div.appendChild(pp);
    const img = document.createElement("img");
    img.classList.add("img");
    img.classList.add("img-responsive");
    img.src = elem.src;
    div.appendChild(img);
    const dlg = $(div).dialog({
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
        close() {
            $(this).dialog('destroy').remove();
        }
    });
    $(dlg).dialog("open");

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
    const $target = $(container).find(".data-display");
    // Remove any previous content
    $target.empty();
    const iemhref = compute_href(uri);
    const pp = document.createElement("p");
    const ahref = document.createElement("a");
    ahref.href = iemhref;
    ahref.target = "_blank";
    ahref.text = "IEM Website Link";
    ahref.classList.add("btn");
    ahref.classList.add("btn-default");
    pp.appendChild(ahref);
    $(pp).appendTo($target);
    if (uri.endsWith("js")){
        // Create a div to append into that target
        const datadiv = document.createElement("div");
        datadiv.id = divid;
        datadiv.classList.add("viz");
        $(datadiv).appendTo($target);
        $.getScript(uri);
    } else {
        const img = document.createElement("img");
        img.classList.add("img");
        img.classList.add("img-responsive");
        img.src = uri;
        $(img).appendTo($target);
    }

}
function changeStations(elem){
    const netclass = $(elem).attr("id");
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
    const $elem = $(elem);
    const container = $elem.closest(".datadiv");
    const station = $(container).data("station");
    const network = $(container).data("network");
    const tpl = $elem.data("url-template");
    const divid = `d${station}${network}`;
    const month = escapeHTML(container.find("select[name=month]").val());
    const type = escapeHTML(container.find("select[name=type]").val());
    const uri = tpl
        .replaceAll("{station}", station)
        .replaceAll("{network}", network)
        .replaceAll("{elem}", divid)
        .replaceAll("{month}", month)
        .replaceAll("{type}", type);
    loadAutoplot(container, uri, divid);
}
function initUI(){
    $(".maprow img").click((event) => {
        loadImage(event.target);
    });
    $(".cs").click((event) => {
        changeStations(event.target);
    });
}

// https://stackoverflow.com/questions/48712560
function addButtons(dlg) {
    // Define Buttons
    const $close = dlg.find(".ui-dialog-titlebar-close");
    const $min = $("<button>", {
        class: "ui-button ui-corner-all ui-widget ui-button-icon-only ui-window-minimize",
        type: "button",
        title: "Minimize"
    }).insertBefore($close);
    $min.data("isMin", false);
    $("<span>", {
        class: "ui-button-icon ui-icon ui-icon-minusthick"
    }).appendTo($min);
    $("<span>", {
        class: "ui-button-icon-space"
    }).html(" ").appendTo($min);
    const $max = $("<button>", {
        class: "ui-button ui-corner-all ui-widget ui-button-icon-only ui-window-maximize",
        type: "button",
        title: "Maximize"
    }).insertBefore($close);
    $max.data("isMax", false);
    $("<span>", {
        class: "ui-button-icon ui-icon ui-icon-plusthick"
    }).appendTo($max);
    $("<span>", {
        class: "ui-button-icon-space"
    }).html(" ").appendTo($max);
    // Define Function
    $min.click(() => {
        if ($min.data("isMin") === false) {
            $min.data("original-pos", dlg.position());
            $min.data("original-size", {
                width: dlg.width(),
                height: dlg.height()
            });
            $min.data("isMin", true);
            dlg.animate({
                height: '40px',
                top: $(window).height() - 50 - dockPosition,
                left: 0
            }, 200);
            dockPosition += 50;
            dlg.find(".ui-dialog-content").hide();
        } else {
            $min.data("isMin", false);
            dlg.find(".ui-dialog-content").show();
            dlg.animate({
                height: $min.data("original-size").height + "px",
                top: $min.data("original-pos").top + "px",
                left: $min.data("original-pos").left + "px"
            }, 200);
            dockPosition -= 50;
        }
    });
    $max.click(() => {
        if ($max.data("isMax") === false) {
            $max.data("original-pos", dlg.position());
            $max.data("original-size", {
                width: dlg.width(),
                height: dlg.height()
            });
            $max.data("isMax", true);
            dlg.animate({
                height: $(window).height() + "px",
                width: $(window).width() - 20 + "px",
                top: 0,
                left: 0
            }, 200);
        } else {
            $max.data("isMax", false);
            dlg.animate({
                height: $max.data("original-size").height + "px",
                width: $max.data("original-size").width + "px",
                top: $max.data("original-pos").top + "px",
                left: $max.data("original-pos").top + "px"
            }, 200);
        }
        // Wait for parent to resize!
        window.setTimeout(() => { resizeCharts(dlg); }, 500);
    });
}
function resizeCharts(dlg) {
    // console.log("resizeCharts with dlg.height=" + dlg.height());
    // Fixes responsive troubles with boostrap?
    $(dlg).find(".ui-dialog-content").height(dlg.height() - 40);
    // Causes charts to fit their container
    $(Highcharts.charts).each((_i, chart) => {
        const height = chart.renderTo.clientHeight;
        const width = chart.renderTo.clientWidth;
        chart.setSize(width, height);
    });
}

function windowFactory(initdiv, classID) {
    const dlg = $(initdiv).dialog({
        draggable: true,
        autoOpen: true,
        dialogClass: classID,
        classes: {
            "ui-dialog": "ui-window-options",
            "ui-dialog-titlebar": "ui-window-bar"
        },
        modal: false,
        responsive: true,
        width: 800,
        height: 500,
        close() {
            $(dlg).dialog('destroy').remove();
        },
        resizeStop() {
            resizeCharts(dlg);
        }
    });

    addButtons($(`.${classID}`));
    $(dlg).dialog("open");
    // Need to reattach the click handler as JqueryUI mucks things up
    const $divs = $(initdiv).find(".autoload");
    $divs.click((event) => {
        loaderClicked(event.target);
    });
    $divs.first().click();

}

$(document).ready(() => {
    initMap();
    initUI();
});