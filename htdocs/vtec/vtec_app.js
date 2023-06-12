// previous hashlinking looks like 2017-O-NEW-KALY-WI-Y-0015

let olmap = null;
let productVectorCountyLayer = null;
let productVectorPolygonLayer = null;
let sbwIntersectionLayer = null;
let lsrLayer = null;
let radarTMSLayer = null;
let radartimes = [];
let eventTable = null;
let ugcTable = null;
let lsrTable = null;
let sbwLsrTable = null;
let element = null;
// CONFIG is set in the base HTML page
var CONFIG = window.CONFIG || {};  // skipcq: JS-0239
var ol = window.ol || {};  // skipcq: JS-0239
var moment = window.moment || {};  // skipcq: JS-0239

Number.prototype.padLeft = function (n, str) { // this
    return Array(n - String(this).length + 1).join(str || '0') + this;
};

const sbwLookup = {
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

const lsrLookup = {
    "0": "/lsr/icons/tropicalstorm.gif",
    "1": "/lsr/icons/flood.png",
    "2": "/lsr/icons/other.png",
    "3": "/lsr/icons/other.png",
    "4": "/lsr/icons/other.png",
    "5": "/lsr/icons/ice.png",
    "6": "/lsr/icons/cold.png",
    "7": "/lsr/icons/cold.png",
    "8": "/lsr/icons/fire.png",
    "9": "/lsr/icons/other.png",
    "a": "/lsr/icons/other.png",
    "A": "/lsr/icons/wind.png",
    "B": "/lsr/icons/downburst.png",
    "C": "/lsr/icons/funnelcloud.png",
    "D": "/lsr/icons/winddamage.png",
    "E": "/lsr/icons/flood.png",
    "F": "/lsr/icons/flood.png",
    "v": "/lsr/icons/flood.png",
    "G": "/lsr/icons/wind.png",
    "h": "/lsr/icons/hail.png",
    "H": "/lsr/icons/hail.png",
    "I": "/lsr/icons/hot.png",
    "J": "/lsr/icons/fog.png",
    "K": "/lsr/icons/lightning.gif",
    "L": "/lsr/icons/lightning.gif",
    "M": "/lsr/icons/wind.png",
    "N": "/lsr/icons/wind.png",
    "O": "/lsr/icons/wind.png",
    "P": "/lsr/icons/other.png",
    "Q": "/lsr/icons/tropicalstorm.gif",
    "R": "/vendor/icons/lsr/rain/${magnitude}.png",
    "s": "/lsr/icons/sleet.png",
    "S": "/vendor/icons/lsr/snow/${magnitude}.png",
    "T": "/lsr/icons/tornado.png",
    "U": "/lsr/icons/fire.png",
    "V": "/lsr/icons/avalanche.gif",
    "W": "/lsr/icons/waterspout.png",
    "X": "/lsr/icons/funnelcloud.png",
    "Z": "/lsr/icons/blizzard.png"
};

const lsrStyle = new ol.style.Style({
    image: new ol.style.Icon({ src: lsrLookup['9'] })
});

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

const sbwIntersectionStyle = [new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#551A8B',
        width: 10
    })
})
];

const textStyle = new ol.style.Style({
    image: new ol.style.Circle({
        radius: 10,
        stroke: new ol.style.Stroke({
            color: '#fff'
        }),
        fill: new ol.style.Fill({
            color: '#3399CC'
        })
    }),
    text: new ol.style.Text({
        font: 'bold 11px "Open Sans", "Arial Unicode MS", "sans-serif"',
        fill: new ol.style.Fill({
            color: 'white'
        })
    })
});

function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

function urlencode() {
    // Make our CONFIG object a URI
    const uri = `?year=${CONFIG.year}&phenomena=${CONFIG.phenomena}&significance=${CONFIG.significance}&eventid=${CONFIG.etn}&wfo=${CONFIG.wfo}`;
    return uri;
}

