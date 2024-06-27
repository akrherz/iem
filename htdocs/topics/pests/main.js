/* global $ */
var pestData = {};
pestData.seedcorn_maggot = { 'gddbase': 39, 'gddceil': 84 };
pestData.alfalfa_weevil = { 'gddbase': 48, 'gddceil': 90 };
pestData.soybean_aphid = { 'gddbase': 50, 'gddceil': 90 };
pestData.common_stalk_borer = { 'gddbase': 41, 'gddceil': 90 };
pestData.japanese_beetle = { 'gddbase': 50, 'gddceil': 90 };
pestData.western_bean_cutworm = { 'gddbase': 38, 'gddceil': 75 };
pestData.european_corn_borer = { 'gddbase': 50, 'gddceil': 86 };

function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

function hideImageLoad() {
    $('#willload').css('display', 'none');
    const url = $("#theimage").attr("src").replace(".png", "");
    $("#thedata").html(
        `<p>Download point data: <a href="${url}.txt" class="btn btn-primary">` +
        '<i class="fa fa-table"></i> As CSV</a> &nbsp;' +
        `<a href="${url}.xlsx" class="btn btn-primary">` +
        '<i class="fa fa-table"></i> As Excel</a></p>');
}
function rectify_start_date(pest) {
    let month = (pest === "western_bean_cutworm") ? "03": "01"; // le sigh
    let day = "01";
    if (pest === "european_corn_borer") {
        month = "05";
        day = "20";
    }
    // Get the year from the edate datepicker
    const edate = text($("#edate").val());
    const year = parseInt(edate.substring(0, 4), 10);
    $("#sdate").val(`${year}-${month}-${day}`);
}

function updateStationForecast() {
    const station = text($("select[name='station']").val());
    const pest = text($("select[name='pest']").val());
    const opts = pestData[pest];
    const sdate = text($("#sdate").val());
    const edate = text($("#edate").val());
    const url = `/json/climodat_dd.py?station=${station}&gddbase=${opts.gddbase}&gddceil=${opts.gddceil}&sdate=${sdate}&edate=${edate}`;
    $.get(url, function (data) {
        $("#station_date").html(data.sdate + " to " + data.edate);
        $("#station_accum").html(data.accum.toFixed(1));

        $("#station_gfs_date").html(data.gfs_sdate + " to " + data.gfs_edate);
        $("#station_gfs_accum").html("+" + data.gfs_accum.toFixed(1));
        $("#station_gfs_total").html((data.accum + data.gfs_accum).toFixed(1));

        $("#station_ndfd_date").html(`${data.ndfd_sdate} to ${data.ndfd_edate}`);
        $("#station_ndfd_accum").html("+" + data.ndfd_accum.toFixed(1));
        $("#station_ndfd_total").html((data.accum + data.ndfd_accum).toFixed(1));
    });
}

function updateImage() {
    showProgressBar();
    $("#theimage").attr("src", "/images/pixel.gif");
    const station = text($("select[name='station']").val());
    const pest = text($("select[name='pest']").val());

    // Hide all the pinfo containers
    $('.pinfo').css('display', 'none');

    // Show this pest's pinfo container
    $('#' + pest).css('display', 'block');
    const opts = pestData[pest];
    const sdate = text($("#sdate").val());
    const edate = text($("#edate").val());
    let state = text($("select[name='network']").val());
    state = (state !== undefined) ? state.substring(0, 2) : "IA";
    const imgurl = `/plotting/auto/plot/97/d:sector::sector:${state}::var:gdd_sum::gddbase:${opts.gddbase}::gddceil:${opts.gddceil}::date1:${sdate}::usdm:no::date2:${edate}::p:contour::cmap:RdYlBu_r::c:yes::_r:43.png`;
    $("#theimage").attr("src", imgurl);

    // Update the web browser URL
    let url = `/topics/pests/?state=${state}&pest=${pest}&sdate=${sdate}&station=${station}`;
    // is edate_off checked?
    if (!$("#edate_off").is(':checked')) {
        url += "&edate=" + edate;
    }
    window.history.pushState({}, "", url);
    updateStationForecast();
}

function showProgressBar() {
    $('#willload').css('display', 'block');
    let timing = 0;
    const progressBar = setInterval(() => {
        if (timing >= 10 ||
            $('#willload').css('display') === 'none') {
            clearInterval(progressBar);
        }
        const width = (timing / 10) * 100.0;
        $("#timingbar").css('width', `${width}%`).attr('aria-valuenow', width);
        timing = timing + 0.2;
    }, 200);
}

function setupUI() {
    $('#theimage').on('load', () => {
        hideImageLoad();
    });
    $('#theimage').on('error', () => {
        hideImageLoad();
    });
    // The image may be cached and return to the user before this javascript
    // is hit, so we do a check to see if it is indeed loaded now
    if ($("#theimage").get(0) && $("#theimage").get(0).complete) {
        hideImageLoad();
    }

    $("#edate").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        minDate: new Date(1893, 0, 1),
        maxDate: 0,
        onSelect(_dateText, _inst) {
            updateImage();
        }
    });
    $("#sdate").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        minDate: new Date(1893, 0, 1),
        maxDate: 0,
        onSelect(_dateText, _inst) {
            updateImage();
        }
    });

    $("select[name='station']").change(() => {
        updateStationForecast();
    });
}
function updatePest() { // skipcq: JS-0128
    const pest = text($("select[name='pest']").val());
    rectify_start_date(pest);
    updateImage();
}

$(document).ready(() => {
    updateImage();
    updateStationForecast();
    showProgressBar();
    setupUI();
});
