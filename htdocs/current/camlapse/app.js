/* global flowplayer */

// https://stackoverflow.com/questions/5202085
function rsplit(val, sep, maxsplit) {
    const split = val.split(sep);
    return maxsplit ? [split.slice(0, -maxsplit).join(sep)].concat(split.slice(-maxsplit)) : split;
}

/**
 * Replace HTML special characters with their entity equivalents
 * @param string val
 * @returns string converted string
 */
function escapeHTML(val) {
    return val.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}

let player = null;

function myloader() {
    const ts = new Date();
    const mycam = escapeHTML(document.theform.mycam.value);
    const mylapse = escapeHTML(document.theform.mylapse.value);
    window.location.href = `#${mycam}_${mylapse}`;
    const url = `https://mesonet.agron.iastate.edu/onsite/lapses/auto/${mycam}_${mylapse}.mp4?${ts.getTime()}`;

    if (player) {
        // Load new video into existing player
        player.load({
            sources: [
                { type: "video/mp4", src: url }
            ]
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the flowplayer
    const container = document.querySelector('.flowplayer');
    player = flowplayer(container, {
        clip: {
            sources: [
                { type: "video/mp4", src: "https://mesonet.agron.iastate.edu/onsite/lapses/auto/isu_curtis_center_sunrise.mp4" }
            ]
        }
    });

    player.on("error", (_e, api, err) => {
        if (err.code === 4) { // Video file not found
            // reset state
            api.error = api.loading = false;
        }
    });

    const tokens = window.location.href.split('#');
    if (tokens.length === 2) {
        const tokens2 = rsplit(tokens[1], '_', 1);
        if (tokens2.length === 2) {
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
