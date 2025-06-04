let report = 'snowdepth';

function fetchData() {
    const tableBody = document.querySelector('#datatable tbody');
    if (!tableBody) return;

    tableBody.innerHTML = '<tr><th colspan="5">Querying server, one moment</th></tr>';

    fetch(`/geojson/recent_metar.py?q=${report}`)
        .then(response => response.json())
        .then(j => {
            tableBody.innerHTML = '';
            for (let i = 0; i < j.features.length; i++) {
                const feat = j.features[i];
                const row = [
                    '<tr>',
                    `<td>${feat.properties.station}</td>`,
                    `<td>${feat.properties.network}</td>`,
                    `<td>${feat.properties.valid}</td>`,
                    `<td>${feat.properties.value}</td>`,
                    `<td>${feat.properties.metar}</td>`,
                    '</tr>',
                ];
                tableBody.insertAdjacentHTML('beforeend', row.join(''));
            }
            if (j.features.length === 0) {
                tableBody.innerHTML = '<tr><th colspan="5">No results were found, sorry!</th></tr>';
            }
        })
        .catch(error => {
            tableBody.innerHTML = `<tr><th colspan="5">Error loading data ${error.message}</th></tr>`;
        });
}

document.addEventListener('DOMContentLoaded', () => {
    const reportSelect = document.getElementById('report');
    if (reportSelect && reportSelect instanceof HTMLSelectElement) {
        reportSelect.addEventListener('change', function () {
            report = this.value;
            window.location.href = `#${report}`;
            fetchData();
        });
    }

    const tokens = window.location.href.split('#');
    if (tokens.length === 2) {
        report = tokens[1];
        if (reportSelect && reportSelect instanceof HTMLSelectElement) {
            reportSelect.value = report;
        }
    }
    fetchData();
});
