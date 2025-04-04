// global $
function urlChanger() {
    const myid = document.myForm.wfo.value.toLowerCase();
    document.getElementById("wfolink").innerHTML = "<b>URL:</b> <a href=\"https://weather.im/iembot-rss/room/" + myid + "chat.xml\">{$EXTERNAL_BASEURL}/iembot-rss/room/" + myid + "chat.xml</a>";
}

$().ready(() => {
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