// Data structure to hold the pest data
var pestData = {};
pestData.seedcorn_maggot = {'gddbase': 39, 'gddceil': 84};
pestData.alfalfa_weevil = {'gddbase': 48, 'gddceil': 90};
pestData.soybean_aphid = {'gddbase': 50, 'gddceil': 90};
pestData.common_stalk_borer = {'gddbase': 41, 'gddceil': 90};
pestData.japanese_beetle = {'gddbase': 50, 'gddceil': 90};

function hideImageLoad(){{
    $('#willload').css('display', 'none');
}}

function updateImage(){
    showProgressBar();
    var pest = $("select[name='pest']").val()

    // Hide all the pinfo containers
    $('.pinfo').css('display', 'none');

    // Show this pest's pinfo container
    $('#' + pest).css('display', 'block');
    var opts = pestData[pest];
    var sdate = $("#sdate").val();
    var edate = $("#edate").val();
    var imgurl = "/plotting/auto/plot/97/d:sector::sector:IA::var:gdd_sum::" +
    "gddbase:" + opts.gddbase + "::gddceil:" + opts.gddceil + "::date1:" + sdate + "::usdm:no::" +
    "date2:" + edate + "::p:contour::cmap:RdYlBu::cmap_r=on::c:yes::_r:43.png";
    $("#theimage").attr("src", imgurl);

    // Update the web browser URL
    var url = "/topics/pests/?pest=" + pest + "&sdate=" + sdate;
    // is edate_off checked?
    if (! $("#edate_off").is(':checked')){
        url += "&edate=" + edate;
    }
    window.history.pushState({}, "", url);
    
}

function showProgressBar(){
    $('#willload').css('display', 'block');
    var timing = 0;
    var progressBar = setInterval(function (){{
            if (timing >= 10 ||
                $('#willload').css('display') == 'none'){{
                    clearInterval(progressBar);
            }}
            var width = (timing / 10) * 100.;
            $("#timingbar").css('width', width +'%').attr('aria-valuenow', width);
            timing = timing + 0.2;
    }}, 200);
}

function setupUI(){
    $('#theimage').on('load', function(){{
        hideImageLoad();
    }});
    $('#theimage').on('error', function(){{
        hideImageLoad();
    }});
    // The image may be cached and return to the user before this javascript
    // is hit, so we do a check to see if it is indeed loaded now
    if ($("#theimage").get(0) && $("#theimage").get(0).complete){{
        hideImageLoad();
    }}

    $("#sdate").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        onSelect: function(dateText, inst){
            updateImage();
        }
    });
    $("#edate").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        onSelect: function(dateText, inst){
            updateImage();
        }
    });
}

$(document).ready(function() {
    updateImage();
    showProgressBar();
    setupUI();
});
