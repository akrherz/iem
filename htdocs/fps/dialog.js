var dockPosition = 0;

// https://stackoverflow.com/questions/48712560
function addButtons(dlg) {
    // Define Buttons
    var $close = dlg.find(".ui-dialog-titlebar-close");
    var $min = $("<button>", {
        class: "ui-button ui-corner-all ui-widget ui-button-icon-only ui-window-minimize",
        type: "button",
        title: "Minimize"
    }).insertBefore($close);
    $min.data("isMin", false);
    $("<span>", {
        class: "ui-button-icon ui-icon ui-icon-minusthick"
    }).appendTo($min);
    $("<span>", {
        class: "ui-button-icon-space"
    }).html(" ").appendTo($min);
    var $max = $("<button>", {
        class: "ui-button ui-corner-all ui-widget ui-button-icon-only ui-window-maximize",
        type: "button",
        title: "Maximize"
    }).insertBefore($close);
    $max.data("isMax", false);
    $("<span>", {
        class: "ui-button-icon ui-icon ui-icon-plusthick"
    }).appendTo($max);
    $("<span>", {
        class: "ui-button-icon-space"
    }).html(" ").appendTo($max);
    // Define Function
    $min.click(function (e) {
        if ($min.data("isMin") === false) {
            $min.data("original-pos", dlg.position());
            $min.data("original-size", {
                width: dlg.width(),
                height: dlg.height()
            });
            $min.data("isMin", true);
            dlg.animate({
                height: '40px',
                top: $(window).height() - 50 - dockPosition,
                left: 0
            }, 200);
            dockPosition += 50;
            dlg.find(".ui-dialog-content").hide();
        } else {
            $min.data("isMin", false);
            dlg.find(".ui-dialog-content").show();
            dlg.animate({
                height: $min.data("original-size").height + "px",
                top: $min.data("original-pos").top + "px",
                left: $min.data("original-pos").left + "px"
            }, 200);
            dockPosition -= 50;
        }
    });
    $max.click(function (e) {
        if ($max.data("isMax") === false) {
            $max.data("original-pos", dlg.position());
            $max.data("original-size", {
                width: dlg.width(),
                height: dlg.height()
            });
            $max.data("isMax", true);
            dlg.animate({
                height: $(window).height() + "px",
                width: $(window).width() - 20 + "px",
                top: 0,
                left: 0
            }, 200);
        } else {
            $max.data("isMax", false);
            dlg.animate({
                height: $max.data("original-size").height + "px",
                width: $max.data("original-size").width + "px",
                top: $max.data("original-pos").top + "px",
                left: $max.data("original-pos").top + "px"
            }, 200);
        }
    });
}

function windowFactory(initdiv, classID){
    var dlg = $(initdiv).dialog({
        draggable: true,
        autoOpen: true,
        dialogClass: classID,
        classes: {
            "ui-dialog": "ui-window-options",
            "ui-dialog-titlebar": "ui-window-bar"
        },
        modal: false,
        responsive: true,
        width: 800,
        height: 500,
        close: function() {
            $(this).dialog('destroy').remove();
        },
        resizeStop: function() {
            // Causes charts to fit their container
            $(Highcharts.charts).each(function(i,chart){
                var height = chart.renderTo.clientHeight; 
                var width = chart.renderTo.clientWidth; 
                chart.setSize(width, height); 
            });
            // Fixes responsive troubles with boostrap?
            $(this).find(".col-md-3").height(this.clientHeight);
        }
    });
    
    addButtons($("."+classID));    
    $(dlg).dialog("open");
}
