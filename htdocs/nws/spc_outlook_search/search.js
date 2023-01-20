
var marker;
var map;
var google = window.google || {}; // skipcq: JS-0239


function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

function workflow(){
    const lon = parseFloat($("#lon").val());
    const lat = parseFloat($("#lat").val());
    if (isNaN(lon) || isNaN(lat)){
        return;
    }
    doOutlook(lon, lat);
    doMCD(lon, lat);
    doWatch(lon, lat);
    updateTableTitle(lon, lat);
}

function buildUI(){
    $("#manualpt").click(function(){
        const la = $("#lat").val();
        const lo = $("#lon").val();
        const latlng = new google.maps.LatLng(parseFloat(la), parseFloat(lo));
        marker.setPosition(latlng);
        updateMarkerPosition(latlng);
    });
    $('#last').change(function() {
        workflow();
    });
    $('#events').change(function() {
        workflow();

    });
    $('input[type=radio][name=day]').change(function() {
        workflow();

    });
    $('input[type=radio][name=cat]').change(function() {
        workflow();

    });
}

function updateTableTitle(lon, lat){
    const txt = `Lon: ${lon} Lat: ${lat}`;
    $('#watches').find("caption").text(`Convective Watches for ${txt}`);
    $('#outlooks').find("caption").text(`Convective Outlooks for ${txt}`);
    $('#mcds').find("caption").text(`Mesoscale Convective Discussions for ${txt}`);
}

function updateMarkerPosition(latLng) {
    $("#lat").val(latLng.lat().toFixed(4));
    $("#lon").val(latLng.lng().toFixed(4));
    window.location.href = `#bypoint/${latLng.lng().toFixed(4)}/${latLng.lat().toFixed(4)}`;
    map.setCenter(latLng);
    workflow();
}

function doOutlook(lon, lat){
    const last = $('#last').is(":checked") ? $("#events").val(): '0';
    const day = text($("input[name='day']:checked").val());
    const cat = text($("input[name='cat']:checked").val());
    let tbody = $("#outlooks tbody").empty();
    $("#outlook_spinner").show();
    const jsonurl = `/json/spcoutlook.py?lon=${lon}&lat=${lat}&last=${last}&day=${day}&cat=${cat}`;
    $("#outlooks_link").attr('href', jsonurl);
    $.ajax({
        dataType: "json",
        url: jsonurl,
        success(data){
            $("#outlook_spinner").hide();
            $.each(data.outlooks, function(index, ol){
                tbody.append(`<tr><td>${ol.day}</td><td>${ol.threshold}</td><td>${ol.utc_product_issue}</td><td>${ol.utc_issue}</td><td>${ol.utc_expire}</td></tr>`)
            });
            if (data.outlooks.length == 0){
                tbody.append(`<tr><td colspan="5">No Results Found!</td></tr>`);
            }
            }
    });
}
function doMCD(lon, lat){
    let tbody = $("#mcds tbody").empty();
    $("#mcd_spinner").show();
    let jsonurl = `/json/spcmcd.py?lon=${lon}&lat=${lat}`;
    $("#mcds_link").attr('href', jsonurl);
    $.ajax({
        dataType: "json",
        url: jsonurl,
        success(data){
            $("#mcd_spinner").hide();
            $.each(data.mcds, function(index, mcd){
                tbody.append(`<tr><td><a href="${mcd.spcurl}" target="_blank">${mcd.year} ${mcd.product_num}</a></td><td>${mcd.utc_issue}</td><td>${mcd.utc_expire}</td></tr>`)
            });
            if (data.mcds.length == 0){
                tbody.append(`<tr><td colspan="3">No Results Found!</td></tr>`);
            }
            }
    });
}

function doWatch(lon, lat){
    let tbody = $("#watches tbody").empty();
    $("#watch_spinner").show();
    const jsonurl = `/json/spcwatch.py?lon=${lon}&lat=${lat}`;
    $("#watches_link").attr('href', jsonurl);
    $.ajax({
        dataType: "json",
        url: jsonurl,
        success(data){
            $("#watch_spinner").hide();
            $.each(data.features, function(index, feature){
                var watch = feature.properties;
                tbody.append(`<tr><td><a href="${watch.spcurl}" target="_blank">${watch.year} ${watch.number}</a></td><td>${watch.type}</td><td>${watch.issue}</td><td>${watch.expire}</td></tr>`)
            });
            if (data.features.length == 0){
                tbody.append(`<tr><td colspan="4">No Results Found!</td></tr>`);
            }
            }
    });
}
function initialize() { // skipcq: JS-0128
    buildUI();
    var latLng = new google.maps.LatLng(41.53, -93.653);
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 5,
        center: latLng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    marker = new google.maps.Marker({
        position: latLng,
        title: 'Point A',
        map,
        draggable: true
    });

    google.maps.event.addListener(marker, 'dragend', () => {
            updateMarkerPosition(marker.getPosition());
        });

    // Do the anchor tag linking, please
    var tokens = window.location.href.split("#");
    if (tokens.length == 2){
        var tokens2 = tokens[1].split("/");
        if (tokens2.length == 3){
            if (tokens2[0] == 'bypoint'){
                var latlng = new google.maps.LatLng(text(tokens2[2]), text(tokens2[1]));
                marker.setPosition(latlng);
                updateMarkerPosition(latlng);
            }
        }
    }

}

// Onload handler to fire off the app.
// addEventListener('load', initialize);
