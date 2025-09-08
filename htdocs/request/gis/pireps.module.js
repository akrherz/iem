// Module to wire up the "filter" inputs to show/hide #spatialfilter without jQuery
const initPireps = () => {
    const inputs = document.querySelectorAll("input[name='filter']");
    const spatial = document.getElementById("spatialfilter");
    const summaryEl = document.getElementById("filter-summary");
    const artcc = document.querySelector("select[name='artcc']");
    const degrees = document.getElementById("degrees");
    const lon = document.getElementById("lon");
    const lat = document.getElementById("lat");

    if (!inputs.length || !spatial || !summaryEl) return;

    const getFilterParts = () => {
        const parts = [];
        if (artcc && artcc.value && artcc.value !== "_ALL") {
            parts.push(`ARTCC=${artcc.value}`);
        }
        const spatialEnabled = document.querySelector("input[name='filter']").checked;
        if (spatialEnabled && degrees && lon && lat) {
            parts.push(`Spatial=${degrees.value}° @ (${lon.value}, ${lat.value})`);
        }
        return parts;
    };

    const setSummaryBadge = (parts) => {
        const badge = summaryEl.querySelector(".badge");
        if (!badge) return;
        if (parts.length) {
            badge.textContent = parts.join(' · ');
            badge.className = 'badge bg-info text-dark';
        } else {
            badge.textContent = 'No filters';
            badge.className = 'badge bg-secondary';
        }
    };

    const updateSummary = () => setSummaryBadge(getFilterParts());

    const validateSpatial = () => {
        let ok = true;
        const setInvalid = (el, cond) => {
            if (!el) return;
            if (cond) {
                el.classList.add('is-invalid');
                ok = false;
            } else {
                el.classList.remove('is-invalid');
            }
        };
        const d = parseFloat(degrees.value);
        setInvalid(degrees, Number.isNaN(d) || d < 0);
        const lonv = parseFloat(lon.value);
        setInvalid(lon, Number.isNaN(lonv) || lonv < -180 || lonv > 180);
        const latv = parseFloat(lat.value);
        setInvalid(lat, Number.isNaN(latv) || latv < -90 || latv > 90);
        return ok;
    };

    // Wire up events
    inputs.forEach((input) => {
        input.addEventListener('change', (evt) => {
            const checked = Boolean(evt.currentTarget.checked);
            spatial.classList.toggle('d-none', !checked);
            if (checked) validateSpatial();
            updateSummary();
        });
    });

    if (artcc) {
        artcc.addEventListener('change', updateSummary);
    }
    [degrees, lon, lat].forEach((el) => {
        if (!el) return;
        el.addEventListener('input', () => {
            // live validate only if spatial filter enabled
            if (document.querySelector("input[name='filter']").checked) validateSpatial();
            updateSummary();
        });
    });

    // initial state
    updateSummary();
};

// Auto-initialize when DOM is ready, but also export for explicit init by consumers.
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPireps);
} else {
    initPireps();
}

export default initPireps;
