/* global $ */
function go() {
    document.getElementById("mycharts").scrollIntoView();
}
$(document).ready(() => {
    $("#gogogo").click(() => {
        go();
    });
    // Check the current URL and if it contains a year parameter, we scroll
    // to the charts.
    if (window.location.href.indexOf("year") > -1) {
        go();
    }

});