// https://stackoverflow.com/questions/2044616
function selectElementContents(elid) {
    const el = document.getElementById(elid);
    const body = document.body;
    let range = null;
    let sel = null;
    if (document.createRange && window.getSelection) {
        range = document.createRange();
        sel = window.getSelection();
        sel.removeAllRanges();
        try {
            range.selectNodeContents(el);
            sel.addRange(range);
        } catch (e) {
            range.selectNode(el);
            sel.addRange(range);
        }
        document.execCommand("copy");
    } else if (body.createTextRange) {
        range = body.createTextRange();
        range.moveToElementText(el);
        range.select();
        range.execCommand("Copy");
    }
}

function updateHash() {
    // Set the hashlink as per our current CONFIG
    let href = `#${CONFIG.year}-O-NEW-${CONFIG.wfo}-${CONFIG.phenomena}-${CONFIG.significance}-${CONFIG.etn.padLeft(4)}`;
    if (CONFIG.radarProductTime !== null && CONFIG.radarProduct !== null &&
        CONFIG.radar !== null) {
        href += "/" + CONFIG.radar + "-" + CONFIG.radarProduct +
            "-" + CONFIG.radarProductTime.utc().format('YMMDDHHmm');
    }
    window.location.href = href;
}

function parseHash() {
    // See what we have for a hash and update the CONFIG if appropriate
    const tokens = window.location.href.split('#');
    if (tokens.length == 2) {
        const subtokens = tokens[1].split("/");
        const vtectokens = subtokens[0].split("-");
        if (vtectokens.length == 7) {
            CONFIG.year = parseInt(vtectokens[0], 10);
            CONFIG.wfo = text(vtectokens[3]);
            CONFIG.phenomena = text(vtectokens[4]);
            CONFIG.significance = text(vtectokens[5]);
            CONFIG.etn = parseInt(vtectokens[6], 10);
        }
        if (subtokens.length > 1) {
            const radartokens = subtokens[1].split("-");
            if (radartokens.length == 3) {
                CONFIG.radar = text(radartokens[0]);
                CONFIG.radarProduct = text(radartokens[1]);
                CONFIG.radarProductTime = moment.utc(text(radartokens[2]),
                    'YYYYMMDDHHmm');
            }
        }
    }
}

