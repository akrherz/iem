var stateSelect;
var ugcSelect;
var mapwidget1;
var mapwidget2;
var table1;
var table2;
var table2IsByPoint = true;
var hashlinkUGC;
var edate;
var sdate;
var BACKEND_SPS_BYPOINT = '/json/sps_by_point.py';

function updateMarkerPosition(lon, lat) {
    var latLng = new google.maps.LatLng(parseFloat(lat), parseFloat(lon))
    $("#lat").val(latLng.lat().toFixed(4));
    $("#lon").val(latLng.lng().toFixed(4));
    window.location.href = "#bypoint/" +
        latLng.lng().toFixed(4) + "/" + latLng.lat().toFixed(4);
    if (mapwidget1){
        mapwidget1.map.setCenter(latLng);
    }
    updateTable();
}

function updateTable(){
    $("#table1title").text(`SPS for Point: ${$("#lon").val()}E ${$("#lat").val()}N`);
    // Do what we need to for table 1
    $.ajax({
        data: {
            lat: $("#lat").val(),
            lon: $("#lon").val(),
            sdate: $.datepicker.formatDate("yy/mm/dd", sdate.datepicker("getDate")),
            edate: $.datepicker.formatDate("yy/mm/dd", edate.datepicker("getDate"))
        },
        url: BACKEND_SPS_BYPOINT,
        dataType: "json",
        method: "GET",
        success: function(data){
            table1.clear();
            $.map(data.data, function(row){
                var uri = '<a href="' + row.uri +'" target="_blank">View Text</a>';
                table1.row.add(
                    [uri, row.issue, row.landspout, row.waterspout,
                     row.max_hail_size, row.max_wind_gust]);
            });
            table1.draw();
        }
    });
}

function buildUI(){
    // Export Buttons
    $(".iemtool").click(function(){
        var btn = $(this);
        var url = BACKEND_SPS_BYPOINT;
        var params = {
            fmt: (btn.data("opt") == "csv") ? "csv" : "xlsx",
            lat: $("#lat").val(),
            lon: $("#lon").val(),
            sdate: $.datepicker.formatDate("yy/mm/dd", sdate.datepicker("getDate")),
            edate: $.datepicker.formatDate("yy/mm/dd", edate.datepicker("getDate"))
        };
        window.location = url + "?" + $.param(params);
    });
    // Tables
    table1 = $("#table1").DataTable({
        "language": {
            "emptyTable": "Drag marker on map to auto-populate this table"
        }
    });

    // Date pickers
    sdate = $("input[name='sdate']").datepicker({
        dateFormat:"mm/dd/yy",
        altFormat:"yy/mm/dd",
        minDate: new Date(1986, 0, 1),
        maxDate: new Date(),
        onClose: function(){
            updateTable2ByUGC();
        }
    });
    sdate.datepicker("setDate", new Date(1986, 0, 1));
    edate = $("input[name='edate']").datepicker({
        dateFormat:"mm/dd/yy",
        altFormat:"yy/mm/dd",
        minDate: new Date(1986, 0, 1),
        defaultDate: +1,
        onClose: function(){
            updateTable2ByUGC();
        }
    });
    edate.datepicker("setDate", +1);
    // Manual Point Entry
    $("#manualpt").click(function(){
        var la = $("#lat").val();
        var lo = $("#lon").val();
        if (la == "" || lo == ""){
            return;
        }
        var latlng = new google.maps.LatLng(parseFloat(la), parseFloat(lo))
        mapwidget1.marker.setPosition(latlng);
        updateMarkerPosition(lo, la);
    });

};

function initialize() {
    buildUI();
    var default_lon = -93.653;
    var default_lat = 41.53;

    // Do the anchor tag linking, please
    var tokens = window.location.href.split("#");
    if (tokens.length == 2){
        var tokens2 = tokens[1].split("/");
        if (tokens2.length == 2){
            if (tokens2[0] == 'byugc'){
                var aTag = $("a[name='byugc']");
                $('html,body').animate({scrollTop: aTag.offset().top},'slow');
                hashlinkUGC = tokens2[1];
                stateSelect.val(tokens2[1].substr(0, 2)).trigger("change");
                stateSelect.val(tokens2[1].substr(0, 2)).trigger({
                    type: "select2:select",
                    params: {
                        data: {
                            id: tokens2[1].substr(0, 2)
                        }
                    }
                });
            }
        }
        if (tokens2.length == 3){
            if (tokens2[0] == 'bypoint'){
                default_lat = tokens2[2];
                default_lon = tokens2[1];
                updateMarkerPosition(default_lon, default_lat);
            }
            if (tokens2[0] == 'eventsbypoint'){
                default_lat = tokens2[2];
                default_lon = tokens2[1];
                updateMarkerPosition2(default_lon, default_lat);
            }
        }
    }

    mapwidget1 = new MapMarkerWidget("map", default_lon, default_lat);
    mapwidget1.register(updateMarkerPosition);

}

// Onload handler to fire off the app.
google.maps.event.addDomListener(window, 'load', initialize);
