// Data structure to hold the pest data
var pestData = {};
pestData.seedcorn_maggot = { 'gddbase': 39, 'gddceil': 84 };
pestData.alfalfa_weevil = { 'gddbase': 48, 'gddceil': 90 };
pestData.soybean_aphid = { 'gddbase': 50, 'gddceil': 90 };
pestData.common_stalk_borer = { 'gddbase': 41, 'gddceil': 90 };
pestData.japanese_beetle = { 'gddbase': 50, 'gddceil': 90 };

function hideImageLoad() {
    {
        $('#willload').css('display', 'none');
        var url = $("#theimage").attr("src").replace(".png", "");
        $("#thedata").html(
            '<p>Download point data: <a href="' + url + '.txt" class="btn btn-primary">' +
            '<i class="fa fa-table"></i> As CSV</a> &nbsp;' +
            '<a href="' + url + '.xlsx" class="btn btn-primary">' +
            '<i class="fa fa-table"></i> As Excel</a></p>');
    }
}

function updateStationForecast() {
    var station = $("select[name='station']").val();
    var pest = $("select[name='pest']").val()
    var opts = pestData[pest];
    var sdate = $("#sdate").val();
    var edate = $("#edate").val();
    var url = "/json/climodat_dd.py?station=" + station + "&gddbase=" + opts.gddbase +
        "&gddceil=" + opts.gddceil + "&sdate=" + sdate + "&edate=" + edate;
    $.get(url, function (data) {
        $("#station_date").html(data.sdate + " to " + data.edate);
        $("#station_accum").html(data.accum.toFixed(1));

        $("#station_gfs_date").html(data.gfs_sdate + " to " + data.gfs_edate);
        $("#station_gfs_accum").html("+" + data.gfs_accum.toFixed(1));
        $("#station_gfs_total").html((data.accum + data.gfs_accum).toFixed(1));

        $("#station_ndfd_date").html(data.ndfd_sdate + " to " + data.ndfd_edate);
        $("#station_ndfd_accum").html("+" + data.ndfd_accum.toFixed(1));
        $("#station_ndfd_total").html((data.accum + data.ndfd_accum).toFixed(1));
    });
}

function updateImage() {
    showProgressBar();
    $("#theimage").attr("src", "/images/pixel.gif");
    var station = $("select[name='station']").val();
    var pest = $("select[name='pest']").val();

    // Hide all the pinfo containers
    $('.pinfo').css('display', 'none');

    // Show this pest's pinfo container
    $('#' + pest).css('display', 'block');
    var opts = pestData[pest];
    var sdate = $("#sdate").val();
    var edate = $("#edate").val();
    var state = $("select[name='state']").val();
    state = (state !== undefined) ? state.substring(0, 2) : "IA";
    var imgurl = "/plotting/auto/plot/97/d:sector::sector:" + state + "::var:gdd_sum::" +
        "gddbase:" + opts.gddbase + "::gddceil:" + opts.gddceil + "::date1:" + sdate + "::usdm:no::" +
        "date2:" + edate + "::p:contour::cmap:RdYlBu_r::c:yes::_r:43.png";
    $("#theimage").attr("src", imgurl);

    // Update the web browser URL
    var url = "/topics/pests/?state=" + state + "&pest=" + pest + "&sdate="
        + sdate + "&station=" + station;
    // is edate_off checked?
    if (!$("#edate_off").is(':checked')) {
        url += "&edate=" + edate;
    }
    window.history.pushState({}, "", url);

}

function showProgressBar() {
    $('#willload').css('display', 'block');
    var timing = 0;
    var progressBar = setInterval(function () {
        {
            if (timing >= 10 ||
                $('#willload').css('display') == 'none') {
                    {
                        clearInterval(progressBar);
                    }
            }
            var width = (timing / 10) * 100.;
            $("#timingbar").css('width', width + '%').attr('aria-valuenow', width);
            timing = timing + 0.2;
        }
    }, 200);
}

function setupUI() {
    $('#theimage').on('load', function () {
        {
            hideImageLoad();
        }
    });
    $('#theimage').on('error', function () {
        {
            hideImageLoad();
        }
    });
    // The image may be cached and return to the user before this javascript
    // is hit, so we do a check to see if it is indeed loaded now
    if ($("#theimage").get(0) && $("#theimage").get(0).complete) {
        {
            hideImageLoad();
        }
    }

    $("#sdate").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        onSelect: function (dateText, inst) {
            updateImage();
        }
    });
    $("#edate").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        onSelect: function (dateText, inst) {
            updateImage();
        }
    });

    $("select[name='station']").change(function () {
        updateStationForecast();
    });
}

$(document).ready(function () {
    updateImage();
    updateStationForecast();
    showProgressBar();
    setupUI();
});
