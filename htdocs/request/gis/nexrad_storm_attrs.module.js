document.addEventListener('DOMContentLoaded', () => {
    const stationSelect = document.querySelector('select[name="station"]');
    const histImage = document.getElementById('histimage');

    if (stationSelect) {
        stationSelect.addEventListener('change', () => {
            const nexrad = stationSelect.value;
            if (histImage) {
                histImage.src = `/pickup/nexrad_attrs/${nexrad}_histogram.png`;
            }
            window.location.hash = nexrad;
        });
    }

    const tokens = window.location.href.split('#');
    if (tokens.length === 2 && tokens[1].length === 3) {
        if (histImage) {
            histImage.src = `/pickup/nexrad_attrs/${tokens[1]}_histogram.png`;
        }
    }
});