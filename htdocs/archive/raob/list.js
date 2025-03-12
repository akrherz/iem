/* global $ */
let station = '_OAX';
let year = new Date().getFullYear();
let dt = null;
let sortby = "-";  // Sentinal value for no sort
let asc = "desc";
let filter_year = true;  // Not implemented as too much data for JSON

function rnd(val, precision){
    return (val === null) ? "": val.toFixed(precision);
}
function fetch(){
    let href = `#${station}`;
    const ascbool = (asc === "asc") ? "true": "false";
    let service = `/api/1/raobs_by_year.json?station=${station}&asc=${ascbool}`;
    let caption = `RAOB Data for ${station}`;
    if (sortby !== "-"){
        caption = `${caption} sorted by ${sortby} ${asc} (Top 100)`;
        href += `:${sortby}:${asc}`;
        service += `&sortby=${sortby}`;
    } else if (filter_year){
        caption = `${caption} for ${year}`;
        href += `:${year}:${asc}`;
        service += `&year=${year}`;
    }
    window.location.href = href;
    $('#datatable tbody').empty();
    $('#datatable tbody').append('<tr><th colspan="15">Querying server, one moment</th></tr>');
    $.get(service).done((j) => {
        $("#datatable caption").text(caption);
        if (dt){
            dt.destroy();
        }
        $('#datatable tbody').empty();
        for (let i=0; i < j.data.length; i++){
            const feat = j.data[i];
            const row = ['<tr>',
                `<td>${feat.station}</td>`,
                `<td>${feat.valid}</td>`,
                `<td>${rnd(feat.sbcape_jkg, 0)}</td>`,
                `<td>${rnd(feat.mucape_jkg, 0)}</td>`,
                `<td>${rnd(feat.sbcin_jkg, 0)}</td>`,
                `<td>${rnd(feat.mucin_jkg, 0)}</td>`,
                `<td>${rnd(feat.pwater_mm, 1)}</td>`,
                `<td>${rnd(feat.lcl_agl_m, 0)}</td>`,
                `<td>${rnd(feat.lfc_agl_m, 0)}</td>`,
                `<td>${rnd(feat.el_agl_m, 0)}</td>`,
                `<td>${rnd(feat.total_totals, 1)}</td>`,
                `<td>${rnd(feat.sweat_index, 1)}</td>`,
                `<td>${rnd(feat.srh_sfc_3km_total, 0)}</td>`,
                `<td>${rnd(feat.srh_sfc_1km_total, 0)}</td>`,
                `<td>${rnd(feat.shear_sfc_6km_smps, 1)}</td>`,
                '</tr>'];
            $('#datatable tbody').append(row.join(''));
        }
        if (j.data.length === 0){
            $('#datatable tbody').append('<tr><th colspan="15">No results were found, sorry!</th></tr>');
        }
        if (dt){
            dt = $("#thetable table").DataTable();
        }
    });
}

$( document ).ready(() => {
    $("#filter_year").click((e) => {
        filter_year = $(e.target).prop('checked');
        fetch();
    });
    $("#download").click(() => {
        const service = `/api/1/raobs_by_year.txt?station=${station}`;
        window.location.href = service;
    });
    $('#makefancy').click(() => {
        dt = $("#thetable table").DataTable();
    });

    $("select[name='station']").change((e) => {
        station = $(e.target).val();
        fetch();
    });
    $("select[name='year']").change((e) => {
        $("select[name='sortby']").val("-");
        sortby = "-";
        year = $(e.target).val();
        fetch();
    });
    $("select[name='sortby']").change((e) => {
        sortby = $(e.target).val();
        if (sortby !== "-"){
            fetch();
        }
    });
    $("select[name='asc']").change((e) => {
        asc = $(e.target).val();
        fetch();
    });
    
    const tokens = window.location.href.split("#");
    if (tokens.length === 2){
        const tokens2 = tokens[1].split(":");
        if (tokens2.length > 0){
            station = tokens2[0];
            $("select[name='station']").val(station);
            filter_year = true;
        }
        if (tokens2.length > 1){
            // Yuck, this is either a year or a sort by
            if (tokens2[1].match(/^\d{4}$/)){
                year = tokens2[1];
                $("select[name='year']").val(year);
            } else {
                sortby = tokens2[1];
                $("select[name='sortby']").val(sortby);
                filter_year = false;
            }
        }
        if (tokens2.length > 2){
            asc = tokens2[2];
            $("select[name='asc']").val(asc);
        }
    }
    fetch();
    
});
