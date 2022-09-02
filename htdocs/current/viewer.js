var map;
var n0q;
var webcamGeoJsonLayer;
var idotdashcamGeoJsonLayer;
var sbwlayer;
var selectControl;
var ts = null;
var aqlive = 0;
var realtimeMode = true;
var currentCameraFeature;
var cameraID = "ISUC-003";
var ISOFMT = "Y-MM-DD[T]HH:mm:ss[Z]";

var sbwLookup = {
    "TO": 'red',
    "MA": 'purple',
    "EW": 'green',
    "SV": 'yellow',
    "SQ": "#C71585",
    "DS": "#FFE4C4"
};

var sbwStyle = [new ol.style.Style({
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

var cameraStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/yellow_arrow.png'
    })
});
var trackaplowStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/trackaplow.png',
        scale: 0.4
    })
});
var trackaplowStyle2 = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/trackaplow_red.png',
        scale: 0.6
    })
});
var cameraStyle2 = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/red_arrow.png',
        scale: 1.2
    })
});

function liveShot() {
    if (aqlive) return;
    aqlive = true;
    ts = new Date();
    $("#webcam_image").attr('src', "/current/live/" + currentCameraFeature.get("cid") + ".jpg?ts=" + ts.getTime());
    aqlive = false;
}

// Updates the window location shown for deep linking
function updateHashLink() {
    if (!currentCameraFeature){
        return;
    }
    var extra = realtimeMode ? "" : "/" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
    window.location.href = '#' + currentCameraFeature.get("cid") + extra;
}

function findFeatureByCid(cid) {
    // Find the feature for the given camera id
    var feature;
    webcamGeoJsonLayer.getSource().forEachFeature(function (feat) {
        if (feat.get('cid') == cid) {
            feature = feat;
        }
    });
    if (feature) {
        return feature;
    }
    idotdashcamGeoJsonLayer.getSource().forEachFeature(function (feat) {
        if (feat.get('cid') == cid) {
            feature = feat;
        }
    });
    return feature;
}

// main workflow for updating the webcam image shown to the user
function updateCamera() {
    if (!currentCameraFeature){
        currentCameraFeature = findFeatureByCid(cameraID);
        if (!currentCameraFeature){
            return;
        }
    }
    var url = currentCameraFeature.get("url");
    if (url === undefined) {
        url = currentCameraFeature.get("imgurl");
    }
    var valid = currentCameraFeature.get("valid");
    if (valid === undefined) {
        valid = currentCameraFeature.get("utc_valid");
    }
    var name = currentCameraFeature.get("name");
    if (name === undefined) {
        name = "Iowa DOT Dash Cam";
    }
    if (url !== undefined) {
        $("#webcam_image").attr('src', url);
        $("#webcam_title").html(
            "[" + currentCameraFeature.get("cid") + "] " + name +
            ' @ ' + moment(valid).format("D MMM YYYY h:mm A"));
        updateHashLink();
    }

}
function cronMinute() {
    // We are called every minute
    if (!realtimeMode) return;
    refreshRADAR();
    refreshJSON();
}

function getRADARSource() {
    var dt = moment();
    if (!realtimeMode) dt = $('#dtpicker').data('DateTimePicker').date();
    dt.subtract(dt.minutes() % 5, 'minutes');
    var prod = dt.year() < 2011 ? 'N0R' : 'N0Q';
    $("#radar_title").html('US Base Reflectivity @ ' + dt.format("h:mm A"));
    return new ol.source.XYZ({
        url: '/cache/tile.py/1.0.0/ridge::USCOMP-' + prod + '-' + dt.utc().format('YMMDDHHmm') + '/{z}/{x}/{y}.png'
    });
}

