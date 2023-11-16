let stateSelect = null;
let stateSelect3 = null;
let ugcSelect = null;
let mapwidget1 = null;
let mapwidget2 = null;
let table1 = null;
let table2 = null;
let table3 = null;
let table2IsByPoint = true;
let hashlinkUGC = null;
let edate = null;
let sdate = null;
let edate1 = null;
let sdate1 = null;
const BACKEND_EVENTS_BYPOINT = '/json/vtec_events_bypoint.py';
const BACKEND_EVENTS_BYUGC = '/json/vtec_events_byugc.py';
const BACKEND_SBW_BYPOINT = '/json/sbw_by_point.py';
const BACKEND_EVENTS = "/json/vtec_events.py";
const BACKEND_EVENTS_BYSTATE = "/json/vtec_events_bystate.py";
const DATE_FMT = "yy-mm-dd";

const states = [["AL", "Alabama"], ["AK", "Alaska"], ["AZ", "Arizona"],
        ["AR", "Arkansas"], ["CA", "California"], ["CO", "Colorado"],
        ["CT", "Connecticut"], ["DE", "Delaware"], ["FL", "Florida"],
        ["GA", "Georgia"], ["HI", "Hawaii"], ["ID", "Idaho"],
        ["IL", "Illinois"], ["IN", "Indiana"], ["IA", "Iowa"],
        ["KS", "Kansas"], ["KY", "Kentucky"], ["LA", "Louisiana"],
        ["ME", "Maine"], ["MD", "Maryland"], ["MA", "Massachusetts"],
        ["MI", "Michigan"], ["MN", "Minnesota"], ["MS", "Mississippi"],
        ["MO", "Missouri"], ["MT", "Montana"], ["NE", "Nebraska"],
        ["NV", "Nevada"], ["NH", "New Hampshire"], ["NJ", "New Jersey"],
        ["NM", "New Mexico"], ["NY", "New York"], ["NC", "North Carolina"],
        ["ND", "North Dakota"], ["OH", "Ohio"], ["OK", "Oklahoma"],
        ["OR", "Oregon"], ["PA", "Pennsylvania"], ["RI", "Rhode Island"],
        ["SC", "South Carolina"], ["SD", "South Dakota"], ["TN", "Tennessee"],
        ["TX", "Texas"], ["UT", "Utah"], ["VT", "Vermont"], ["VA", "Virginia"],
        ["WA", "Washington"], ["WV", "West Virginia"], ["WI", "Wisconsin"],
        ["WY", "Wyoming"],
        ["AM", "Atlantic Ocean AM"],
        ["AN", "Atlantic Ocean AN"],
        ["AS", "AS"],
        ["DC", "Distict of Columbia"],
        ["GM", "Gulf of Mexico"],
        ["GU", "Guam"],
        ["LC", "Lake St. Clair"],
        ["LE", "Lake Erie"],
        ["LH", "Lake Huron"],
        ["LM", "Lake Michigan"],
        ["LO", "Lake Ontario"],
        ["LS", "Lake Superior"],
        ["PH", "Hawaii PH Zones"],
        ["PK", "Alaska PK Zones"],
        ["PM", "Zones PM"],
        ["PR", "Puerto Rico"],
        ["PS", "Zones PS"],
        ["PZ", "Pacific Ocean PZ"],
        ["SL", "St. Lawrence River"]
];
var google = window.google || {};  // skipcq: JS-0239

function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

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
function updateMarkerPosition2(lon, lat) {
    const latLng = new google.maps.LatLng(parseFloat(lat), parseFloat(lon))
    $("#lat2").val(latLng.lat().toFixed(4));
    $("#lon2").val(latLng.lng().toFixed(4));
    window.location.href = `#eventsbypoint/${latLng.lng().toFixed(4)}/${latLng.lat().toFixed(4)}`;
    if (mapwidget2){
        mapwidget2.map.setCenter(latLng);
    }
    updateTable2ByPoint();
}
function updateTable(){
    $("#table1title").text(`Storm Based Warnings for Point: ${$("#lon").val()}E ${$("#lat").val()}N`);
    // Do what we need to for table 1
    $.ajax({
        data: {
            lat: $("#lat").val(),
            lon: $("#lon").val(),
            sdate: $.datepicker.formatDate(DATE_FMT, sdate1.datepicker("getDate")),
            edate: $.datepicker.formatDate(DATE_FMT, edate1.datepicker("getDate"))
        },
        url: BACKEND_SBW_BYPOINT,
        dataType: "json",
        method: "GET",
        success: (data) => {
            table1.clear();
            $.map(data.sbws, (row) => {
                const uri = `<a href="${row.url}" target="_blank">${row.eventid}</a>`;
                table1.row.add(
                    [uri, row.ph_name, row.sig_name, row.issue,
                    row.expire, row.issue_hailtag, row.issue_windtag,
                    row.issue_tornadotag, row.issue_damagetag]);
            });
            table1.draw();
        }
    });
}

