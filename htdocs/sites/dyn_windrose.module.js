document.addEventListener('DOMContentLoaded', () => {
    const setbins = document.querySelector('input[name="setbins"]');
    const showbins = document.getElementById('showbins');

    if (setbins && showbins) {
        setbins.addEventListener('change', () => {
            if (setbins.checked) {
                showbins.style.display = '';
            } else {
                showbins.style.display = 'none';
            }
        });
    }

    const windrose = document.getElementById('windrose-plot');
    const imgLoading = document.getElementById('img-loading');

    const hideLoading = () => {
        if (imgLoading) imgLoading.style.display = 'none';
    };

    if (windrose) {
        windrose.addEventListener('load', hideLoading);
        // If the element is an <img> and already loaded from cache, hide immediately
        if (windrose.complete) hideLoading();
    }
});
