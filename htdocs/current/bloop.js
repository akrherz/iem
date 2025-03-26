// global $
$().ready(() => {
    $("#myanimation").jsani({
        imageSrcs: $("#imagesrcs li").map((_i, el) => $(el).text()).get(),
        aniWidth: $("#myanimation").width() + 100,
        aniHeight: $("#myanimation").width() + 100,
        initdwell: 200,
        controls: ['stopplay', 'firstframe', 'previous', 'next', 'lastframe', 'looprock', 'slow', 'fast', 'zoom'],
        last_frame_pause: 8,
        first_frame_pause: 1,
        frame_pause: '0:5, 3:6'
    });
});