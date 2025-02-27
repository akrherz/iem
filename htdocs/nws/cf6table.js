/* global $ */
$(document).ready(() => {
    $(".iemselect2").select2();
    $('#makefancy').click(() => {
        $("#thetable").DataTable();
    });
});
