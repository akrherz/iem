// TODO print grid
var dragPan;
var olmap; // Openlayers map
var lsrtable; // LSR DataTable
var sbwtable; // SBW DataTable
var n0q = {}; // RADAR Layer
let countiesLayer = {};
let statesLayer = {};
var wfoSelect;
var stateSelect;
var lsrtypefilter;
var sbwtypefilter;
var dateFormat1 = "YYYYMMDDHHmm";
var realtime = false;
var TABLE_FILTERED_EVENT = "tfe";
var moment = window.moment || {}; // skipcq: JS-0239
var ol = window.ol || {}; // skipcq: JS-0239
var iemdata = window.iemdata || {}; // skipcq: JS-0239
let nexradBaseTime = moment().utc().subtract(moment().minutes() % 5, "minutes");

// Use momentjs for formatting
$.datetimepicker.setDateFormatter('moment');

// https://datatables.net/plug-ins/api/row().show()
$.fn.dataTable.Api.register('row().show()', function() { // need this to work
    const page_info = this.table().page.info();
    // Get row index
    const new_row_index = this.index();
    // Row position
    const row_position = this.table()
        .rows({ search: 'applied' })[0]
        .indexOf(new_row_index);
    // Already on right page ?
    if ((row_position >= page_info.start && row_position < page_info.end) || row_position < 0) {
        // Return row object
        return this;
    }
    // Find page number
    const page_to_display = Math.floor(row_position / this.table().page.len());
    // Go to that page
    this.table().page(page_to_display);
    // Return row object
    return this;
});

function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

function parse_href() {
    // Figure out how we were called
    let sts = null;
    let ets = null;
    const tokens = window.location.href.split('#');
    if (tokens.length !== 2) {
        return;
    }
    const tokens2 = tokens[1].split("/");
    if (tokens2.length < 2) {
        return;
    }
    const ids = text(tokens2[0]).split(",");
    if (ids.length > 0){
        if (ids[0].length === 3){
            wfoSelect.val(ids).trigger("change");
        } else {
            stateSelect.val(ids).trigger("change");
            $("#by_state").click();
        }
    }
    if (tokens2.length > 2) {
        sts = moment.utc(text(tokens2[1]), dateFormat1);
        ets = moment.utc(text(tokens2[2]), dateFormat1);
    }
    else {
        realtime = true;
        $("#realtime").prop('checked', true);
        // Offset timing
        ets = moment.utc();
        sts = moment.utc(ets).add(parseInt(tokens2[1], 10), 'seconds');
    }
    $("#sts").val(sts.local().format("L LT"));
    $("#ets").val(ets.local().format("L LT"));
    updateRADARTimes();
    if (tokens2.length > 3) {
        // We have settings
        applySettings(tokens2[3]);
    }
    setTimeout(loadData, 0);
}
function cronMinute() {
    if (!realtime) return;
    // Compute the delta
    const sts = moment($("#sts").val(), 'L LT').utc();
    const ets = moment($("#ets").val(), 'L LT').utc();
    $("#ets").val(moment().format('L LT'));
    const seconds = ets.diff(sts) / 1000;  // seconds
    $("#sts").val(moment().subtract(seconds, 'seconds').format('L LT'));
    setTimeout(loadData, 0);
}
function getRADARSource(dt) {
    const prod = dt.year() < 2011 ? 'N0R' : 'N0Q';
    return new ol.source.XYZ({
        url: `https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/ridge::USCOMP-${prod}-${dt.utc().format('YMMDDHHmm')}/{z}/{x}/{y}.png`
    });
}

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

var sbwLookup = {
    "TO": 'red',
    "MA": 'purple',
    "FF": 'green',
    "EW": 'green',
    "FA": 'green',
    "FL": 'green',
    "SV": 'yellow',
    "SQ": "#C71585",
    "DS": "#FFE4C4"
};

