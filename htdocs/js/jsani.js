// global $

/**
 * Converts the iemjsani div into an animation player
 */
$().ready(() => {
    $("#iemjsani").jsani({
        imageSrcs: $("#iemjsani_frames li").map((_i, el) => $(el).text()).get(),
        aniWidth: $("#iemjsani").width(),
        aniHeight: $("#iemjsani").height(),
        initdwell: 200,
        controls: ['stopplay', 'firstframe', 'previous', 'next', 'lastframe', 'looprock', 'slow', 'fast', 'zoom'],
        last_frame_pause: 8,
        first_frame_pause: 1,
        frame_pause: '0:5, 3:6'
    });
});