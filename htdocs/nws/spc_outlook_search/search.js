/* global $, ol, olSelectLonLat */
let marker = null;

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

function workflow() {
    const lon = parseFloat($("#lon").val());
    const lat = parseFloat($("#lat").val());
    if (isNaN(lon) || isNaN(lat)) {
        return;
    }
    doOutlook(lon, lat);
    doMCD(lon, lat);
    doWatch(lon, lat);
    updateTableTitle(lon, lat);
}

function updateURLParams(params = {}) {
    const url = new URL(window.location.href);
    // Update provided parameters
    Object.entries(params).forEach(([key, value]) => {
        if (value !== null) {
            url.searchParams.set(key, value);
        }
    });
    window.history.replaceState({}, '', url);
}

function updateMarkerPosition(lon, lat) {
    updateURLParams({lon, lat});
    workflow();
}

function buildUI() {
    $("#manualpt").click(() => {
        const la = parseFloat($("#lat").val());
        const lo = parseFloat($("#lon").val());
        marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lo, la])));
        updateMarkerPosition(lo, la);
    });
    $('#last').change(() => {
        workflow();
    });
    $('#events').change(() => {
        workflow();
    });
    $('input[type=radio][name=day]').change(() => {
        const day = $("input[name='day']:checked").val();
        updateURLParams({day});
        workflow();
    });
    $('input[type=radio][name=cat]').change(() => {
        const cat = $("input[name='cat']:checked").val();
        updateURLParams({cat});
        workflow();
    });
}

function updateTableTitle(lon, lat) {
    const txt = `Lon: ${lon} Lat: ${lat} Day: ${$("input[name='day']:checked").val()} Category: ${$("input[name='cat']:checked").val()}`;
    $('#watches').find("caption").text(`Convective Watches for ${txt}`);
    $('#outlooks').find("caption").text(`Convective Outlooks for ${txt}`);
    $('#mcds').find("caption").text(`Mesoscale Convective Discussions for ${txt}`);
}

function doOutlook(lon, lat) {
    const last = $('#last').is(":checked") ? escapeHTML($("#events").val()) : '0';
    const day = escapeHTML($("input[name='day']:checked").val());
    const cat = escapeHTML($("input[name='cat']:checked").val());
    const tbody = $("#outlooks tbody").empty();
    $("#outlook_spinner").show();
    const jsonurl = `/json/spcoutlook.py?lon=${lon}&lat=${lat}&last=${last}&day=${day}&cat=${cat}`;
    $("#outlooks_link").attr('href', jsonurl);
    const excelurl = `/json/spcoutlook.py?lon=${lon}&lat=${lat}&last=${last}&day=${day}&cat=${cat}&fmt=excel`;
    $("#outlooks_excel").attr('href', excelurl);
    const csvurl = `/json/spcoutlook.py?lon=${lon}&lat=${lat}&last=${last}&day=${day}&cat=${cat}&fmt=csv`;
    $("#outlooks_csv").attr('href', csvurl);
    $.ajax({
        dataType: "json",
        url: jsonurl,
        success(data) {
            $("#outlook_spinner").hide();
            $.each(data.outlooks, (_index, ol) => {
                tbody.append(`<tr><td>${ol.day}</td><td>${ol.threshold}</td><td>${ol.utc_product_issue}</td><td>${ol.utc_issue}</td><td>${ol.utc_expire}</td></tr>`)
            });
            if (data.outlooks.length === 0) {
                tbody.append('<tr><td colspan="5">No Results Found!</td></tr>');
            }
        }
    });
}
function doMCD(lon, lat) {
    const tbody = $("#mcds tbody").empty();
    $("#mcd_spinner").show();
    const jsonurl = `/json/spcmcd.py?lon=${lon}&lat=${lat}`;
    $("#mcds_link").attr('href', jsonurl);
    const excelurl = `/json/spcmcd.py?lon=${lon}&lat=${lat}&fmt=excel`;
    $("#mcds_excel").attr('href', excelurl);
    const csvurl = `/json/spcmcd.py?lon=${lon}&lat=${lat}&fmt=csv`;
    $("#mcds_csv").attr('href', csvurl);
    $.ajax({
        dataType: "json",
        url: jsonurl,
        success(data) {
            $("#mcd_spinner").hide();
            $.each(data.mcds, (_index, mcd) => {

                tbody.append(
                    `<tr><td><a href="${mcd.spcurl}" target="_blank">${mcd.year} ` +
                    `${mcd.product_num}</a></td>` +
                    `<td>${mcd.utc_issue}</td>` +
                    `<td>${mcd.utc_expire}</td>` +
                    `<td>${mcd.watch_confidence || ''}</td>` +
                    `<td>${mcd.concerning}</td>` +
                    `<td>${mcd.most_prob_tornado}</td>` +
                    `<td>${mcd.most_prob_hail}</td>` +
                    `<td>${mcd.most_prob_gust}</td>` +
                    '</tr>');
            });
            if (data.mcds.length === 0) {
                tbody.append('<tr><td colspan="6">No Results Found!</td></tr>');
            }
        }
    });
}

