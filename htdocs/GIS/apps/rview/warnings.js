
import $ from '/js/jquery.module.js';

export function showControl(layerName) {
    const oldval = document.getElementById(layerName).style.display;
    setLayerDisplay("layers-control", 'none');
    setLayerDisplay("locations-control", 'none');
    setLayerDisplay("time-control", 'none');
    setLayerDisplay("options-control", 'none');
    if (oldval === 'none') {
        setLayerDisplay(layerName, 'block');
    }
}

export function setLayerDisplay(layerName, dd) {
    const ww = document.getElementById(layerName);
    ww.style.display = dd;
}

$(document).ready(() => {
    $("#datawindow button").click((event) => {
        const layer = $(event.target).data("control");
        showControl(`${layer}-control`);
    });
});
