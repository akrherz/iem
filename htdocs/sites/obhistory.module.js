// ES Module
import $ from '/js/jquery.module.js';
let station = null;
let network = null;
let metar_show = false;
let madis_show = false;
let month = null;
let day = null;
let year = null;

function updateButton(label){
    const btn = $(`#${label}`);
    let uri = `${window.location.origin}${window.location.pathname}`+
    `?station=${station}&network=${network}&year=${btn.data("year")}`+
    `&month=${btn.data("month")}&day=${btn.data("day")}`;
    if (metar_show){
        uri += "&metar=1";
    }
    if (madis_show){
        uri += "&madis=1";
    }
    btn.attr("href", uri);
}
function updateURI(){
    // Add CGI vars that control the METAR and MADIS show buttons
    let uri = `${window.location.origin}${window.location.pathname}?`+
        `station=${station}&network=${network}&year=${year}`+
        `&month=${month}&day=${day}`;
    if (metar_show){
        uri += "&metar=1";
    }
    if (madis_show){
        uri += "&madis=1";
    }
    window.history.pushState({}, "", uri);
    updateButton("prevbutton");
    updateButton("nextbutton");
}
function showMETAR(){
    $(".metar").css("display", "table-row");
    if (madis_show){
        $(".hfmetar").css("display", "table-row");
    }
    $("#metar_toggle").html("<i class=\"fa fa-minus\"></i> Hide METARs");
}
function toggleMETAR(){
    if (metar_show){
        // Hide both METARs and HFMETARs
        $(".metar").css("display", "none");
        $(".hfmetar").css("display", "none");
        $("#metar_toggle").html("<i class=\"fa fa-plus\"></i> Show METARs");
        $("#hmetar").val("0");
    } else{
        // show
        showMETAR();
        $("#hmetar").val("1");
    }
    metar_show = !metar_show;
    updateURI();
}
function showMADIS(){
    $("tr[data-madis=1]").css("display", "table-row");
    if (metar_show){
        $(".hfmetar").css("display", "table-row");
    }
    $("#madis_toggle").html("<i class=\"fa fa-minus\"></i> Hide High Frequency MADIS");
}
function toggleMADIS(){
    if (madis_show){
        // Hide MADIS
        $("tr[data-madis=1]").css("display", "none");
        $(".hfmetar").css("display", "none");
        $("#madis_toggle").html("<i class=\"fa fa-plus\"></i> Show High Frequency MADIS");
        $("#hmadis").val("0");
    } else {
        // Show
        showMADIS();
        $("#hmadis").val("1");
    }
    madis_show = !madis_show;
    updateURI();
}
$().ready(() => {
    station = $("#station").val();
    network = $("#network").val();
    metar_show = $("#hmetar").val() === "1";
    madis_show = $("#hmadis").val() === "1";
    month = $("#theform").data("month");
    day = $("#theform").data("day");
    year = $("#theform").data("year");
    $("#metar_toggle").click(toggleMETAR);
    $("#madis_toggle").click(toggleMADIS);
    if (metar_show) {
        showMETAR();
    }
    if (madis_show) {
        showMADIS();
    }
});