// Lookup 'table' for styling
var lsrLookup = {
    "0": "icons/tropicalstorm.gif",
    "1": "icons/flood.png",
    "2": "icons/other.png",
    "3": "icons/other.png",
    "4": "icons/other.png",
    "5": "icons/ice.png",
    "6": "icons/cold.png",
    "7": "icons/cold.png",
    "8": "icons/fire.png",
    "9": "icons/other.png",
    "a": "icons/other.png",
    "A": "icons/wind.png",
    "B": "icons/downburst.png",
    "C": "icons/funnelcloud.png",
    "D": "icons/winddamage.png",
    "E": "icons/flood.png",
    "F": "icons/flood.png",
    "v": "icons/flood.png",
    "G": "icons/wind.png",
    "h": "icons/hail.png",
    "H": "icons/hail.png",
    "I": "icons/hot.png",
    "J": "icons/fog.png",
    "K": "icons/lightning.gif",
    "L": "icons/lightning.gif",
    "M": "icons/wind.png",
    "N": "icons/wind.png",
    "O": "icons/wind.png",
    "P": "icons/other.png",
    "q": "icons/downburst.png",
    "Q": "icons/tropicalstorm.gif",
    "s": "icons/sleet.png",
    "T": "icons/tornado.png",
    "U": "icons/fire.png",
    "V": "icons/avalanche.gif",
    "W": "icons/waterspout.png",
    "X": "icons/funnelcloud.png",
    "x": "icons/debrisflow.png",
    "Z": "icons/blizzard.png"
};

var sbwStyle = [new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#000',
        width: 4.5
    })
}), new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#319FD3',
        width: 3
    })
})
];
var lsrStyle = new ol.style.Style({
    image: new ol.style.Icon({ src: lsrLookup['9'] })
});

var textStyle = new ol.style.Style({
    text: new ol.style.Text({
        font: 'bold 11px "Open Sans", "Arial Unicode MS", "sans-serif"',
        fill: new ol.style.Fill({
            color: 'white'
        }),
        placement: 'point',
        backgroundFill: new ol.style.Fill({
            color: "black"
        }),
        padding: [2, 2, 2, 2]
    })
});
const lsrTextBackgroundColor = {
    'S': 'purple',
    'R': 'blue',
    '5': 'pink'
};

// create vector layer
const lsrLayer = new ol.layer.Vector({
    title: "Local Storm Reports",
    source: new ol.source.Vector({
        format: new ol.format.GeoJSON()
    }),
    style: (feature, _resolution) => {
        if (feature.hidden === true) {
            return new ol.style.Style();
        }
        const mag = feature.get('magnitude').toString();
        const typ = feature.get('type');
        if (mag != "") {
            if (typ == 'S' || typ == 'R' || typ == '5') {
                textStyle.getText().setText(mag);
                textStyle.getText().getBackgroundFill().setColor(
                    lsrTextBackgroundColor[typ]
                );
                return textStyle;
            }
        }
        const url = lsrLookup[typ];
        if (url) {
            const icon = new ol.style.Icon({
                src: url
            });
            lsrStyle.setImage(icon);
        }
        return lsrStyle;
    }
});
lsrLayer.addEventListener(TABLE_FILTERED_EVENT, () => {
    // Turn all features back on
    lsrLayer.getSource().getFeatures().forEach((feat) => {
        feat.hidden = false;
    });
    // Filter out the map too
    lsrtable.rows({ "search": "removed" }).every(function (_idx) { // this
        lsrLayer.getSource().getFeatureById(this.data().id).hidden = true;
    });
    lsrLayer.changed();
});
lsrLayer.getSource().on('change', (_e) => {
    if (lsrLayer.getSource().isEmpty()) {
        return;
    }
    if (lsrLayer.getSource().getState() === 'ready') {
        olmap.getView().fit(
            lsrLayer.getSource().getExtent(),
            {
                size: olmap.getSize(),
                padding: [50, 50, 50, 50]
            }
        );
    }
    lsrtable.rows().remove();
    const data = [];
    lsrLayer.getSource().getFeatures().forEach((feat) => {
        const props = feat.getProperties();
        props.id = feat.getId();
        data.push(props);
    });
    lsrtable.rows.add(data).draw();

    // Build type filter
    lsrtable.column(7).data().unique().sort().each((d, _j) => {
        lsrtypefilter.append(`<option value="${d}">${d}</option`);
    });
});
lsrLayer.on('change:visible', updateURL);

