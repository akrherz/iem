let report = 'snowdepth';

function fetch() {
    $('#datatable tbody').empty();
    $('#datatable tbody').append('<tr><th colspan="5">Querying server, one moment</th></tr>');
    $.get(`/geojson/recent_metar.py?q=${report}`).done((j) => {
        $('#datatable tbody').empty();
        for (let i = 0; i < j.features.length; i++) {
            const feat = j.features[i];
            const row = ['<tr>',
                `<td>${feat.properties.station}</td>`,
                `<td>${feat.properties.network}</td>`,
                `<td>${feat.properties.valid}</td>`,
                `<td>${feat.properties.value}</td>`,
                `<td>${feat.properties.metar}</td>`,
                '</tr>'];
            $('#datatable tbody').append(row.join(''));
        }
        if (j.features.length === 0) {
            $('#datatable tbody').append('<tr><th colspan="5">No results were found, sorry!</th></tr>');
        }
    });
}

$(document).ready(() => {
    $("#report").change(function () { // this
        report = this.value;
        window.location.href = `#${report}`;
        fetch();
    });

    const tokens = window.location.href.split("#");
    if (tokens.length === 2) {
        report = tokens[1];
        $('#report').val(report);
    }
    fetch();
});