function doWatch(lon, lat) {
    const tbody = $("#watches tbody").empty();
    $("#watch_spinner").show();
    const jsonurl = `/json/spcwatch.py?lon=${lon}&lat=${lat}`;
    $("#watches_link").attr('href', jsonurl);
    const excelurl = `/json/spcwatch.py?lon=${lon}&lat=${lat}&fmt=excel`;
    $("#watches_excel").attr('href', excelurl);
    const csvurl = `/json/spcwatch.py?lon=${lon}&lat=${lat}&fmt=csv`;
    $("#watches_csv").attr('href', csvurl);
    $.ajax({
        dataType: "json",
        url: jsonurl,
        success(data) {
            $("#watch_spinner").hide();
            $.each(data.features, (_index, feature) => {
                const watch = feature.properties;
                tbody.append(
                    `<tr><td><a href="${watch.spcurl}" target="_blank">${watch.year} `+
                    `${watch.number}</a></td><td>${watch.type}</td><td>${watch.issue}</td>`+
                    `<td>${watch.expire}</td><td>${watch.max_hail_size}</td>`+
                    `<td>${watch.max_wind_gust_knots}</td>`+
                    `<td>${watch.is_pds}</td></tr>`)
            });
            if (data.features.length === 0) {
                tbody.append('<tr><td colspan="4">No Results Found!</td></tr>');
            }
        }
    });
}

function convertLegacyHashLink() {
    // Do the anchor tag linking, please
    const tokens = window.location.href.split("#");
    if (tokens.length === 2) {
        const tokens2 = tokens[1].split("/");
        if (tokens2.length === 3) {
            if (tokens2[0] === 'bypoint') {
                const lon = parseFloat(tokens2[1]);
                const lat = parseFloat(tokens2[2]);
                marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])));
                updateMarkerPosition(lon, lat);
            }
        }
        // Remove the hash from the URL
        window.history.replaceState({}, '', tokens[0]);
    }
}

function readURLParams(){
    // Read the URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const lon = parseFloat(urlParams.get('lon'));
    const lat = parseFloat(urlParams.get('lat'));
    if (!isNaN(lon) && !isNaN(lat)) {
        marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])));
        updateMarkerPosition(lon, lat);
    }
    // Set the day selection if provided in URL
    const day = urlParams.get('day');
    if (day) {
        $(`input[name='day'][value='${escapeHTML(day)}']`).prop('checked', true);
    }
    // Set the category selection if provided in URL
    const cat = urlParams.get('cat');
    if (cat) {
        $(`input[name='cat'][value='${escapeHTML(cat)}']`).prop('checked', true);
    }
    if (day || cat) {
        workflow();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    buildUI();
    const res = olSelectLonLat("map", updateMarkerPosition);
    marker = res.marker;

    // Legacy URLs used anchor tags, which we want to migrate to url parameters
    convertLegacyHashLink();
    readURLParams();

});