const sbwLayer = new ol.layer.Vector({
    title: "Storm Based Warnings",
    source: new ol.source.Vector({
        format: new ol.format.GeoJSON()
    }),
    visible: true,
    style: (feature, _resolution) => {
        if (feature.hidden === true) {
            return new ol.style.Style();
        }
        const color = sbwLookup[feature.get('phenomena')];
        if (color === undefined) return;
        sbwStyle[1].getStroke().setColor(color);
        return sbwStyle;
    }
});
sbwLayer.on('change:visible', updateURL);
sbwLayer.addEventListener(TABLE_FILTERED_EVENT, () => {
    // Turn all features back on
    sbwLayer.getSource().getFeatures().forEach((feat) => {
        feat.hidden = false;
    });
    // Filter out the map too
    sbwtable.rows({ "search": "removed" }).every(function(_idx) {  // this
        sbwLayer.getSource().getFeatureById(this.data().id).hidden = true;
    });
    sbwLayer.changed();
});
sbwLayer.getSource().on('change', (_e) => {
    sbwtable.rows().remove();
    const data = [];
    sbwLayer.getSource().getFeatures().forEach(function (feat) {
        const props = feat.getProperties();
        props.id = feat.getId();
        data.push(props);
    });
    sbwtable.rows.add(data).draw();

    // Build type filter
    sbwtable.column(3).data().unique().sort().each((d, _j) => {
        sbwtypefilter.append(`<option value="${iemdata.vtec_phenomena[d]}">${iemdata.vtec_phenomena[d]}</option`);
    });

});

function formatLSR(data) {
    // Format what is presented
    return `<div><strong>Source:</strong> ${data.source} &nbsp; <strong>UTC Valid:</strong> ${data.valid}<br /><strong>Remark:</strong> ${data.remark}</div>`;
}

function revisedRandId() {
    return Math.random().toString(36).replace(/[^a-z]+/g, '').substr(2, 10);
}
function lsrHTML(feature) {
    const lines = [];
    const dt = moment.utc(feature.get("valid"));
    const ldt = dt.local().format("M/D LT");
    const zz = dt.utc().format("HH:mm");
    lines.push(`<strong>Valid:</strong> ${ldt} (${zz}Z)`);
    let vv = feature.get("source");
    if (vv !== null) {
        lines.push(`<strong>Source:</strong> ${vv}`);
    }
    vv = feature.get("typetext");
    if (vv !== null) {
        lines.push(`<strong>Type:</strong> ${vv}`);
    }
    vv = feature.get("magnitude");
    if (vv !== null && vv !== "") {
        let unit = feature.get("unit");
        if (unit === null) {
            unit = "";
        }
        lines.push(`<strong>Magnitude:</strong> ${vv} ${unit}`);
    }
    vv = feature.get("remark");
    if (vv !== null) {
        lines.push(`<strong>Remark:</strong> ${vv}`);
    }
    return lines.join("<br />");
}

function formatSBW(feature) {
    const lines = [];
    const ph = feature.get("phenomena");
    const pph = ph in iemdata.vtec_phenomena ? iemdata.vtec_phenomena[ph] : ph;
    const sig = feature.get("significance");
    const ss = sig in iemdata.vtec_significance ? iemdata.vtec_significance[sig] : sig;
    lines.push(`<strong>${pph} ${ss}</strong>`);
    const issue = moment.utc(feature.get("issue"));
    const expire = moment.utc(feature.get("expire"));
    let ldt = issue.local().format("M/D LT");
    let zz = issue.utc().format("HH:mm")
    lines.push(`<strong>Issued:</strong> ${ldt} (${zz}Z)`);
    ldt = expire.local().format("M/D LT");
    zz = expire.utc().format("HH:mm")
    lines.push(`<strong>Expired:</strong> ${ldt} (${zz}Z)`);
    lines.push(`<strong>More Details:</strong> <a href='${feature.get("href")}' target='_blank'>VTEC Browser</a>`);
    return lines.join("<br />");
}

