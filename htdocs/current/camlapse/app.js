
var flowplayer = window.flowplayer || {}; // skipcq: JS-0239

// https://stackoverflow.com/questions/5202085
String.prototype.rsplit = function (sep, maxsplit) {
    var split = this.split(sep);
    return maxsplit ? [split.slice(0, -maxsplit).join(sep)].concat(split.slice(-maxsplit)) : split;
}
function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

flowplayer((api, _root) => {
    api.on("error", (_e, api2, err) => {
        if (err.code === 4) { // Video file not found
            // reset state
            api2.error = api2.loading = false;
        }
    });

});

function myloader() {
    const ts = new Date();
    const mycam = text(document.theform.mycam.value);
    const mylapse = text(document.theform.mylapse.value);
    window.location.href = `#${mycam}_${mylapse}`;
    const url = `/onsite/lapses/auto/${mycam}_${mylapse}.flv?${ts.getTime()}`;
    const url2 = `/onsite/lapses/auto/${mycam}_${mylapse}.mp4?${ts.getTime()}`;
    flowplayer(0).load({
        sources: [
            { type: "video/flv", src: url },
            { type: "video/mp4", src: url2 }
        ]
    });
}

$(() => {
    const tokens = window.location.href.split('#');
    if (tokens.length == 2) {
        const tokens2 = tokens[1].rsplit('_', 1);
        if (tokens2.length == 2) {
            const mycam = tokens2[0];
            document.getElementById('mycam').value = mycam;
            const mylapse = tokens2[1];
            document.getElementById('mylapse').value = mylapse;
            window.setTimeout(myloader, 1000);
        } else {
            document.getElementById('mycam').value = 'isu_curtis_center';
        }
    } else {
        document.getElementById('mycam').value = 'isu_curtis_center';
    }
});