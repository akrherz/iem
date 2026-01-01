/* global moment */
let dt = moment(); // Current application time
let irealtime = true; // Is our application in realtime mode or not
let isUpdating = false; // Prevent recursive calls

/**
 * Replace HTML special characters with their entity equivalents
 * @param string val
 * @returns string converted string
 */
function escapeHTML(val) {
    if (typeof val !== 'string') {
        return ''; // Return an empty string for invalid inputs
    }
    return val.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}

function updateURL() {
    // Update the URL with the current product and timestamp
    const url = new URL(window.location.href);
    const opt = getSelectedOption();
    if (!opt) return;
    const pid = opt.value;
    const stamp = dt.utc().format('YYYYMMDDHHmm');
    url.searchParams.set('product', pid);
    url.searchParams.set('timestamp', irealtime ? "0" : stamp);
    window.history.replaceState({}, '', url);
}
function readURL() {
    // Read the URL and set the product and timestamp
    const urlParams = new URLSearchParams(window.location.search);
    const pid = urlParams.get('product');
    const stamp = urlParams.get('timestamp');
    // parse the timestamp
    if (stamp && stamp !== "0") {
        dt = moment.utc(stamp, 'YYYYMMDDHHmm');
        irealtime = false;
    }
    // Set the product
    setProduct(pid);
}

function setProduct(pid) {
    const pp = document.querySelector('select[name=products]');
    if (pid) {
        const options = pp.querySelectorAll('option');
        for (let i = 0; i < options.length; i++) {
            if (options[i].value === pid) {
                pp.selectedIndex = i;
                break;
            }
        }
        // Trigger the change event to update the UI
        const event = new Event('change');
        pp.dispatchEvent(event);
    }
}

function addproducts(data) {
    const pp = document.querySelector('select[name=products]');
    let groupname = '';
    let optgroup = null;

    data.products.forEach(item => {
        if (groupname !== item.groupname) {
            optgroup = document.createElement('optgroup');
            optgroup.setAttribute('label', item.groupname);
            pp.appendChild(optgroup);
            groupname = item.groupname;
        }

        const option = document.createElement('option');
        option.value = item.id;
        option.setAttribute('data-avail_lag', item.avail_lag);
        option.setAttribute('data-interval', item.interval);
        option.setAttribute('data-sts', item.sts);
        option.setAttribute('data-template', item.template);
        option.setAttribute('data-time_offset', item.time_offset);
        option.textContent = item.name;
        optgroup.appendChild(option);
    });
}

function updateTimeDisplay() {
    // Update the time display elements
    document.getElementById('year-value').textContent = dt.year();
    document.getElementById('month-value').textContent = dt.format('MMM');
    document.getElementById('day-value').textContent = dt.format('D');

    const hour = dt.local().hour();
    const period = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    document.getElementById('hour-value').textContent = `${hour12} ${period}`;
    document.getElementById('minute-value').textContent = dt.format('mm');
}

// Helper functions for update() complexity reduction
function calculateTimeConstraints(opt) {
    const ets = moment();
    const sts = moment(opt.getAttribute('data-sts'));
    const interval = parseInt(opt.getAttribute('data-interval'), 10);
    const avail_lag = parseInt(opt.getAttribute('data-avail_lag'), 10);
    const time_offset = parseInt(opt.getAttribute('data-time_offset'), 10);

    if (avail_lag > 0) {
        ets.add(0 - avail_lag, 'minutes');
    }
    ets.subtract(time_offset, 'minutes');

    return { ets, sts, interval };
}

function adjustTimeForConstraints(sts, ets, interval) {
    // Check 1: Bounds check
    if (dt < sts) {
        dt = sts;
    }
    if (dt > ets) {
        dt = ets;
    }

    // Check 2: If our modulus is OK, we can quit early
    if ((dt.utc().hours() * 60 + dt.minutes()) % interval !== 0) {
        // Check 3: Place dt on a time that works for the given interval
        if (interval > 1440) {
            dt = dt.utc().startOf('month');
        } else if (interval >= 60) {
            // minute has to be zero
            dt = dt.utc().startOf('hour');
            if (interval !== 60) {
                dt = dt.utc().startOf('day');
            }
        } else {
            dt = dt.utc().startOf('hour');
        }
    }
}

function updateTimeSliders(sts, interval) {
    // No sliders to update anymore - just update visibility
    updateControlVisibility(interval);
}

function updateControlVisibility(interval) {
    // Show/hide controls based on interval
    // Year and Month are always visible for navigation
    // Day/Hour/Minute visibility depends on product interval
    const minuteControl = document.getElementById('minute-control');
    const hourControl = document.getElementById('hour-control');
    const dayControl = document.getElementById('day-control');

    if (minuteControl) {
        minuteControl.style.display = interval >= 60 ? 'none' : 'block';
    }
    if (hourControl) {
        hourControl.style.display = interval >= 1440 ? 'none' : 'block';
    }
    if (dayControl) {
        dayControl.style.display = interval > 1440 ? 'none' : 'block';
    }
}

