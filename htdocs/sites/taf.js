document.addEventListener('DOMContentLoaded', () => {
    const rawtext = document.getElementById('rawtext');
    if (rawtext) {
        const station3 = rawtext.dataset.station3;
        if (station3) {
            fetch(`/cgi-bin/afos/retrieve.py?pil=TAF${station3}&fmt=html`)
                .then(response => response.text())
                .then(data => {
                    rawtext.innerHTML = data;
                })
                .catch(error => {
                    rawtext.innerHTML = `<p>Error loading TAF data: ${error}</p>`;
                });
        }
    }

    const afd = document.getElementById('afd');
    if (afd) {
        const wfo = afd.dataset.wfo;
        if (wfo) {
            fetch(`/cgi-bin/afos/retrieve.py?pil=AFD${wfo}&fmt=html&aviation_afd=1`)
                .then(response => response.text())
                .then(data => {
                    afd.innerHTML = data;
                })
                .catch(error => {
                    afd.innerHTML = `<p>Error loading AFD data: ${error}</p>`;
                });
        }
    }

    const metars = document.getElementById('metars');
    if (metars) {
        const station4 = metars.dataset.station4;
        if (station4) {
            fetch(
                `/cgi-bin/request/asos.py?station=${station4}&hours=4&nometa=1&data=metar&report_type=3,4`
            )
                .then(response => response.text())
                .then(data => {
                    metars.innerHTML = `<pre>${data}</pre>`;
                })
                .catch(error => {
                    metars.innerHTML = `<pre>Error loading METAR data: ${error}</pre>`;
                });
        }
    }
});