function handleSBWClick(feature) {
    const divid = revisedRandId();
    const div = document.createElement("div");
    const title = `${feature.get("wfo")} ${feature.get("phenomena")}.${feature.get("significance")} #${feature.get("eventid")}`;
    div.innerHTML = `<div class="panel panel-primary panel-popup" id="${divid}"><div class="panel-heading">${title} &nbsp; <button type="button" class="close" data-target="#${divid}" data-dismiss="alert"> <span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button></div><div class="panel-body">${formatSBW(feature)}</div></div>`;
    const coordinates = feature.getGeometry().getFirstCoordinate();
    const marker = new ol.Overlay({
        position: coordinates,
        positioning: 'center-center',
        element: div,
        stopEvent: false,
        dragging: false
    });
    olmap.addOverlay(marker);
    div.addEventListener('mousedown', (_evt) => {
        dragPan.setActive(false);
        marker.set('dragging', true);
    });
    olmap.on('pointermove', (evt) => {
        if (marker.get('dragging') === true) {
            marker.setPosition(evt.coordinate);
        }
    });
    olmap.on('pointerup', (_evt) => {
        if (marker.get('dragging') === true) {
            dragPan.setActive(true);
            marker.set('dragging', false);
        }
    });
    const id = feature.getId();
    sbwtable.rows().deselect();
    sbwtable.row(
        sbwtable.rows((idx, data, _node) => {
            if (data["id"] === id) {
                sbwtable.row(idx).select();
                return true;
            }
            return false;
        })
    ).show().draw(false);

}
function initUI() {
    // Generate UI components of the page
    const handle = $("#radartime");
    $("#timeslider").slider({
        min: 0,
        max: 100,
        create: function () {
            handle.text(nexradBaseTime.local().format("L LT"));
        },
        slide: function (event, ui) {
            const dt = moment(nexradBaseTime);
            dt.add(ui.value * 5, 'minutes');
            handle.text(dt.local().format("L LT"));
        },
        change: function (event, ui) {
            const dt = moment(nexradBaseTime);
            dt.add(ui.value * 5, 'minutes');
            n0q.setSource(getRADARSource(dt));
            handle.text(dt.local().format("L LT"));
        }
    });
    n0q = new ol.layer.Tile({
        title: 'NEXRAD Base Reflectivity',
        visible: true,
        source: getRADARSource(nexradBaseTime)
    });
    n0q.on('change:visible', updateURL);
    lsrtypefilter = $("#lsrtypefilter").select2({
        placeholder: "Filter LSRs by Event Type",
        width: 300,
        multiple: true
    });
    lsrtypefilter.on("change", function() { // this
        const vals = $(this).val();
        const val = vals ? vals.join("|") : null;
        lsrtable.column(7).search(val ? '^' + val + '$' : '', true, false).draw();
    });
    sbwtypefilter = $("#sbwtypefilter").select2({
        placeholder: "Filter SBWs by Event Type",
        width: 300,
        multiple: true
    });
    sbwtypefilter.on("change", function() { // this
        const vals = $(this).val();
        const val = vals ? vals.join("|") : null;
        sbwtable.column(3).search(val ? '^' + val + '$' : '', true, false).draw();
    });
    wfoSelect = $("#wfo").select2({
        templateSelection: (state) => {
            return state.id;
        }
    });
    stateSelect = $("#state").select2({
        templateSelection: (state) => {
            return state.id;
        }
    });
    $.each(iemdata.wfos, function (idx, entry) {
        const opt = new Option(`[${entry[0]}] ${entry[1]}`, entry[0], false, false);
        wfoSelect.append(opt);
    });
    $.each(iemdata.states, function (idx, entry) {
        const opt = new Option(`[${entry[0]}] ${entry[1]}`, entry[0], false, false);
        stateSelect.append(opt);
    });

    $(".iemdtp").datetimepicker({
        format: "L LT",
        step: 1,
        maxDate: '+1970/01/03',
        minDate: '2003/01/01',
        onClose: (_dp, _input) => {
            setTimeout(loadData, 0);
        }
    });
    const sts = moment().subtract(1, 'day');
    const ets = moment();
    $("#sts").val(sts.format('L LT'));
    $("#ets").val(ets.format('L LT'));
    updateRADARTimes();

    $("#load").click(() => {
        setTimeout(loadData, 0);
    });
    $("#lsrshapefile").click(() => {
        window.location.href = getShapefileLink("lsr");
    });
    $("#lsrexcel").click(() => {
        window.location.href = `${getShapefileLink("lsr")}&fmt=excel`;
    });
    $("#lsrkml").click(() => {
        window.location.href = `${getShapefileLink("lsr")}&fmt=kml`;
    });
    $("#warnshapefile").click(() => {
        window.location.href = getShapefileLink("watchwarn");
    });
    $("#warnexcel").click(() => {
        window.location.href = `${getShapefileLink("watchwarn")}&accept=excel`;
    });
    $("#sbwshapefile").click(() => {
        window.location.href = `${getShapefileLink("watchwarn")}&limit1=yes`;
    });
    $("#realtime").click(function() {
        realtime = this.checked;
        if (realtime) {
            setTimeout(loadData, 0);
        }
    });
    statesLayer = make_iem_tms('US States', 'usstates', true, '');
    statesLayer.on('change:visible', updateURL);
    countiesLayer = make_iem_tms('US Counties', 'uscounties', false, '');
    countiesLayer.on('change:visible', updateURL);

    olmap = new ol.Map({
        target: 'map',
        controls: ol.control.defaults.defaults().extend([new ol.control.FullScreen()]),
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
            new ol.layer.Tile({
                title: "MapTiler Toner (Black/White)",
                type: 'base',
                visible: false,
                source: new ol.source.TileJSON({
                    url: 'https://api.maptiler.com/maps/toner/tiles.json?key=d7EdAVvDI3ocoa9OUt9Z',
                    tileSize: 512,
                    crossOrigin: 'anonymous'
                })
            }),
            new ol.layer.Tile({
                title: "MapTiler Pastel",
                type: 'base',
                visible: false,
                source: new ol.source.TileJSON({
                    url: 'https://api.maptiler.com/maps/pastel/tiles.json?key=d7EdAVvDI3ocoa9OUt9Z',
                    tileSize: 512,
                    crossOrigin: 'anonymous'
                })
            }),
            n0q,
            statesLayer,
            countiesLayer,
            sbwLayer,
            lsrLayer
        ]
    });
    const ls = new ol.control.LayerSwitcher();
    olmap.addControl(ls);
    olmap.getInteractions().forEach((interaction) => {
        if (interaction instanceof ol.interaction.DragPan) {
            dragPan = interaction;
        }
    });

    olmap.on('click', (evt) => {
        const feature = olmap.forEachFeatureAtPixel(evt.pixel,
            (feature2) => {
                return feature2;
            });
        if (feature === undefined) {
            return;
        }
        if (feature.get("phenomena") !== undefined) {
            handleSBWClick(feature);
            return;
        }
        if (feature.get('magnitude') === undefined) return;
        // evt.originalEvent.x
        const divid = revisedRandId();
        const div = document.createElement("div");
        div.innerHTML = `<div class="panel panel-primary panel-popup" id="${divid}"><div class="panel-heading">${feature.get("city")}, ${feature.get("st")} &nbsp; <button type="button" class="close" data-target="#${divid}" data-dismiss="alert"> <span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button></div><div class="panel-body">${lsrHTML(feature)}</div></div>`;
        const coordinates = feature.getGeometry().getCoordinates();
        const marker = new ol.Overlay({
            position: coordinates,
            positioning: 'center-center',
            element: div,
            stopEvent: false,
            dragging: false
        });
        olmap.addOverlay(marker);
        div.addEventListener('mousedown', (_evt) => {
            dragPan.setActive(false);
            marker.set('dragging', true);
        });
        olmap.on('pointermove', (evt2) => {
            if (marker.get('dragging') === true) {
                marker.setPosition(evt2.coordinate);
            }
        });
        olmap.on('pointerup', (_evt) => {
            if (marker.get('dragging') === true) {
                dragPan.setActive(true);
                marker.set('dragging', false);
            }
        });
        const id = feature.getId();
        lsrtable.rows().deselect();
        lsrtable.row(
            lsrtable.rows((idx, data, _node) => {
                if (data["id"] === id) {
                    lsrtable.row(idx).select();
                    return true;
                }
                return false;
            })
        ).show().draw(false);


    });

    lsrtable = $("#lsrtable").DataTable({
        select: true,
        rowId: 'id',
        columns: [
            {
                "data": "valid",
                "visible": false
            }, {
                "className": 'details-control',
                "orderable": false,
                "data": null,
                "defaultContent": ''
            }, {
                "data": "wfo"
            }, {
                "data": "valid",
                "type": "datetime",
                "orderData": [0]
            }, {
                "data": "county"
            }, {
                "data": "city"
            }, {
                "data": "st"
            }, {
                "data": "typetext"
            }, {
                "data": "magnitude"
            }
        ],
        columnDefs: [
            {
                targets: 3,
                render: (data) => {
                    return moment.utc(data).local().format('M/D LT');
                }
            }
        ]
    });
    lsrtable.on("search.dt", () => {
        lsrLayer.dispatchEvent(TABLE_FILTERED_EVENT);
    });
    // Add event listener for opening and closing details
    $('#lsrtable tbody').on('click', 'td.details-control', function() { // this
        const tr = $(this).closest('tr');
        const row = lsrtable.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child(formatLSR(row.data())).show();
            tr.addClass('shown');
        }
    });
    sbwtable = $("#sbwtable").DataTable({
        columns: [
            {
                "data": "issue",
                "visible": false
            }, {
                "data": "expire",
                "visible": false
            }, {
                "data": "wfo"
            }, {
                "data": "phenomena"
            }, {
                "data": "significance"
            }, {
                "data": "eventid"
            }, {
                "data": "issue",
                "orderData": [0]
            }, {
                "data": "expire",
                "orderData": [1]
            }
        ],
        columnDefs: [
            {
                targets: 3,
                render: (data) => {
                    return data in iemdata.vtec_phenomena ? iemdata.vtec_phenomena[data] : data;
                }
            }, {
                targets: 4,
                render: (data) => {
                    return data in iemdata.vtec_significance ? iemdata.vtec_significance[data] : data;
                }
            }, {
                targets: 5,
                render: (_data, type, row, _meta) => {
                    if (type == 'display') {
                        return `<a href="${row.href}">${row.eventid}</a>`;
                    }
                    return row.eventid;
                }
            }, {
                targets: [6, 7],
                render: (data) => {
                    return moment.utc(data).local().format('M/D LT');
                }
            }
        ]
    });
    sbwtable.on("search.dt", () => {
        sbwLayer.dispatchEvent(TABLE_FILTERED_EVENT);
    });
}

