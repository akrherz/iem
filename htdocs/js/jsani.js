/**
 * Vanilla JS image animation player for #iemjsani
 * Replaces legacy jQuery/jsani usage
 *
 * Controls: play/pause, first, prev, next, last, loop, speed, zoom
 *
 * Usage: expects #iemjsani_frames li to contain frame URLs
 */
document.addEventListener('DOMContentLoaded', () => {
    const frameList = document.querySelectorAll('#iemjsani_frames li');
    const imageSrcs = Array.from(frameList).map(el => el.textContent.trim());
    const container = document.getElementById('iemjsani');
    if (!container || imageSrcs.length === 0) return;

    // Buttons
    let controlsFaster = null;
    let controlsSlower = null;
    let controlsLoop = null;
    let controlsPlay = null;
    let controlsFirst = null;
    let controlsPrev = null;
    let controlsNext = null;
    let controlsLast = null;
    let controlsZoomIn = null;
    let controlsZoomOut = null;

    // Config
    const aniWidth = container.offsetWidth;
    const aniHeight = container.offsetHeight;
    const initdwell = 200;
    const lastFramePause = 8;
    const firstFramePause = 1;
    // frame_pause: '0:5, 3:6' (frame:pause) not implemented for brevity

    // State
    let current = 0;
    let playing = false;
    let dwell = initdwell;
    let loop = true;
    let timer = null;
    let zoom = 1;

    // Create DOM
    container.innerHTML = '';
    const img = document.createElement('img');
    img.style.width = `${aniWidth}px`;
    img.style.height = `${aniHeight}px`;
    img.style.objectFit = 'contain';
    img.src = imageSrcs[0];
    container.appendChild(img);

    // Controls
    const controls = document.createElement('div');
    controls.className = 'jsani-controls btn-group mb-2';
    controls.role = 'group';

    function makeBtn(label, title, onClick) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-outline-primary';
        btn.textContent = label;
        btn.title = title;
        btn.addEventListener('click', onClick);
        return btn;
    }

    function updateImg() {
        img.src = imageSrcs[current];
        img.style.transform = `scale(${zoom})`;
    }

    function play() {
        if (playing) return;
        playing = true;
        controlsPlay.textContent = 'Pause';
        nextFrameLoop();
    }
    function pause() {
        playing = false;
        controlsPlay.textContent = 'Play';
        if (timer) clearTimeout(timer);
    }
    function nextFrameLoop() {
        if (!playing) return;
        next();
        let frameDwell = dwell;
        if (current === 0) frameDwell *= firstFramePause;
        if (current === imageSrcs.length - 1) frameDwell *= lastFramePause;
        timer = setTimeout(nextFrameLoop, frameDwell);
    }
    function next() {
        current = (current + 1) % imageSrcs.length;
        if (!loop && current === 0) pause();
        updateImg();
    }
    function prev() {
        current = (current - 1 + imageSrcs.length) % imageSrcs.length;
        updateImg();
    }
    function first() {
        current = 0;
        updateImg();
    }
    function last() {
        current = imageSrcs.length - 1;
        updateImg();
    }
    function toggleLoop() {
        loop = !loop;
        controlsLoop.textContent = loop ? 'Loop' : 'No Loop';
    }
    function slower() {
        dwell = Math.min(dwell + 100, 2000);
    }
    function faster() {
        dwell = Math.max(dwell - 50, 50);
    }
    function zoomIn() {
        zoom = Math.min(zoom + 0.2, 3);
        updateImg();
    }
    function zoomOut() {
        zoom = Math.max(zoom - 0.2, 0.5);
        updateImg();
    }

    // Buttons
    controlsPlay = makeBtn('Play', 'Play/Pause', () => playing ? pause() : play());
    controlsFirst = makeBtn('⏮', 'First Frame', first);
    controlsPrev = makeBtn('◀', 'Previous Frame', prev);
    controlsNext = makeBtn('▶', 'Next Frame', next);
    controlsLast = makeBtn('⏭', 'Last Frame', last);
    controlsLoop = makeBtn('Loop', 'Toggle Loop', toggleLoop);
    controlsSlower = makeBtn('–', 'Slower', slower);
    controlsFaster = makeBtn('+', 'Faster', faster);
    controlsZoomIn = makeBtn('🔍+', 'Zoom In', zoomIn);
    controlsZoomOut = makeBtn('🔍–', 'Zoom Out', zoomOut);

    [controlsPlay, controlsFirst, controlsPrev, controlsNext, controlsLast, controlsLoop, controlsSlower, controlsFaster, controlsZoomIn, controlsZoomOut].forEach(btn => controls.appendChild(btn));
    container.appendChild(controls);

    // Keyboard navigation (optional)
    container.tabIndex = 0;
    container.addEventListener('keydown', (e) => {
        if (e.key === ' ') { e.preventDefault(); playing ? pause() : play(); }
        if (e.key === 'ArrowRight') { next(); }
        if (e.key === 'ArrowLeft') { prev(); }
    });

    // Initial render
    updateImg();
});