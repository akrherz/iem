

// https://stackoverflow.com/questions/5202085
String.prototype.rsplit = function (sep, maxsplit) {
    var split = this.split(sep);
    return maxsplit ? [split.slice(0, -maxsplit).join(sep)].concat(split.slice(-maxsplit)) : split;
}

flowplayer(function (api, root) { 
    api.on("error", function (e, api, err) {
        if (err.code === 4) { // Video file not found
            // reset state
            api.error = api.loading = false;
        }
    });
  
 });

function myloader() {
    var ts = new Date();
    var mycam = document.theform.mycam.value;
    var mylapse = document.theform.mylapse.value;
    window.location.href = "#" + mycam + "_" + mylapse;
    var url = "/onsite/lapses/auto/" + mycam + "_" + mylapse + ".flv?" + ts.getTime();
    var url2 = "/onsite/lapses/auto/" + mycam + "_" + mylapse + ".mp4?" + ts.getTime();
    var api = flowplayer(0);
    api.load({
        sources: [
            { type: "video/flv", src: url },
            { type: "video/mp4",  src: url2 }
        ]
    });
}

$(function () {
    var ts = new Date();
    var tokens = window.location.href.split('#');
    if (tokens.length == 2) {
        var tokens2 = tokens[1].rsplit('_', 1);
        if (tokens2.length == 2) {
            var mycam = tokens2[0];
            document.getElementById('mycam').value = mycam;
            var mylapse = tokens2[1];
            document.getElementById('mylapse').value = mylapse;
            window.setTimeout(myloader, 1000);
        } else {
            document.getElementById('mycam').value = 'ames';
        }
    } else {
        document.getElementById('mycam').value = 'ames';
    }
});