function genSettings() {
    /* Generate URL options set on this page */
    let s = "";
    s += (n0q.isVisible() ? "1" : "0");
    s += (lsrLayer.isVisible() ? "1" : "0");
    s += (sbwLayer.isVisible() ? "1" : "0");
    s += (realtime ? "1" : "0");
    s += (statesLayer.isVisible() ? "1" : "0");
    s += (countiesLayer.isVisible() ? "1" : "0");
    return s;
}

function updateURL() {
    const sts = moment($("#sts").val(), 'L LT').utc().format(dateFormat1);
    const ets = moment($("#ets").val(), 'L LT').utc().format(dateFormat1);
    const by = $("input[type=radio][name=by]:checked").val();
    const wfos = $("#wfo").val();  // null for all or array
    const states = $("#state").val();  // null for all or array
    var wstr = "";
    if (wfos !== null && by === "wfo") wstr = wfos.join(",");
    else if (states !== null && by === "state") wstr = states.join(",");
    window.location.href = `#${text(wstr)}/${sts}/${ets}/${genSettings()}`;

}
function applySettings(opts) {
    if (opts[0] !== undefined) { // Show RADAR
        n0q.setVisible(opts[0] === "1");
    }
    if (opts[1] !== undefined) { // Show LSRs
        lsrLayer.setVisible(opts[1] === "1");
    }
    if (opts[2] !== undefined) { // Show SBWs
        sbwLayer.setVisible(opts[2] === "1");
    }
    if (opts[3] === "1") { // Realtime
        realtime = true;
        $("#realtime").prop('checked', true);
    }
    if (opts[4] !== undefined) {
        statesLayer.setVisible(opts[4] === "1");
    }
    if (opts[5] !== undefined) {
        countiesLayer.setVisible(opts[5] === "1");
    }
}
function updateRADARTimes() {
    // Figure out what our time slider should look like
    const sts = moment($("#sts").val(), 'L LT').utc();
    const ets = moment($("#ets").val(), 'L LT').utc();
    sts.subtract(sts.minute() % 5, 'minutes');
    ets.add(5 - ets.minute() % 5, 'minutes');
    const times = ets.diff(sts) / 300000;  // 5 minute bins
    nexradBaseTime = sts;
    $("#timeslider")
        .slider("option", "max", times - 1)
        .slider("value", realtime ? times - 1 : 0);
}
function loadData() {
    // Load up the data please!
    if ($(".tab .active > a").attr("href") != "#2a") {
        $("#lsrtab").click();
    }
    const wfos = $("#wfo").val();  // null for all or array
    const states = $("#state").val();  // null for all or array
    const by = $("input[type=radio][name=by]:checked").val();
    const sts = moment($("#sts").val(), 'L LT').utc().format(dateFormat1);
    const ets = moment($("#ets").val(), 'L LT').utc().format(dateFormat1);
    updateRADARTimes();

    const opts = {
        sts,
        ets
    };
    if (by === "state"){
        opts.states = (states === null) ? "" : text(states.join(","));
    } else {
        opts.wfos = (wfos === null) ? "" : text(wfos.join(","));
    }
    lsrLayer.getSource().clear(true);
    sbwLayer.getSource().clear(true);

    $.ajax({
        data: opts,
        method: "GET",
        url: "/geojson/lsr.php",
        dataType: 'json',
        success: (data) => {
            if (data.features.length == 10000) {
                alert("App limit of 10,000 LSRs reached.");
            }
            lsrLayer.getSource().addFeatures(
                (new ol.format.GeoJSON({ featureProjection: 'EPSG:3857' })
                ).readFeatures(data)
            );
        }
    });
    $.ajax({
        data: opts,
        method: "GET",
        url: "/geojson/sbw.php",
        dataType: 'json',
        success: (data) => {
            sbwLayer.getSource().addFeatures(
                (new ol.format.GeoJSON({ featureProjection: 'EPSG:3857' })
                ).readFeatures(data)
            );
        }
    });
    updateURL();
}

function getShapefileLink(base) {
    let uri = `/cgi-bin/request/gis/${base}.py?`;
    const by = $("input[type=radio][name=by]:checked").val();
    const wfos = $("#wfo").val();
    if (wfos && by === "wfo") {
        for (let i = 0; i < wfos.length; i++) {
            uri += `&wfo[]=${text(wfos[i])}`;
        }
    }
    const states = $("#state").val();
    if (states && by == "state") {
        for (let i = 0; i < states.length; i++) {
            uri += `&states[]=${text(states[i])}`;
        }
    }
    const sts = moment($("#sts").val(), 'L LT');
    const ets = moment($("#ets").val(), 'L LT');
    uri += "&year1=" + sts.utc().format('Y');
    uri += "&month1=" + sts.utc().format('M');
    uri += "&day1=" + sts.utc().format('D');
    uri += "&hour1=" + sts.utc().format('H');
    uri += "&minute1=" + sts.utc().format('m');
    uri += "&year2=" + ets.utc().format('Y');
    uri += "&month2=" + ets.utc().format('M');
    uri += "&day2=" + ets.utc().format('D');
    uri += "&hour2=" + ets.utc().format('H');
    uri += "&minute2=" + ets.utc().format('m');
    return uri;
}