function updateImageDisplay(opt) {
    const imagedisplay = document.getElementById('imagedisplay');
    const loadingIndicator = document.getElementById('loading-indicator');

    if (loadingIndicator) {
        loadingIndicator.textContent = 'Loading...'; // Set loading text
        loadingIndicator.style.display = 'block'; // Show loading indicator
    }

    const templateText = escapeHTML(opt.getAttribute('data-template'));
    const url = templateText.replace(/%Y/g, dt.utc().format('YYYY'))
        .replace(/%y/g, dt.utc().format('YY'))
        .replace(/%m/g, dt.utc().format('MM'))
        .replace(/%d/g, dt.utc().format('DD'))
        .replace(/%H/g, dt.utc().format('HH'))
        .replace(/%i/g, dt.utc().format('mm'));

    imagedisplay.onload = () => {
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none'; // Hide loading indicator
        }
    };
    imagedisplay.onerror = () => {
        if (loadingIndicator) {
            loadingIndicator.textContent = 'Error loading image';
        }
    };
    imagedisplay.setAttribute('src', url);
}

function update() {
    if (isUpdating) return; // Safeguard to prevent recursion
    isUpdating = true;

    updateTimeDisplay();

    // Make sure that our current dt matches what can be provided by the
    // currently selected option.
    const opt = getSelectedOption();
    const { ets, sts, interval } = calculateTimeConstraints(opt);

    adjustTimeForConstraints(sts, ets, interval);
    updateTimeSliders(sts, interval);
    updateImageDisplay(opt);

    updateURL();
    updateUITimestamp();
    isUpdating = false;
}

function updateUITimestamp() {
    const opt = getSelectedOption();
    if (parseInt(opt.getAttribute('data-interval'), 10) >= 1440) {
        document.getElementById('utctime').textContent = dt.utc().format('MMM Do YYYY');
        document.getElementById('localtime').textContent = dt.local().format('MMM Do YYYY');
    } else {
        document.getElementById('utctime').textContent = dt.utc().format('MMM Do YYYY HH:mm');
        document.getElementById('localtime').textContent = dt.local().format('MMM Do YYYY h:mm a');
    }
}
function getSelectedOption() {
    const pp = document.querySelector('select[name=products]');
    const selectedOption = pp.options[pp.selectedIndex];
    if (selectedOption) {
        return selectedOption;
    }
    return null;
}

// Replace jQuery UI sliders with simple button controls
function buildUI() {
    // Listen for button clicks
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            // Get the current product interval
            const opt = getSelectedOption();
            if (!opt) {
                return;
            }
            const interval = parseInt(opt.getAttribute('data-interval'), 10);
            // retrieve the data-unit value from the DOM obj
            const unit = button.getAttribute('data-unit');
            let offset = parseInt(button.getAttribute('data-offset'), 10);
            // If the abs(offset) is greater than the interval, we need to adjust
            // the interval to match the offset
            if (unit === "minute" && (Math.abs(offset) < interval)) {
                offset = offset < 0 ? -interval : interval;
            }

            if (unit && !isNaN(offset)) {
                dt.add(offset, unit);
                irealtime = false;
            }
            button.blur();
            update();
        });
    });

    document.querySelector('select[name=products]').addEventListener('change', () => {
        update();
        // unblur
        document.querySelector('select[name=products]').blur();
    });
}
function refresh() {
    if (irealtime) {
        dt = moment();
    }
}

/**
 * Legacy URLs had a hash link with a product ID and timestamp.
 * This function will convert that into a hash link
 */
function translateHashLink() {
    // get the hash link
    const tokens = window.location.href.split("#");
    if (tokens.length !== 2) {
        return;
    }
    const tokens2 = tokens[1].split(".");
    if (tokens2.length !== 2) {
        return;
    }
    const product = escapeHTML(tokens2[0]);
    const timestamp = escapeHTML(tokens2[1]);
    // Set the URL without updating the history using query params
    const url = new URL(window.location.href);
    url.searchParams.set('product', product);
    url.searchParams.set('timestamp', timestamp);
    window.history.replaceState({}, '', url);
}

document.addEventListener('DOMContentLoaded', () => {
    translateHashLink();
    fetch("/json/products.json")
        .then(response => {
            if (!response.ok) throw new Error('Failed to load products');
            return response.json();
        })
        .then(data => {
            addproducts(data);
            buildUI();
            readURL();
            update();
            // Start the timer
            window.setTimeout(refresh, 300000);
        });

    // Add logic for the realtime button
    const realtimeButton = document.getElementById('realtime');
    if (realtimeButton) {
        realtimeButton.addEventListener('click', (event) => {
            event.preventDefault();
            dt = moment(); // Reset to current time
            irealtime = true; // Enable realtime mode
            update(); // Update the UI
        });
    }
});