function refreshRADAR() {
    if (n0q) {
        n0q.setSource(getRADARSource());
    }
}
function refreshJSON() {
    var url = "/geojson/webcam.php?network=TV";
    if (!realtimeMode) {
        // Append the current timestamp to the URI
        url += "&ts=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
    }
    var newsource = new ol.source.Vector({
        url: url,
        format: new ol.format.GeoJSON()
    });
    newsource.on('change', function () {
        updateCamera();
    });
    webcamGeoJsonLayer.setSource(newsource);

    url = "/api/1/idot_dashcam.geojson";
    if (!realtimeMode) {
        // Append the current timestamp to the URI
        url += "?valid=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
    }
    newsource = new ol.source.Vector({
        url: url,
        format: new ol.format.GeoJSON()
    });
    newsource.on('change', function () {
        updateCamera();
    });
    idotdashcamGeoJsonLayer.setSource(newsource);

    var url = "/geojson/sbw.geojson";
    if (!realtimeMode) {
        // Append the current timestamp to the URI
        url += "?ts=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
    }
    sbwlayer.setSource(new ol.source.Vector({
        url: url,
        format: new ol.format.GeoJSON()
    }));
}

// Set the current camera by cid
function setCamera(cid) {
    var feature = findFeatureByCid(cid);
    if (feature) {
        currentCameraFeature = feature;
    }
    $("#c" + cid).prop('checked', true);
    updateHashLink();
    updateCamera();
}

function parseURI() {
    var tokens = window.location.href.split('#');
    if (tokens.length == 2) {
        var tokens2 = tokens[1].split("/");
        if (tokens2.length == 1) {
            cameraID = tokens[1];
        } else {
            cameraID = tokens2[0];
            $('#toggle_event_mode button').eq(1).click();
            $('#dtpicker').data('DateTimePicker').date(moment(tokens2[1]));
        }
    }
}

function buildUI() {

    // Thanks to http://jsfiddle.net/hmgyu371/
    $('#toggle_event_mode button').click(function () {
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
    $('#dtpicker').on('dp.change', function () {
        if (!realtimeMode) {
            refreshJSON();
            refreshRADAR();
        }
    });
}

$().ready(function () {
    buildUI();

    sbwlayer = new ol.layer.Vector({
        title: 'Storm Based Warnings',
        source: new ol.source.Vector({
            url: "/geojson/sbw.geojson",
            format: new ol.format.GeoJSON()
        }),
        style: function (feature, resolution) {
            var color = sbwLookup[feature.get('phenomena')];
            if (color === undefined) return;
            sbwStyle[1].getStroke().setColor(color);
            return sbwStyle;
        }
    });
    idotdashcamGeoJsonLayer = new ol.layer.Vector({
        title: 'Iowa DOT Truck Dashcams',
        style: function (feature, resolution) {
            if (currentCameraFeature &&
                currentCameraFeature.get("cid") == feature.get("cid")) {
                currentCameraFeature = feature;
                return [trackaplowStyle2];
            }
            return [trackaplowStyle];
        }
    });
    webcamGeoJsonLayer = new ol.layer.Vector({
        title: 'Webcams',
        style: function (feature, resolution) {
            if (currentCameraFeature &&
                currentCameraFeature.get("cid") == feature.get("cid")) {
                currentCameraFeature = feature;
                // OL rotation is in radians!
                cameraStyle2.getImage().setRotation(
                    parseInt(feature.get('angle')) / 180. * 3.14);
                return [cameraStyle2];
            }
            cameraStyle.getImage().setRotation(
                parseInt(feature.get('angle')) / 180. * 3.14);
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
            webcamGeoJsonLayer,
            idotdashcamGeoJsonLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 6
        })
    });
    var layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    map.on('click', function (evt) {
        var feature = map.forEachFeatureAtPixel(evt.pixel,
            function (feature, layer) {
                return feature;
            }
        );
        if (!feature) {
            return;
        }
        // Remove styling
        if (currentCameraFeature){
            currentCameraFeature.setStyle(feature.getStyle());
        }
        // Update
        currentCameraFeature = feature;
        // Set new styling
        if (feature.get("angle") !== undefined) {
            cameraStyle2.getImage().setRotation(
                parseInt(feature.get('angle')) / 180. * 3.14);
            feature.setStyle(cameraStyle2);
        }
        updateCamera();
    });

    parseURI();
    refreshJSON();
    updateCamera();

    window.setInterval(cronMinute, 60000);
});
