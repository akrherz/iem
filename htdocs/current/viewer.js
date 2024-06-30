/* global $, ol, moment */
let map = null;
let n0q = null;
let webcamGeoJsonLayer = null;
let idotdashcamGeoJsonLayer = null;
let idotRWISLayer = null;
let sbwlayer = null;
let ts = null;
let aqlive = 0;
let realtimeMode = true;
let currentCameraFeature = null;
let cameraID = "ISUC-006";
const ISOFMT = "Y-MM-DD[T]HH:mm:ss[Z]";

const sbwLookup = {
    "TO": 'red',
    "MA": 'purple',
    "EW": 'green',
    "SV": 'yellow',
    "SQ": "#C71585",
    "DS": "#FFE4C4"
};

const sbwStyle = [new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#FFF',
        width: 4.5
    })
}), new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#319FD3',
        width: 3
    })
})
];

const cameraStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/yellow_arrow.png'
    })
});
const trackaplowStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/trackaplow.png',
        scale: 0.4
    })
});
const trackaplowStyle2 = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/trackaplow_red.png',
        scale: 0.6
    })
});
const rwisStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/rwiscam.svg',
        scale: 0.6
    })
});
const cameraStyle2 = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/red_arrow.png',
        scale: 1.2
    })
});

function text(str) {
    return $("<p>").text(str).html();
}


function liveShot() {
    if (aqlive) return;
    aqlive = true;
    ts = new Date();
    $("#webcam_image").attr('src', `/current/live/${currentCameraFeature.get("cid")}.jpg?ts=${ts.getTime()}`);
    aqlive = false;
}

// Updates the window location shown for deep linking
function updateHashLink() {
    if (!currentCameraFeature) {
        return;
    }
    const extra = realtimeMode ? "" : `/${$('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT)}`;
    window.location.href = `#${currentCameraFeature.get("cid")}${extra}`;
}

function findFeatureByCid(cid) {
    // Find the feature for the given camera id
    let feature = null;
    webcamGeoJsonLayer.getSource().forEachFeature((feat) => {
        if (feat.get('cid') == cid) {
            feature = feat;
        }
    });
    if (feature) {
        return feature;
    }
    idotdashcamGeoJsonLayer.getSource().forEachFeature((feat) => {
        if (feat.get('cid') == cid) {
            feature = feat;
        }
    });
    if (feature) {
        return feature;
    }
    idotRWISLayer.getSource().forEachFeature((feat) => {
        if (feat.get('cid') == cid) {
            feature = feat;
        }
    });
    return feature;
}

function handleRWISClick(img) {
    $("#rwismain").attr('src', $(img).attr("src"));
}

function doRWISView() {
    // Do the magic that is the multi-view RWIS data...
    $("#singleimageview").css("display", "none");
    $("#rwisview").css("display", "block");
    $("#rwislist").empty();
    let i = 0;
    let hit = false;
    while (i < 10) {
        const url = currentCameraFeature.get(`imgurl${i}`);
        if (url !== null && url !== undefined) {
            if (!hit) {
                $("#rwismain").attr('src', url);
                hit = true;
                continue;
            }
            $("#rwislist").append(`<div class="col-md-2"><img onclick="handleRWISClick(this);" src="${url}" class="img img-responsive"></div>`);
        }
        i += 1;
    }
}