function updateTable2ByUGC(){
    table2IsByPoint = false;
    $("#table2title").text(`Events for UGC: ${ugcSelect.val()}`);
    // Do what we need to for table 2
    $.ajax({
        data: {
            ugc: ugcSelect.val(),
            sdate: $.datepicker.formatDate(DATE_FMT, sdate.datepicker("getDate")),
            edate: $.datepicker.formatDate(DATE_FMT, edate.datepicker("getDate"))
        },
        url: BACKEND_EVENTS_BYUGC,
        dataType: "json",
        method: "GET",
        success: (data) => {
            table2.clear();
            $.map(data.events, (row) => {
                const uri = `<a href="${row.url}" target="_blank">${row.eventid}</a>`;
                table2.row.add(
                    [uri, row.ph_name, row.sig_name, row.issue, row.expire]);
            });
            table2.draw();
        }
    });
}

function updateTable2ByPoint(){
    table2IsByPoint = true;
    $("#table2title").text(`Events for Point: ${$("#lon2").val()}E ${$("#lat2").val()}N`);
    // Do what we need to for table 2
    $.ajax({
        data: {
            lat: $("#lat2").val(),
            lon: $("#lon2").val(),
            sdate: $.datepicker.formatDate(DATE_FMT, sdate.datepicker("getDate")),
            edate: $.datepicker.formatDate(DATE_FMT, edate.datepicker("getDate"))
        },
        url: BACKEND_EVENTS_BYPOINT,
        dataType: "json",
        method: "GET",
        success: (data) => {
            table2.clear();
            $.map(data.events, (row) => {
                const uri = `<a href="${row.url}" target="_blank">${row.eventid}</a>`;
                table2.row.add(
                    [uri, row.ph_name, row.sig_name, row.issue, row.expire]);
            });
            table2.draw();
        }
    });
}

function updateTable3(){
    // get currently selected by3 radio button
    const by = text($("input[name='by3']:checked").val());
    const datum = (by == "state") ? text(stateSelect3.val()) : text($("#wfo3").val());
    const year = text($("#year3").val());
    const ph = text($("#ph3").val());
    const sig = text($("#sig3").val());
    window.location.href = `#list/${by}/${datum}/${year}/${ph}/${sig}`;
    $("#table3title").text(`Events for ${by} ${datum} in ${year}`);
    // Do what we need to for table 3
    $.ajax({
        data: {
            wfo: $("#wfo3").val(),
            state: stateSelect3.val(),
            year: year,
            phenomena: ph,
            significance: sig
        },
        url: (by == "wfo") ? BACKEND_EVENTS: BACKEND_EVENTS_BYSTATE,
        dataType: "json",
        method: "GET",
        success: (data) => {
            table3.clear();
            $.map(data.events, (row) => {
                const uri = `<a href="${row.uri}" target="_blank">${row.phenomena}.${row.significance}.${row.eventid}</a>`;
                table3.row.add(
                    [uri, row.wfo, row.locations, row.issue, row.expire]);
            });
            table3.draw();
        }
    });
}