function readHTMLForm() {
    // See what the user has set
    CONFIG.year = parseInt($("#year").val(), 10);
    CONFIG.wfo = text($("#wfo").val());
    CONFIG.phenomena = text($("#phenomena").val());
    CONFIG.significance = text($("#significance").val());
    CONFIG.etn = parseInt($("#etn").val(), 10);

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

function getRADARSource() {
    const dt = radartimes[$("#timeslider").slider("value")];
    if (dt === undefined) {
        return new ol.source.XYZ({
            url: '/cache/tile.py/1.0.0/ridge::USCOMP-N0Q-0/{z}/{x}/{y}.png'
        });
    }
    radarTMSLayer.set('title', '@ ' + dt.format());
    const src = text($("#radarsource").val());
    const prod = text($("#radarproduct").val());
    const url = `/cache/tile.py/1.0.0/ridge::${src}-${prod}-${dt.utc().format('YMMDDHHmm')}/{z}/{x}/{y}.png`;
    return new ol.source.XYZ({
        url
    });
}


function buildMap() {
    element = document.getElementById('popup');
    // Build up the mapping
    radarTMSLayer = new ol.layer.Tile({
        title: 'NEXRAD Base Reflectivity',
        source: getRADARSource()
    });
    productVectorCountyLayer = new ol.layer.Vector({
        title: 'VTEC Product Geometry',
        style: (_feature, _resolution) => {
            return [new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: '#000000',
                    width: 2
                })
            })];
        },
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        })
    });

    sbwIntersectionLayer = new ol.layer.Vector({
        title: 'SBW County Intersection',
        style: sbwIntersectionStyle,
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        })
    });


    productVectorPolygonLayer = new ol.layer.Vector({
        title: 'VTEC Product Polygon',
        style: (feature, _resolution) => {
            sbwStyle[1].getStroke().setColor(sbwLookup[feature.get('phenomena')]);
            return sbwStyle;
        },
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        })
    });

    lsrLayer = new ol.layer.Vector({
        title: 'Local Storm Reports',
        style: (feature, _resolution) => {
            if (feature.get('type') == 'S' || feature.get('type') == 'R') {
                textStyle.getText().setText(feature.get('magnitude').toString());
                return textStyle;
            }
            let url = lsrLookup[feature.get('type')];
            if (url) {
                url = url.replace("${magnitude}", feature.get('magnitude'));
                const icon = new ol.style.Icon({
                    src: url
                });
                lsrStyle.setImage(icon);
            }
            return lsrStyle;
        },
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        })
    });

    olmap = new ol.Map({
        target: 'map',
        view: new ol.View({
            enableRotation: false,
            center: ol.proj.transform([-94.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
        }),
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                source: new ol.source.OSM()
            }),
            radarTMSLayer,
            make_iem_tms('US States', 'usstates', true, ''),
            make_iem_tms('US Counties', 'uscounties', false, ''),
            sbwIntersectionLayer,
            productVectorCountyLayer,
            productVectorPolygonLayer,
            lsrLayer]
    });
    const popup = new ol.Overlay({
        element,
        positioning: 'bottom-center',
        stopEvent: false,
        offset: [0, -5]
    });
    olmap.addOverlay(popup);

    const layerSwitcher = new ol.control.LayerSwitcher();
    olmap.addControl(layerSwitcher);

    olmap.on('moveend', () => {
        // Someday, we will hashlink this too
    });
    // display popup on click
    // TODO support mobile
    olmap.on('click', (evt) => {
        const feature = olmap.forEachFeatureAtPixel(evt.pixel,
            function (feature2) {
                return feature2;
            });
        if (feature) {
            if (feature.get('magnitude') === undefined) return;
            const coordinates = feature.getGeometry().getCoordinates();
            popup.setPosition(coordinates);
            $(element).popover({
                'placement': 'top',
                'html': true,
                'content': lsrFeatureHTML(feature)
            });
            $(element).popover('show');
        } else {
            $(element).popover('destroy');
        }
    });
}
function lsrFeatureHTML(feature) {
    // Make a pretty HTML feature
    const html = ['<div class="panel panel-default">',
        '<div class="panel-heading">',
        '<h3 class="panel-title">Local Storm Report</h3>',
        '</div>',
        '<div class="panel-body">',
        `<strong>Event</strong>: ${feature.get('event')}<br />`,
        `<strong>Location</strong>: ${feature.get('city')}<br />`,
        `<strong>Time</strong>: ${moment.utc(feature.get('utc_valid')).format('MMM Do, h:mm a')}<br />`,
        `<strong>Magnitude</strong>: ${feature.get('magnitude')}<br />`,
        `<strong>Remark</strong>: ${feature.get('remark')}<br />`,
        '</div>',
        '</div>'];
    return html.join('\n');
}

function updateRADARTimeSlider() {
    // operation=list&product=N0Q&radar=USCOMP&start=2012-01-23T08%3A10Z&end=2012-01-23T08%3A45Z
    $.ajax({
        data: {
            radar: $("#radarsource").val(),
            product: $("#radarproduct").val(),
            start: CONFIG.issue.utc().format(),
            end: CONFIG.expire.utc().format(),
            operation: 'list'
        },
        url: '/json/radar',
        method: 'GET',
        dataType: 'json',
        success: (data) => {
            // remove previous options
            radartimes = [];
            $.each(data.scans, (_idx, scan) => {
                radartimes.push(moment.utc(scan.ts));
            });
            if (CONFIG.radarProductTime === null && radartimes.length > 0) {
                CONFIG.radarProducTime = radartimes[0];
            }
            let idx = 0;
            $.each(radartimes, (i, rt) => {
                if (rt.isSame(CONFIG.radarProductTime)) {
                    idx = i;
                };
            });
            $("#timeslider").slider("option", "max", radartimes.length).slider('value', idx);
        }
    });

}

