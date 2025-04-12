/* global moment, $, noUiSlider */
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
    const pid = getSelectedOption().value;
    const stamp = dt.utc().format('YYYYMMDDHHmm');
    url.searchParams.set('product', pid);
    url.searchParams.set('timestamp', irealtime ? "0": stamp);
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

function updateSliderLabels() {
    // Update the labels for the sliders
    const yearLabelText = document.querySelector('label[for="year_slider"] .year-label-text');
    const dayLabelText = document.querySelector('label[for="day_slider"] .day-label-text');
    const hourLabelText = document.querySelector('label[for="hour_slider"] .hour-label-text');
    const minuteLabelText = document.querySelector('label[for="minute_slider"] .minute-label-text');
    if (yearLabelText) {
        yearLabelText.textContent = `${dt.year()}`;
    }
    if (dayLabelText) {
        dayLabelText.textContent = `Day: ${moment([dt.year()]).dayOfYear(dt.dayOfYear()).format('MMM D')}`;
    }
    if (hourLabelText) {
        const hour = dt.local().hour();
        const period = hour >= 12 ? 'PM' : 'AM';
        const hour12 = hour % 12 || 12; // Convert to 12-hour format
        hourLabelText.textContent = `${hour12} ${period}`;
    }
    if (minuteLabelText) {
        minuteLabelText.textContent = `${dt.local().minute()}`;
    }
}

function update() {
    if (isUpdating) return; // Safeguard to prevent recursion
    isUpdating = true;

    updateSliderLabels();

    // Make sure that our current dt matches what can be provided by the
    // currently selected option.
    const opt = getSelectedOption();
    const ets = moment();
    const sts = moment(opt.getAttribute('data-sts'));
    const interval = parseInt(opt.getAttribute('data-interval'), 10);
    const avail_lag = parseInt(opt.getAttribute('data-avail_lag'), 10);
    if (avail_lag > 0) {
        // Adjust the ets such to account for this lag
        ets.add(0 - avail_lag, 'minutes');
    }
    const time_offset = parseInt(opt.getAttribute('data-time_offset'), 10);
    ets.subtract(time_offset, 'minutes');
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
            dt.utc().startOf('month');
        } else if (interval >= 60) {
            // minute has to be zero
            dt.utc().startOf('hour');
            if (interval !== 60) {
                dt.utc().startOf('day');
            }
        } else {
            dt.utc().startOf('hour');
        }
    }
    const now = moment();

    // Update year slider
    const yearSlider = document.getElementById('year_slider');
    if (yearSlider?.noUiSlider) {
        yearSlider.noUiSlider.updateOptions({
            range: {
                min: sts.year(),
                max: now.year()
            },
            start: dt.local().year()
        });
    }

    // Update day slider
    const daySlider = document.getElementById('day_slider');
    if (daySlider?.noUiSlider) {
        daySlider.noUiSlider.set(dt.local().dayOfYear());
    }

    // Update hour slider
    const hourSlider = document.getElementById('hour_slider');
    if (hourSlider?.noUiSlider) {
        if (interval >= 1440) { // Disable if interval is a day or more
            hourSlider.setAttribute('disabled', true);
            hourSlider.classList.add('noUi-disabled');
        } else {
            hourSlider.removeAttribute('disabled');
            hourSlider.classList.remove('noUi-disabled');
            hourSlider.noUiSlider.set(dt.local().hour());
        }
    }

    // Update minute slider
    const minuteSlider = document.getElementById('minute_slider');
    if (minuteSlider?.noUiSlider) {
        if (interval < 60) {
            minuteSlider.removeAttribute('disabled');
            minuteSlider.classList.remove('noUi-disabled');
            minuteSlider.noUiSlider.updateOptions({
                range: {
                    min: 0,
                    max: 59
                },
                step: interval, // Dynamically set the step interval
                start: dt.local().minute()
            });
        } else {
            minuteSlider.setAttribute('disabled', true);
            minuteSlider.classList.add('noUi-disabled');
        }
    }

    // Show or hide sliders based on interval
    if (opt.getAttribute('data-interval') >= 60) {
        document.getElementById('minute_slider').style.display = 'none';
    } else {
        document.getElementById('minute_slider').style.display = 'block';
    }
    if (opt.getAttribute('data-interval') >= 1440) {
        document.getElementById('hour_slider').style.display = 'none';
    } else {
        document.getElementById('hour_slider').style.display = 'block';
    }

    // Update image display with loading indicator
    const imagedisplay = document.getElementById('imagedisplay');
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.textContent = 'Loading...'; // Set loading text
        loadingIndicator.style.display = 'block'; // Show loading indicator
    }
    const tpl = document.createElement('p');
    tpl.textContent = opt.getAttribute('data-template');
    const templateText = tpl.textContent;
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
        loadingIndicator.textContent = 'Error loading image';
    };
    imagedisplay.setAttribute('src', url);

    updateURL();

    // Update UI timestamp
    updateUITimestamp();
    isUpdating = false;
}

