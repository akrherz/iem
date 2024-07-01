
/* global $, ol */
let marker = null;
let map = null;

function text(str) {
    // XSS
    return $("<p>").text(str).html();
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

function buildUI() {
    $("#manualpt").click(() => {
        const la = parseFloat($("#lat").val());
        const lo = parseFloat($("#lon").val());
        marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lo, la])));
        updateMarkerPosition(lon, lat);
    });
    $('#last').change(() => {
        workflow();
    });
    $('#events').change(() => {
        workflow();

    });
    $('input[type=radio][name=day]').change(() => {
        workflow();

    });
    $('input[type=radio][name=cat]').change(() => {
        workflow();

    });
}

function updateTableTitle(lon, lat) {
    const txt = `Lon: ${lon} Lat: ${lat}`;
    $('#watches').find("caption").text(`Convective Watches for ${txt}`);
    $('#outlooks').find("caption").text(`Convective Outlooks for ${txt}`);
    $('#mcds').find("caption").text(`Mesoscale Convective Discussions for ${txt}`);
}

function updateMarkerPosition(lon, lat) {
    $("#lat").val(lat.toFixed(4));
    $("#lon").val(lon.toFixed(4));
    window.location.href = `#bypoint/${lon.toFixed(4)}/${lat.toFixed(4)}`;
    workflow();
}

function doOutlook(lon, lat) {
    const last = $('#last').is(":checked") ? text($("#events").val()) : '0';
    const day = text($("input[name='day']:checked").val());
    const cat = text($("input[name='cat']:checked").val());
    const tbody = $("#outlooks tbody").empty();
    $("#outlook_spinner").show();
    const jsonurl = `/json/spcoutlook.py?lon=${lon}&lat=${lat}&last=${last}&day=${day}&cat=${cat}`;
    $("#outlooks_link").attr('href', jsonurl);
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
                    '</tr>');
            });
            if (data.mcds.length === 0) {
                tbody.append('<tr><td colspan="3">No Results Found!</td></tr>');
            }
        }
    });
}

function doWatch(lon, lat) {
    const tbody = $("#watches tbody").empty();
    $("#watch_spinner").show();
    const jsonurl = `/json/spcwatch.py?lon=${lon}&lat=${lat}`;
    $("#watches_link").attr('href', jsonurl);
    $.ajax({
        dataType: "json",
        url: jsonurl,
        success(data) {
            $("#watch_spinner").hide();
            $.each(data.features, (_index, feature) => {
                const watch = feature.properties;
                tbody.append(`<tr><td><a href="${watch.spcurl}" target="_blank">${watch.year} ${watch.number}</a></td><td>${watch.type}</td><td>${watch.issue}</td><td>${watch.expire}</td></tr>`)
            });
            if (data.features.length === 0) {
                tbody.append('<tr><td colspan="4">No Results Found!</td></tr>');
            }
        }
    });
}

$(document).ready(() => {
    buildUI();
    let res = olSelectLonLat("map", -93.653, 41.53, updateMarkerPosition);
    map = res.map;
    marker = res.marker;

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
    }

});