function updateRADARProducts() {
    // operation=products&radar=USCOMP&start=2012-01-23T08%3A10Z
    $.ajax({
        data: {
            radar: $("#radarsource").val(),
            start: (CONFIG.issue !== null) ? CONFIG.issue.utc().format() : '',
            operation: 'products'
        },
        url: '/json/radar',
        method: 'GET',
        dataType: 'json',
        success: (data) => {
            // remove previous options
            $("#radarproduct").empty();
            $.each(data.products, (_idx, product) => {
                $("#radarproduct").append(`<option value="${product.id}">${product.name}</option>`);
            });
            if (CONFIG.radarProduct) {
                $("#radarproduct").val(CONFIG.radarProduct);
            } else {
                CONFIG.radarProduct = text($("#radarproduct").val());
            }
            // step3
            updateRADARTimeSlider();
        }
    });
}

function updateRADARSources() {
    // Use these x, y coordinates to drive our RADAR availablility work
    const center = ol.proj.transform(olmap.getView().getCenter(),
        'EPSG:3857', 'EPSG:4326');
    $.ajax({
        data: {
            lat: center[1],
            lon: center[0],
            start: (CONFIG.issue !== null) ? CONFIG.issue.utc().format() : '',
            operation: 'available'
        },
        url: '/json/radar',
        method: 'GET',
        dataType: 'json',
        success: (data) => {
            // remove previous options
            $("#radarsource").empty();
            $.each(data.radars, (_idx, radar) => {
                $("#radarsource").append(`<option value="${radar.id}">${radar.name}</option>`);
            });
            if (CONFIG.radar) {
                $("#radarsource").val(CONFIG.radar);
            } else {
                CONFIG.radar = text($("#radarsource").val());
            }
            // step2
            updateRADARProducts();
        }
    });
}

function getVTECGeometry() {
    // After the initial metadata is fetched, we get the geometry
    $.ajax({
        data: {
            wfo: CONFIG.wfo,
            phenomena: CONFIG.phenomena,
            significance: CONFIG.significance,
            etn: CONFIG.etn,
            year: CONFIG.year,
            sbw: 0,
            lsrs: 0
        },
        url: "/geojson/vtec_event.py",
        method: "GET",
        dataType: "json",
        success: (geodata) => {
            // The below was way painful on how to get the EPSG 4326 data
            // to load
            const format = new ol.format.GeoJSON({
                featureProjection: "EPSG:3857"
            });
            const vectorSource = new ol.source.Vector({
                features: format.readFeatures(geodata)
            });
            productVectorCountyLayer.setSource(vectorSource);
            const ee = productVectorCountyLayer.getSource().getExtent();
            const xx = (ee[2] + ee[0]) / 2.0;
            const yy = (ee[3] + ee[1]) / 2.0;
            olmap.getView().setCenter([xx, yy]);
            updateRADARSources();
        }
    });
    $.ajax({
        data: {
            wfo: CONFIG.wfo,
            phenomena: CONFIG.phenomena,
            significance: CONFIG.significance,
            etn: CONFIG.etn,
            year: CONFIG.year,
            sbw: 1,
            lsrs: 0
        },
        url: "/geojson/vtec_event.py",
        method: "GET",
        dataType: "json",
        success: (geodata) => {
            // The below was way painful on how to get the EPSG 4326 data
            // to load
            const format = new ol.format.GeoJSON({
                featureProjection: "EPSG:3857"
            });
            const vectorSource = new ol.source.Vector({
                features: format.readFeatures(geodata)
            });
            productVectorPolygonLayer.setSource(vectorSource);
        }
    });
    // Intersection
    $.ajax({
        data: {
            wfo: CONFIG.wfo,
            phenomena: CONFIG.phenomena,
            significance: CONFIG.significance,
            eventid: CONFIG.etn,
            year: CONFIG.year
        },
        url: "/geojson/sbw_county_intersect.php",
        method: "GET",
        dataType: "json",
        success: (geodata) => {
            // The below was way painful on how to get the EPSG 4326 data
            // to load
            const format = new ol.format.GeoJSON({
                featureProjection: "EPSG:3857"
            });
            const vectorSource = new ol.source.Vector({
                features: format.readFeatures(geodata)
            });
            sbwIntersectionLayer.setSource(vectorSource);
        }
    });

    // All LSRs
    $.ajax({
        data: {
            wfo: CONFIG.wfo,
            phenomena: CONFIG.phenomena,
            significance: CONFIG.significance,
            etn: CONFIG.etn,
            year: CONFIG.year,
            sbw: 0,
            lsrs: 1
        },
        url: "/geojson/vtec_event.py",
        method: "GET",
        dataType: "json",
        success: (geodata) => {
            const format = new ol.format.GeoJSON({
                featureProjection: "EPSG:3857"
            });
            const vectorSource = new ol.source.Vector({
                features: format.readFeatures(geodata)
            });
            lsrLayer.setSource(vectorSource);
            lsrTable.clear();
            $.each(geodata.features, (_idx, feat) => {
                const prop = feat.properties;
                lsrTable.row.add(prop);
            });
            lsrTable.draw();
        }
    });
    // SBW LSRs
    $.ajax({
        data: {
            wfo: CONFIG.wfo,
            phenomena: CONFIG.phenomena,
            significance: CONFIG.significance,
            etn: CONFIG.etn,
            year: CONFIG.year,
            sbw: 1,
            lsrs: 1
        },
        url: "/geojson/vtec_event.py",
        method: "GET",
        dataType: "json",
        success: (geodata) => {
            sbwLsrTable.clear();
            $.each(geodata.features, (_idx, feat) => {
                const prop = feat.properties;
                sbwLsrTable.row.add(prop);
            });
            sbwLsrTable.draw();
        }
    });
}

