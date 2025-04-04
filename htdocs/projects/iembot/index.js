// global $

function clean(str) {
    return $("<p>").html(str).text();
}

function urlChanger() {
    const myid = clean(document.myForm.wfo.value.toLowerCase());
    document.getElementById("wfolink").innerHTML = `<b>URL:</b> <a href="https://weather.im/iembot-rss/room/${myid}chat.xml">/iembot-rss/room/${myid}chat.xml</a>`;
}

function revdiv(myid){
    const $a = $(`#${myid}`);
    if ($a.css('display') === 'block'){
        $a.css('display', 'none');
        $(`#channel_${myid}`).html('<i class="fa fa-plus"></i>');
    } else {
        window.location.hash = `#channel_${myid}`;
        $(`#channel_${myid}`).parent().parent().addClass('info');
        $a.css('display', 'block');
        $(`#channel_${myid}`).html('<i class="fa fa-minus"></i>');
    }
    }


$().ready(() => {

    $("#wfoselect").change(() => {
        urlChanger();
    });

    const tokens = window.location.href.split('#');
    if (tokens.length === 2) {
        const subtokens = tokens[1].split("_");
        if (subtokens.length === 2) {
            revdiv(subtokens[1]);
            $([document.documentElement, document.body]).animate({
                scrollTop: $(`#${tokens[1]}`).offset().top
            }, 2000);
        }
    }
});