// main workflow for updating the webcam image shown to the user
function updateCamera() {
    if (!currentCameraFeature) {
        currentCameraFeature = findFeatureByCid(cameraID);
        if (!currentCameraFeature) {
            return;
        }
    }
    const cid = currentCameraFeature.get("cid");
    if (cid.startsWith("IDOT-")) {
        doRWISView();
        updateHashLink();
    }
    else {
        $("#singleimageview").css("display", "block");
        $("#rwisview").css("display", "none");
        $("#liveshot").css("display", "block");
        let url = currentCameraFeature.get("url");
        if (url === undefined) {
            $("#liveshot").css("display", "none");
            url = currentCameraFeature.get("imgurl");
        }
        if (url === undefined) {
            url = currentCameraFeature.get("imgurl0");
        }
        let valid = currentCameraFeature.get("valid");
        if (valid === undefined) {
            valid = currentCameraFeature.get("utc_valid");
        }
        let name = currentCameraFeature.get("name");
        if (name === undefined) {
            name = "Iowa DOT Dash Cam";
        }
        if (url !== undefined) {
            $("#webcam_image").attr('src', url);
            $("#webcam_title").html(
                `[${currentCameraFeature.get("cid")}] ${name} @ ${moment(valid).format("D MMM YYYY h:mm A")}`);
            updateHashLink();
        }
    }

}
function cronMinute() {
    // We are called every minute
    if (!realtimeMode) return;
    refreshRADAR();
    refreshJSON();
}

function getRADARSource() {
    let dt = moment();
    if (!realtimeMode) dt = $('#dtpicker').data('DateTimePicker').date();
    dt.subtract(dt.minutes() % 5, 'minutes');
    const prod = dt.year() < 2011 ? 'N0R' : 'N0Q';
    $("#radar_title").html(`US Base Reflectivity @ ${dt.format("h:mm A")}`);
    return new ol.source.XYZ({
        url: `https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/ridge::USCOMP-${prod}-${dt.utc().format('YMMDDHHmm')}/{z}/{x}/{y}.png`
    });
}

function refreshRADAR() {
    if (n0q) {
        n0q.setSource(getRADARSource());
    }
}
function refreshJSON() {
    let url = "/geojson/webcam.geojson?network=TV";
    if (!realtimeMode) {
        // Append the current timestamp to the URI
        url += "&valid=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
    }
    let newsource = new ol.source.Vector({
        url,
        format: new ol.format.GeoJSON()
    });
    newsource.on('change', function () {
        updateCamera();
    });
    webcamGeoJsonLayer.setSource(newsource);

    // Dashcam
    url = "/api/1/idot_dashcam.geojson";
    if (!realtimeMode) {
        // Append the current timestamp to the URI
        url += "?valid=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
    }
    newsource = new ol.source.Vector({
        url,
        format: new ol.format.GeoJSON()
    });
    newsource.on('change', function () {
        updateCamera();
    });
    idotdashcamGeoJsonLayer.setSource(newsource);

    // RWIS
    url = "/api/1/idot_rwiscam.geojson";
    if (!realtimeMode) {
        // Append the current timestamp to the URI
        url += "?valid=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
    }
    newsource = new ol.source.Vector({
        url,
        format: new ol.format.GeoJSON()
    });
    newsource.on('change', function () {
        updateCamera();
    });
    idotRWISLayer.setSource(newsource);

    url = "/geojson/sbw.geojson";
    if (!realtimeMode) {
        // Append the current timestamp to the URI
        url += "?ts=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
    }
    sbwlayer.setSource(new ol.source.Vector({
        url,
        format: new ol.format.GeoJSON()
    }));
}

// Set the current camera by cid

function setCamera(cid) {
    const feature = findFeatureByCid(cid);
    if (feature) {
        currentCameraFeature = feature;
    }
    $(`#c${cid}`).prop('checked', true);
    updateHashLink();
    updateCamera();
}

function parseURI() {
    const tokens = window.location.href.split('#');
    if (tokens.length == 2) {
        const tokens2 = tokens[1].split("/");
        if (tokens2.length == 1) {
            cameraID = text(tokens[1]);
        } else {
            cameraID = text(tokens2[0]);
            $('#toggle_event_mode button').eq(1).click();
            $('#dtpicker').data('DateTimePicker').date(moment(text(tokens2[1])));
        }
    }
}

