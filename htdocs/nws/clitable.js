/* global $ */
$(document).ready(() => {
    $('#makefancy').click(() => {
        $("#thetable").DataTable();
    });

    $("#makerecords").click(function () {
        const val = $(this).data("toggle");
        if (val === 0) {
            $("#thetable [data-record=0]").hide();
            $("#makerecordslabel").text("Show All Rows");
            $(this).data("toggle", 1);
        } else {
            $("#makerecordslabel").text("Show Rows with Records");
            $(this).data("toggle", 0);
            $("#thetable tr").show();
        }
    });
});
