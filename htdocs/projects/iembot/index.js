function clean(str) {
    const tempDiv = document.createElement("div");
    tempDiv.appendChild(document.createTextNode(str));
    return tempDiv.innerHTML;
}

function urlChanger() {
    const myid = clean(document.myForm.wfo.value.toLowerCase());
    document.getElementById("wfolink").innerHTML = `<b>URL:</b> <a href="https://weather.im/iembot-rss/room/${myid}chat.xml">https://weather.im/iembot-rss/room/${myid}chat.xml</a>`;
}

function revdiv(myid) {
    const elem = document.getElementById(myid);
    const channelElem = document.getElementById(`channel_${myid}`);
    if (window.getComputedStyle(elem).display === 'block') {
        elem.style.display = 'none';
        channelElem.innerHTML = '<i class="fa fa-plus"></i>';
    } else {
        window.location.hash = `#channel_${myid}`;
        const parent = channelElem.parentElement;
        if(parent?.parentElement) {
            parent.parentElement.classList.add('info');
        }
        elem.style.display = 'block';
        channelElem.innerHTML = '<i class="fa fa-minus"></i>';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("wfoselect").addEventListener("change", urlChanger);
    const tokens = window.location.href.split('#');
    if (tokens.length === 2) {
        const subtokens = tokens[1].split("_");
        if (subtokens.length === 2) {
            revdiv(subtokens[1]);
            const targetElem = document.getElementById(tokens[1]);
            if (targetElem) {
                if ('scrollBehavior' in document.documentElement.style) {
                    targetElem.scrollIntoView({ behavior: "smooth" });
                } else {
                    window.scrollTo(0, targetElem.offsetTop);
                }
            }
        }
    }
});