function buildUI(){
    // Export Buttons
    $(".iemtool").click(function(){ // this
        const btn = $(this);
        let url = BACKEND_SBW_BYPOINT;
        var params = {
            fmt: (btn.data("opt") == "csv") ? "csv" : "xlsx",
            lat: $("#lat").val(),
            lon: $("#lon").val(),
            sdate: $.datepicker.formatDate(DATE_FMT, sdate1.datepicker("getDate")),
            edate: $.datepicker.formatDate(DATE_FMT, edate1.datepicker("getDate"))
        };
        if (btn.data("table") == "2"){
            url = BACKEND_EVENTS_BYUGC;
            params.ugc = ugcSelect.val();
            params.sdate = $.datepicker.formatDate(DATE_FMT, sdate.datepicker("getDate"));
            params.edate = $.datepicker.formatDate(DATE_FMT, edate.datepicker("getDate"));
            if (table2IsByPoint) {
                url = BACKEND_EVENTS_BYPOINT;
                params.lon = $("#lon2").val();
                params.lat = $("#lat2").val();
            }
        }
        if (btn.data("table") == "3"){
            const by = $("input[name='by3']:checked").val();
            url = (by == "state") ? BACKEND_EVENTS_BYSTATE: BACKEND_EVENTS;
            params = {
                fmt: (btn.data("opt") == "csv") ? "csv" : "xlsx",
                wfo: $("#wfo3").val(),
                state: stateSelect3.val(),
                year: $("#year3").val(),
                phenomena: $("#ph3").val(),
                significance: $("#sig3").val()
            };
        }
        window.location = `${url}?${$.param(params)}`;
    });
    // Tables
    table1 = $("#table1").DataTable({
        "language": {
            "emptyTable": "Drag marker on map to auto-populate this table"
        }
    });
    table2 = $("#table2").DataTable({
        "language": {
            "emptyTable": "Drag marker on map or select UGC to auto-populate this table"
        }
    });
    table3 = $("#table3").DataTable({
        "language": {
            "emptyTable": "Select options to auto-populate this table"
        }
    });
    // Date pickers
    sdate = $("input[name='sdate']").datepicker({
        dateFormat:"mm/dd/yy",
        altFormat:DATE_FMT,
        minDate: new Date(1986, 0, 1),
        maxDate: new Date(),
        onClose: () => {
            updateTable2ByUGC();
        }
    });
    sdate.datepicker("setDate", new Date(1986, 0, 1));
    edate = $("input[name='edate']").datepicker({
        dateFormat:"mm/dd/yy",
        altFormat:DATE_FMT,
        minDate: new Date(1986, 0, 1),
        defaultDate: +1,
        onClose: () => {
            updateTable2ByUGC();
        }
    });
    edate.datepicker("setDate", +1);
    sdate1 = $("input[name='sdate1']").datepicker({
        dateFormat:"mm/dd/yy",
        altFormat:DATE_FMT,
        minDate: new Date(2002, 0, 1),
        maxDate: new Date(),
        onClose: () => {
            updateTable();
        }
    });
    sdate1.datepicker("setDate", new Date(2002, 0, 1));
    edate1 = $("input[name='edate1']").datepicker({
        dateFormat:"mm/dd/yy",
        altFormat:DATE_FMT,
        minDate: new Date(2002, 0, 1),
        defaultDate: +1,
        onClose: () => {
            updateTable();
        }
    });
    edate1.datepicker("setDate", +1);

    // select boxes
    const data = $.map(states, (obj) => {
        const ee = {};
        ee.id = obj[0];
        ee.text = obj[1];
        return ee;
    });
    stateSelect3 = $("#state3").select2({
        placeholder: "Select a geography/state",
        data: data
    });
    stateSelect3.val('').trigger("change");
    stateSelect = $("#state").select2({
        placeholder: "Select a geography/state",
        data: data
    });
    stateSelect.val('').trigger("change");
    stateSelect.on("select2:select", (e) => {
        const state = e.params.data.id;
        // Load the ugcSelect box
        $.ajax({
            data: {
                state
            },
            url: "/json/state_ugc.php",
            method: "GET",
            dataType: "json",
            success: (data2) => {
                ugcSelect.empty();
                $.map(data2.ugcs, (obj) => {
                    const extra = (obj.ugc.substr(2, 1) === "Z") ? " (Zone)": "";
                    ugcSelect.append(new Option("[" + obj.ugc + "] "+ obj.name + extra, obj.ugc, false, false));
                });
                ugcSelect.val('').trigger("change");
                if (hashlinkUGC){
                    ugcSelect.val(hashlinkUGC).trigger("change");
                    hashlinkUGC = null;
                    updateTable2ByUGC();
                }
            }
        });
    });
    ugcSelect = $("select[name='ugc']").select2({
        placeholder: "Select County/Zone after Selecting Geography"
    });
    ugcSelect.on("select2:select", (e) => {
        const ugc = e.params.data.id;
        window.location.href = `#byugc/${ugc}`;
        updateTable2ByUGC();
    });
    // Manual Point Entry
    $("#manualpt").click(() => {
        const la = $("#lat").val();
        const lo = $("#lon").val();
        if (la == "" || lo == ""){
            return;
        }
        const latlng = new google.maps.LatLng(parseFloat(la), parseFloat(lo))
        mapwidget1.marker.setPosition(latlng);
        updateMarkerPosition(lo, la);
    });
    $("#manualpt2").click(() => {
        const la = $("#lat2").val();
        const lo = $("#lon2").val();
        if (la == "" || lo == ""){
            return;
        }
        const latlng = new google.maps.LatLng(parseFloat(la), parseFloat(lo))
        mapwidget2.marker.setPosition(latlng);
        updateMarkerPosition2(lo, la);
    });
    $("#button3").click(() => {
        updateTable3();
    });
    // Populate wfos select with iemdata.wfos data
    const wfos = $.map(iemdata.wfos, (obj) => {
        const ee = {};
        ee.id = obj[0];
        ee.text = `[${obj[0]}] ${obj[1]}`;
        return ee;
    });
    $("select[name='wfo']").select2({
        placeholder: "Select a WFO",
        data: wfos
    });
    const ph = $.map(iemdata.vtec_phenomena, (obj) => {
        const ee = {};
        ee.id = obj[0];
        ee.text = obj[1];
        return ee;
    });
    $("select[name='ph']").select2({
        placeholder: "Select a Phenomena",
        data: ph
    });
    const sig = $.map(iemdata.vtec_significance, (obj) => {
        const ee = {};
        ee.id = obj[0];
        ee.text = obj[1];
        return ee;
    });
    $("select[name='sig']").select2({
        placeholder: "Select a Phenomena",
        data: sig
    });
    // populate year3 select with values from 1986 to current year
    const year3 = $("select[name='year']");
    const currentYear = new Date().getFullYear();
    for (let i = 1986; i <= currentYear; i++){
        year3.append(new Option(i, i, false, false));
    }
};

