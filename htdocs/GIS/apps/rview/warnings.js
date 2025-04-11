/* global $ */

function showControl(layerName) {
    const oldval = document.getElementById(layerName).style.display;
    setLayerDisplay("layers-control", 'none');
    setLayerDisplay("locations-control", 'none');
    setLayerDisplay("time-control", 'none');
    setLayerDisplay("options-control", 'none');
    if (oldval === 'none') {
        setLayerDisplay(layerName, 'block');
    }
}

function setLayerDisplay(layerName, dd) {
    const ww = document.getElementById(layerName);
    ww.style.display = dd;
}

$(document).ready(() => {
    $("#datawindow button").click((event) => {
        const layer = $(event.target).data("control");
        showControl(`${layer}-control`);
    });

    // check if archive=yes is set in the URL
    const urlParams = new URLSearchParams(window.location.search);
    if (! urlParams.has('archive')) {
        setTimeout(() => { document.myform.submit(); }, 300000);
    }
});