function updateUITimestamp() {
    const opt = getSelectedOption();
    if (opt.getAttribute('data-interval') >= 1440) {
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

// Replace jQuery UI sliders with noUiSlider
function buildUI() {
    // Year slider
    const yearSlider = document.getElementById('year_slider');
    const yearLabelText = document.querySelector('label[for="year_slider"] .year-label-text');
    noUiSlider.create(yearSlider, {
        start: dt.year(),
        range: {
            min: 2000, // Example start year
            max: moment().year()
        },
        step: 1,
        tooltips: true,
        format: {
            to: value => Math.round(value),
            from: value => Math.round(value)
        }
    });
    yearSlider.noUiSlider.on('change', (values) => {
        dt.year(parseInt(values[0], 10));
        if (yearLabelText) {
            yearLabelText.textContent = `${values[0]}`;
        }
        irealtime = false;
        update();
    });

    // Day slider
    const daySlider = document.getElementById('day_slider');
    const dayLabelText = document.querySelector('label[for="day_slider"] .day-label-text');
    const updateDaySlider = () => {
        const year = dt.year();
        const daysInYear = moment([year]).isLeapYear() ? 366 : 365;
        const monthStartDays = Array.from({ length: 12 }, (_, i) =>
            moment([year, i, 1]).dayOfYear()
        );

        if (daySlider.noUiSlider) {
            daySlider.noUiSlider.destroy();
        }

        noUiSlider.create(daySlider, {
            start: dt.dayOfYear(),
            range: {
                min: 1,
                max: daysInYear
            },
            step: 1,
            tooltips: {
                to: value => moment([year]).dayOfYear(Math.round(value)).format('MMM D'),
                from: value => Math.round(value)
            },
            format: {
                to: value => Math.round(value),
                from: value => Math.round(value)
            }
        });

        daySlider.noUiSlider.on('change', (values) => {
            dt.dayOfYear(parseInt(values[0], 10));
            if (dayLabelText) {
                dayLabelText.textContent = `Day: ${moment([dt.year()]).dayOfYear(values[0]).format('MMM D')}`;
            }
            irealtime = false;
            update();
        });

        const density = window.innerWidth < 768 ? 2 : 4;

        daySlider.noUiSlider.pips({
            mode: 'values',
            values: monthStartDays,
            density,
            format: {
                to: value => moment([year]).dayOfYear(value).format('MMM D'),
                from: value => value
            }
        });
    };

    updateDaySlider();

    // Hour slider
    const hourSlider = document.getElementById('hour_slider');
    const hourLabelText = document.querySelector('label[for="hour_slider"] .hour-label-text');
    noUiSlider.create(hourSlider, {
        start: dt.hour(),
        range: {
            min: 0,
            max: 23
        },
        step: 1,
        tooltips: true,
        format: {
            to: value => Math.round(value),
            from: value => Math.round(value)
        }
    });
    hourSlider.noUiSlider.on('change', (values) => {
        dt.hour(parseInt(values[0], 10));
        const hour = dt.local().hour();
        const period = hour >= 12 ? 'PM' : 'AM';
        const hour12 = hour % 12 || 12; // Convert to 12-hour format
        if (hourLabelText) {
            hourLabelText.textContent = `${hour12} ${period}`;
        }
        irealtime = false;
        update();
    });

    // Minute slider
    const minuteSlider = document.getElementById('minute_slider');
    const minuteLabelText = document.querySelector('label[for="minute_slider"] .minute-label-text');
    noUiSlider.create(minuteSlider, {
        start: dt.minute(),
        range: {
            min: 0,
            max: 59
        },
        step: 1,
        tooltips: true,
        format: {
            to: value => Math.round(value),
            from: value => Math.round(value)
        }
    });
    minuteSlider.noUiSlider.on('change', (values) => {
        dt.minute(parseInt(values[0], 10));
        if (minuteLabelText) {
            minuteLabelText.textContent = `${values[0]}`;
        }
        irealtime = false;
        update();
    });

    // Listen for click
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            // Get the current product interval
            const opt = getSelectedOption();
            if (!opt) {
                return;
            }
            const interval = parseInt(opt.getAttribute('data-interval'), 10);
            // retrive the data-unit value from the DOM obj
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
        .then(response => response.json())
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
