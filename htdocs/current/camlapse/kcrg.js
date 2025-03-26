// global flowplayer
flowplayer.conf = {
    engine: 'flash',
    swf: '/vendor/flowplayer/6.0.2/flowplayer.swf'
};
let mycam = null;
let mylapse = null;
let ts = new Date();
const container = document.getElementById("player");
flowplayer(container, {
    clip: {
        sources: [{
            type: 'video/mp4',
            src: `/onsite/lapses/auto/kirkwood_sunrise.mp4?${ts.getTime()}`
        },
        {
            type: 'video/flv',
            src: `/onsite/lapses/auto/kirkwood_sunrise.flv?${ts.getTime()}`
        }

        ]
    }
});

function myloader() {
    ts = new Date();
    mycam = document.theform.mycam.value;
    mylapse = document.theform.mylapse.value;
    window.location.href = `#${mycam}_${mylapse}`;
    const url = `/onsite/lapses/auto/${mycam}_${mylapse}.flv?${ts.getTime()}`;
    const url2 = `/onsite/lapses/auto/${mycam}_${mylapse}.mp4?${ts.getTime()}`;
    api = flowplayer();
    api.load([{ flash: url, mp4: url2 }]);
}

const tokens = window.location.href.split('#');
if (tokens.length == 2) {
    const tokens2 = tokens[1].split('_');
    if (tokens2.length == 2) {
        mycam = tokens2[0];
        document.getElementById('mycam').value = mycam;
        mylapse = tokens2[1];
        document.getElementById('mylapse').value = mylapse;
        myloader();
    }
}
