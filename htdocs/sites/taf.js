$(document).ready(() =>{
    const rawtext = $("#rawtext");
    const station3 = rawtext.data("station3");
    $.ajax({
        url: `/cgi-bin/afos/retrieve.py?pil=TAF${station3}&fmt=html`,
        success: (data) => {
            rawtext.html(data);
        }
    });

    const afd = $("#afd");
    const wfo = afd.data("wfo");
    $.ajax({
        url: `/cgi-bin/afos/retrieve.py?pil=AFD${wfo}&fmt=html&aviation_afd=1`,
        success: (data) => {
            afd.html(data);
        }
    });

    const metars = $("#metars");
    const station4 = metars.data("station4");
    $.ajax({
        url: `/cgi-bin/request/asos.py?station=${station4}&hours=4&nometa=1&data=metar&report_type=3,4`,
        success: (data) => {
            metars.html(`<pre>${data}</pre>`);
        }
    });

});