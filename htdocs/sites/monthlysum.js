function go() {
    const myChartsElement = document.getElementById('mycharts');
    if (myChartsElement) {
        myChartsElement.scrollIntoView();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const gogogoBtn = document.getElementById('gogogo');
    if (gogogoBtn) {
        gogogoBtn.addEventListener('click', () => {
            go();
        });
    }

    // Check the current URL and if it contains a year parameter, we scroll
    // to the charts.
    if (window.location.href.indexOf('year') > -1) {
        go();
    }
});