function loadTabs() {
    // OK, lets load up the tab content
    const vstring = `${CONFIG.year}.O.NEW.${CONFIG.wfo}.${CONFIG.phenomena}.${CONFIG.significance}.${CONFIG.etn.padLeft(4)}`;
    const vstring2 = `${CONFIG.year}.${CONFIG.wfo}.${CONFIG.phenomena}.${CONFIG.significance}.${CONFIG.etn.padLeft(4)}`;
    $("#radarmap").html(`<img src="/GIS/radmap.php?layers[]=nexrad&layers[]=sbw&layers[]=sbwh&layers[]=uscounties&vtec=${vstring}" class="img img-responsive">`);
    $("#sbwhistory").html(`<img src="/GIS/sbw-history.php?vtec=${vstring2}" class="img img-responsive">`);

    $("#vtec_label").html(
        `${CONFIG.year} ${text($("#wfo option:selected").text())}
            ${text($("#phenomena option:selected").text())}
            ${text($("#significance option:selected").text())}
            Number ${text($("#etn").val())}`
    );
    $.ajax({
        data: {
            wfo: CONFIG.wfo,
            phenomena: CONFIG.phenomena,
            significance: CONFIG.significance,
            etn: CONFIG.etn,
            year: CONFIG.year
        },
        url: "/json/vtec_event.py",
        method: "GET",
        dataType: "json",
        success: (data) => {
            //$("#textdata").html("<pre>"+ data.report +"</pre>");
            const tabs = $("#textdata ul");
            const tabcontent = $("#textdata div.tab-content");
            tabs.empty();
            tabcontent.empty();
            tabs.append(`<li><a href="#tall" data-toggle="tab">All</a></li>`);
            tabs.append(`<li class="active"><a href="#t0" data-toggle="tab">Issuance</a></li>`);
            tabcontent.append(`<div class="tab-pane" id="tall"><pre>${data.report.text}</pre></div>`);
            tabcontent.append(`<div class="tab-pane active" id="t0"><pre>${data.report.text}</pre></div>`);
            let tidx = 1;
            $.each(data.svs, (_idx, svs) => {
                tabs.append(`<li><a href="#t${tidx}" data-toggle="tab">Update ${tidx}</a></li>`);
                tabcontent.append(`<div class="tab-pane" id="t${tidx}"><pre>${svs.text}</pre></div>`);
                $("#tall").append(`<pre>${svs.text}</pre>`);
                tidx += 1;
            });
            ugcTable.clear();
            $.each(data.ugcs, (_idx, ugc) => {
                ugcTable.row.add([ugc.ugc, ugc.name, ugc.status,
                ugc.utc_product_issue, ugc.utc_issue,
                ugc.utc_init_expire, ugc.utc_expire]);
            });
            ugcTable.draw();
            CONFIG.issue = moment.utc(data.utc_issue);
            CONFIG.expire = moment.utc(data.utc_expire);
            getVTECGeometry();
        }
    });

    $.ajax({
        data: {
            wfo: CONFIG.wfo,
            phenomena: CONFIG.phenomena,
            significance: CONFIG.significance,
            year: CONFIG.year
        },
        url: "/json/vtec_events.py",
        method: "GET",
        dataType: "json",
        success: (data) => {
            eventTable.clear();
            $.each(data.events, (_idx, vtec) => {
                eventTable.row.add([vtec.eventid, vtec.product_issue, vtec.issue,
                vtec.init_expire, vtec.expire, vtec.area, vtec.locations, vtec.fcster]);
            });
            eventTable.draw();
        }
    });
    updateHash();
    // Set the active tab to 'Event Info' if we are on the first tab
    if ($("#thetabs .active > a").attr("href") == "#help") {
        $("#event_tab").click();
    }
}
function remarkformat(d) {
    // `d` is the original data object for the row
    return `<div style="margin-left: 10px;"><strong>Remark:</strong> ${d.remark}</div>`;
}
function makeLSRTable(div) {
    const table = $(`#${div}`).DataTable({
        select: "single",
        "columns": [
            {
                "className": 'details-control',
                "orderable": false,
                "data": null,
                "defaultContent": '',
                "render": () => {
                    return '<i class="fa fa-plus-square" aria-hidden="true"></i>';
                },
                width: "15px"
            },
            { "data": "utc_valid" },
            { "data": "event" },
            { "data": "magnitude" },
            { "data": "city" },
            { "data": "county" },
            { "data": "remark", visible: false }
        ],
        "order": [[1, 'asc']]
    });
    // Add event listener for opening and closing details
    $(`#${div} tbody`).on('click', 'td.details-control', function () { // this
        const tr = $(this).closest('tr');
        const tdi = tr.find("i.fa");
        const row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
            tdi.first().removeClass('fa-minus-square');
            tdi.first().addClass('fa-plus-square');
        }
        else {
            // Open this row
            row.child(remarkformat(row.data())).show();
            tr.addClass('shown');
            tdi.first().removeClass('fa-plus-square');
            tdi.first().addClass('fa-minus-square');
        }
    });

    table.on("user-select", (e, _dt, _type, cell, _originalEvent) => {
        if ($(cell.node()).hasClass("details-control")) {
            e.preventDefault();
        }
    });
    return table;
}

