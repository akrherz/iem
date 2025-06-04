// filepath: /home/akrherz/projects/iem/htdocs/GIS/apps/iem/freeze.js
document.addEventListener('DOMContentLoaded', () => {
    // Initialize button states and event listeners
    initializeMapControls();
    initializePresetViews();

    function resetButtons() {
        // Reset all button images to their off state
        const panButton = document.querySelector('img[name="panButton"]');
        const zoominButton = document.querySelector('img[name="zoominButton"]');
        const zoomoutButton = document.querySelector('img[name="zoomoutButton"]');

        if (panButton && panButton instanceof HTMLImageElement) {
            panButton.src = '/images/button_pan_off.png';
        }
        if (zoominButton && zoominButton instanceof HTMLImageElement) {
            zoominButton.src = '/images/button_zoomin_off.png';
        }
        if (zoomoutButton && zoomoutButton instanceof HTMLImageElement) {
            zoomoutButton.src = '/images/button_zoomout_off.png';
        }
    }

    function initializeMapControls() {
        const myForm = document.querySelector('form[name="myform"]');
        if (!myForm || !(myForm instanceof HTMLFormElement)) return;

        // Zoom In button
        const zoominButton = document.querySelector('img[name="zoominButton"]');
        if (zoominButton && zoominButton instanceof HTMLImageElement) {
            zoominButton.addEventListener('click', function () {
                resetButtons();
                this.src = '/images/button_zoomin_on.png';
                const zoomInput = myForm.querySelector('input[name="zoom"]');
                if (zoomInput && zoomInput instanceof HTMLInputElement) {
                    zoomInput.value = '-2';
                }
            });
        }

        // Pan button
        const panButton = document.querySelector('img[name="panButton"]');
        if (panButton && panButton instanceof HTMLImageElement) {
            panButton.addEventListener('click', function () {
                resetButtons();
                this.src = '/images/button_pan_on.png';
                const zoomInput = myForm.querySelector('input[name="zoom"]');
                if (zoomInput && zoomInput instanceof HTMLInputElement) {
                    zoomInput.value = '1';
                }
            });
        }

        // Zoom Out button
        const zoomoutButton = document.querySelector('img[name="zoomoutButton"]');
        if (zoomoutButton && zoomoutButton instanceof HTMLImageElement) {
            zoomoutButton.addEventListener('click', function () {
                resetButtons();
                this.src = '/images/button_zoomout_on.png';
                const zoomInput = myForm.querySelector('input[name="zoom"]');
                if (zoomInput && zoomInput instanceof HTMLInputElement) {
                    zoomInput.value = '2';
                }
            });
        }
    }

    function initializePresetViews() {
        // Handle preset view dropdown navigation
        const baForm = document.querySelector('form[name="ba"]');
        if (baForm && baForm instanceof HTMLFormElement) {
            const baSelect = baForm.querySelector('select[name="ba"]');
            if (baSelect && baSelect instanceof HTMLSelectElement) {
                baSelect.addEventListener('change', function () {
                    const selectedValue = this.options[this.selectedIndex].value;
                    if (selectedValue && selectedValue !== '#') {
                        window.location.href = selectedValue;
                    }
                });
            }
        }
    }
});
