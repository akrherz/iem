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

    $("#myanimation").jsani({
        imageSrcs: $("#imagesrcs li").map((_i, el) => $(el).text()).get(),
        aniWidth: $("#datawindow").width(),
        aniHeight: $("#datawindow").height(),
        initdwell: 200,
        controls: ['stopplay', 'firstframe', 'previous', 'next', 'lastframe', 'looprock', 'slow', 'fast', 'zoom'],
        last_frame_pause: 8,
        first_frame_pause: 1,
        frame_pause: '0:5, 3:6'
    });

    $(".iemselect2").select2();

    // check if archive=yes is set in the URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('archive')) {
        setTimeout("document.myform.submit()", 300000);
    }
});