function buildUI() {
    // build the UI components
    let html = "";
    $.each(iemdata.wfos, (_idx, arr) => {
        html += "<option value=\"" + arr[0] + "\">[" + arr[0] + "] " + arr[1] + "</option>";
    });
    $("#wfo").append(html);
    $(`#wfo option[value='${CONFIG.wfo}']`).prop('selected', true)

    html = "";
    $.each(iemdata.vtec_phenomena_dict, (_idx, arr) => {
        html += "<option value=\"" + arr[0] + "\">" + arr[1] + " (" + arr[0] + ")</option>";
    });
    $("#phenomena").append(html);
    $(`#phenomena option[value='${CONFIG.phenomena}']`).prop('selected', true)

    html = "";
    $.each(iemdata.vtec_sig_dict, (_idx, arr) => {
        html += "<option value=\"" + arr[0] + "\">" + arr[1] + " (" + arr[0] + ")</option>";
    });
    $("#significance").append(html);
    $(`#significance option[value='${CONFIG.significance}']`).prop('selected', true)

    html = "";
    for (let year = 1986; year <= (new Date()).getFullYear(); year++) {
        html += "<option value=\"" + year + "\">" + year + "</option>";
    }
    $("#year").append(html);
    $(`#year option[value='${CONFIG.year}']`).prop('selected', true)

    $("#etn").val(CONFIG.etn);
    $("#myform-submit").click(function () { // this
        readHTMLForm();
        loadTabs();
        $(this).blur();
    });
    ugcTable = $("#ugctable").DataTable();
    lsrTable = makeLSRTable("lsrtable");
    sbwLsrTable = makeLSRTable("sbwlsrtable");

    eventTable = $("#eventtable").DataTable();
    $('#eventtable tbody').on('click', 'tr', function () {  // this
        const data = eventTable.row(this).data();
        if (data[0] == CONFIG.etn) return;
        CONFIG.etn = data[0];
        $("#etn").val(CONFIG.etn);
        loadTabs();
        // Switch to the details tab after the click
        $('#event_tab').trigger('click');
    });

    $('a[data-toggle="tab"]').on('shown.bs.tab', (e) => {
        const target = $(e.target).attr("href") // activated tab
        if (target == "#themap") {
            olmap.updateSize();
        }
    });
    $("#radaropacity").slider({
        min: 0,
        max: 100,
        value: 100,
        slide: (_event, ui) => {
            radarTMSLayer.setOpacity(parseInt(ui.value) / 100.);
        }
    });
    $("#timeslider").slider({
        min: 0,
        max: 100,
        change: (_event, ui) => {
            if (radartimes[ui.value] === undefined) {
                return;
            }
            CONFIG.radarProductTime = radartimes[ui.value];
            radarTMSLayer.setSource(getRADARSource());
            updateHash();
            const label = radartimes[ui.value].local().format("D MMM YYYY h:mm A");
            $("#radartime").html(label);
        },
        slide: (_event, ui) => {
            const label = radartimes[ui.value].local().format("D MMM YYYY h:mm A");
            $("#radartime").html(label);
        }
    });
    $("#radarsource").change(() => {
        CONFIG.radar = text($("#radarsource").val());
        updateRADARProducts();
        updateHash();
    });
    $("#radarproduct").change(() => {
        // we can safely(??) assume that radartimes does not update when we
        // switch products
        CONFIG.radarProduct = text($("#radarproduct").val());
        radarTMSLayer.setSource(getRADARSource());
        updateHash();
    });
    $("#lsr_kml_button").click(() => {
        window.location.href = `/kml/sbw_lsrs.php${urlencode()}`;
    });
    $("#warn_kml_button").click(() => {
        window.location.href = `/kml/vtec.php${urlencode()}`;
    });
    $("#ci_kml_button").click(() => {
        window.location.href = `/kml/sbw_county_intersect.php${urlencode()}`;
    });
    $("#gr_button").click(() => {
        window.location.href = `/request/grx/vtec.php${urlencode()}`;
    });

    $("#toolbar-print").click(function () { // this
        $(this).blur();
        const tabid = $("#textdata .nav-tabs li.active a").attr('href');
        // https://stackoverflow.com/questions/33732739
        const divToPrint = $(tabid)[0];
        const newWin = window.open('', 'Print-Window');
        newWin.document.open();
        newWin.document.write(`<html><body onload="window.print()">${divToPrint.innerHTML}</body></html>`);
        newWin.document.close();
        setTimeout(() => { newWin.close(); }, 10);
    });

}

$(() => {
    //onReady
    try {
        parseHash();
    } catch (err) { 
        // Nothing?
    };
    buildUI();
    buildMap();
    loadTabs();
});