function buildUI() {

    // Time increment and decrement buttons
    $("button.timecontrol").click((evt) => {
        const offset = parseInt($(evt.target).data('offset'));
        const dt = $('#dtpicker').data('DateTimePicker').date();
        dt.add(offset, 'minutes');
        $('#dtpicker').data('DateTimePicker').date(dt);
        // unblur the button
        $(evt.target).blur();
    });

    // Thanks to http://jsfiddle.net/hmgyu371/
    $('#toggle_event_mode button').click(function () { // this
        if ($(this).hasClass('locked_active') || $(this).hasClass('unlocked_inactive')) {
            // Enable Archive
            realtimeMode = false;
            $('#dtdiv').show();
            refreshJSON();
        } else {
            // Enable Realtime
            realtimeMode = true;
            $('#dtdiv').hide();
            cronMinute();
        }

        $('#toggle_event_mode button').eq(0).toggleClass('locked_inactive locked_active btn-default btn-info');
        $('#toggle_event_mode button').eq(1).toggleClass('unlocked_inactive unlocked_active btn-info btn-default');
    });

    $('#dtpicker').datetimepicker({
        defaultDate: new Date(),
        icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar"
        }
    });
    $('#dtpicker').on('dp.change', () => {
        if (!realtimeMode) {
            refreshJSON();
            refreshRADAR();
        }
    });
}

$().ready(() => {
    buildUI();

    sbwlayer = new ol.layer.Vector({
        title: 'Storm Based Warnings',
        source: new ol.source.Vector({
            url: "/geojson/sbw.geojson",
            format: new ol.format.GeoJSON()
        }),
        style: (feature) => {
            const color = sbwLookup[feature.get('phenomena')];
            if (color === undefined) return;
            sbwStyle[1].getStroke().setColor(color);
            return sbwStyle;
        }
    });
    idotdashcamGeoJsonLayer = new ol.layer.Vector({
        title: 'Iowa DOT Truck Dashcams (2014-)',
        style: (feature) => {
            if (currentCameraFeature &&
                currentCameraFeature.get("cid") == feature.get("cid")) {
                currentCameraFeature = feature;
                return [trackaplowStyle2];
            }
            return [trackaplowStyle];
        }
    });
    idotRWISLayer = new ol.layer.Vector({
        title: 'Iowa DOT RWIS Webcams (2010-)',
        style: function (feature) {
            if (currentCameraFeature &&
                currentCameraFeature.get("cid") == feature.get("cid")) {
                currentCameraFeature = feature;
                return [rwisStyle];
            }
            return [rwisStyle];
        }
    });
    webcamGeoJsonLayer = new ol.layer.Vector({
        title: 'Webcams (2003-)',
        style: (feature) => {
            if (currentCameraFeature &&
                currentCameraFeature.get("cid") == feature.get("cid")) {
                currentCameraFeature = feature;
                // OL rotation is in radians!
                cameraStyle2.getImage().setRotation(
                    parseInt(feature.get('angle')) / 180.0 * 3.14, 10);
                return [cameraStyle2];
            }
            cameraStyle.getImage().setRotation(
                parseInt(feature.get('angle')) / 180.0 * 3.14, 10);
            return [cameraStyle];
        }
    });
    n0q = new ol.layer.Tile({
        title: 'NEXRAD Base Reflectivity',
        source: getRADARSource()
    });
    map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
        }),
            n0q,
            sbwlayer,
            idotdashcamGeoJsonLayer,
            idotRWISLayer,
            webcamGeoJsonLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 6
        })
    });
    const layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    map.on('click', (evt) => {
        const feature = map.forEachFeatureAtPixel(evt.pixel,
            function (feature2) {
                return feature2;
            }
        );
        if (!feature) {
            return;
        }
        // Remove styling
        if (currentCameraFeature) {
            currentCameraFeature.setStyle(feature.getStyle());
        }
        // Update
        currentCameraFeature = feature;
        // Set new styling
        if (feature.get("angle") !== undefined) {
            cameraStyle2.getImage().setRotation(
                parseInt(feature.get('angle')) / 180.0 * 3.14, 10);
            feature.setStyle(cameraStyle2);
        }
        updateCamera();
    });

    parseURI();
    refreshJSON();
    updateCamera();

    window.setInterval(cronMinute, 60000);
});
