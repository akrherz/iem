/* global MapMarkerWidget */
let mapwidget1 = null;
let table1 = null;
let edate = null;
let sdate = null;
const BACKEND_SPS_BYPOINT = '/json/sps_by_point.py';


function updateMarkerPosition(lon, lat) {
    const latLng = new google.maps.LatLng(parseFloat(lat), parseFloat(lon))
    $("#lat").val(latLng.lat().toFixed(4));
    $("#lon").val(latLng.lng().toFixed(4));
    window.location.href = `#bypoint/${latLng.lng().toFixed(4)}/${latLng.lat().toFixed(4)}`;
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
        success: (data) => {
            table1.clear();
            $.map(data.data, (row) => {
                const uri = `<a href="${row.uri}" target="_blank">View Text</a>`;
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
    $(".iemtool").click(function(){ // this
        const btn = $(this);
        const url = BACKEND_SPS_BYPOINT;
        const params = {
            fmt: (btn.data("opt") == "csv") ? "csv" : "xlsx",
            lat: $("#lat").val(),
            lon: $("#lon").val(),
            sdate: $.datepicker.formatDate("yy/mm/dd", sdate.datepicker("getDate")),
            edate: $.datepicker.formatDate("yy/mm/dd", edate.datepicker("getDate"))
        };
        window.location = `${url}?${$.param(params)}`;
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
        onClose: () => {
            updateTable();
        }
    });
    sdate.datepicker("setDate", new Date(1986, 0, 1));
    edate = $("input[name='edate']").datepicker({
        dateFormat:"mm/dd/yy",
        altFormat:"yy/mm/dd",
        minDate: new Date(1986, 0, 1),
        defaultDate: +1,
        onClose: () => {
            updateTable();
        }
    });
    edate.datepicker("setDate", +1);
    // Manual Point Entry
    $("#manualpt").click(function(){
        const la = $("#lat").val();
        const lo = $("#lon").val();
        if (la == "" || lo == ""){
            return;
        }
        const latlng = new google.maps.LatLng(parseFloat(la), parseFloat(lo))
        mapwidget1.marker.setPosition(latlng);
        updateMarkerPosition(lo, la);
    });

};
// Callback from Google Load
// eslint-disable-next-line no-unused-vars
function _gcb() {
    buildUI();
    let default_lon = -93.653;
    let default_lat = 41.53;

    // Do the anchor tag linking, please
    const tokens = window.location.href.split("#");
    if (tokens.length == 2){
        const tokens2 = tokens[1].split("/");
        if (tokens2.length == 3){
            if (tokens2[0] == 'bypoint'){
                default_lat = tokens2[2];
                default_lon = tokens2[1];
                updateMarkerPosition(default_lon, default_lat);
            }
        }
    }

    mapwidget1 = new MapMarkerWidget("map", default_lon, default_lat);
    mapwidget1.register(updateMarkerPosition);
}