function _load() {
    buildUI();
    let default_lon = -93.653;
    let default_lat = 41.53;

    // Do the anchor tag linking, please
    const tokens = window.location.href.split("#");
    if (tokens.length == 2){
        const tokens2 = tokens[1].split("/");
        if (tokens2.length == 2){
            if (tokens2[0] == 'byugc'){
                const aTag = $("a[name='byugc']");
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
                default_lat = text(tokens2[2]);
                default_lon = text(tokens2[1]);
                updateMarkerPosition(default_lon, default_lat);
            }
            if (tokens2[0] == 'eventsbypoint'){
                default_lat = text(tokens2[2]);
                default_lon = text(tokens2[1]);
                updateMarkerPosition2(default_lon, default_lat);
            }
        }
        if (tokens2.length == 6){
            const aTag = $("a[name='list']");
            $('html,body').animate({scrollTop: aTag.offset().top},'slow');
            const by = text(tokens2[1]);
            const datum = text(tokens2[2]);
            const year = text(tokens2[3]);
            const ph = text(tokens2[4]);
            const sig = text(tokens2[5]);
            $("input[name='by3'][value='"+by+"']").prop("checked", true);
            $("#year3").val(year);
            $("#ph3").val(ph);
            $("#sig3").val(sig);
            if (by == "state"){
                stateSelect3.val(datum).trigger("change");
            } else {
                $("#wfo3").val(datum);
            }
            updateTable3();
        }
    }

    mapwidget1 = new MapMarkerWidget("map", default_lon, default_lat);
    mapwidget1.register(updateMarkerPosition);

    mapwidget2 = new MapMarkerWidget("map2", default_lon, default_lat);
    mapwidget2.register(updateMarkerPosition2);

}
