/* global $ */
let station = '_OAX';
let year = new Date().getFullYear();
let j2 = null;
let dt = null;

function zero(val){
    return (val === null) ? "": val;
}
function fetch(){
    $('#datatable tbody').empty();
    $('#datatable tbody').append('<tr><th colspan="5">Querying server, one moment</th></tr>');
    $.get(`/api/1/raobs_by_year.json?station=${station}&year=${year}`).done((j) => {
        if (dt){
            dt.destroy();
        }
        $('#datatable tbody').empty();
        for (let i=0; i < j.data.length; i++){
            const feat = j.data[i];
            const row = ['<tr>',
                `<td>${feat.station}</td>`,
                `<td>${feat.valid}</td>`,
                `<td>${zero(feat.sbcape_jkg)}</td>`,
                `<td>${zero(feat.mucape_jkg)}</td>`,
                `<td>${zero(feat.pwater_mm)}</td>`,
                '</tr>'];
            $('#datatable tbody').append(row.join(''));
        }
        if (j.data.length == 0){
            $('#datatable tbody').append('<tr><th colspan="5">No results were found, sorry!</th></tr>');
        }
        if (dt){
            dt = $("#thetable table").DataTable();
        }
    });
}

$( document ).ready(() => {
    $('#makefancy').click(() => {
        dt = $("#thetable table").DataTable();
    });

    $("select[name='station']").change(function(){ // this
        station = this.value;
        window.location.href = `#${station}:${year}`;
        fetch();
    });
    $("select[name='year']").change(function(){ // this
        year = this.value;
        window.location.href = `#${station}:${year}`;
        fetch();
    });
    
    const tokens = window.location.href.split("#");
    if (tokens.length === 2){
        const tokens2 = tokens[1].split(":");
        if (tokens2.length === 2){
            station = tokens2[0];
            year = tokens2[1];
            $("select[name='station']").val(station);
            $("select[name='year']").val(year);
        }
    }
    fetch();
    
});
