/* global moment, $ */
let dt = moment(); // Current application time
let irealtime = true; // Is our application in realtime mode or not

function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

function readHashLink() {
    const tokens = window.location.href.split("#");
    if (tokens.length != 2) {
        return;
    }
    const tokens2 = tokens[1].split(".");
    if (tokens2.length != 2) {
        return;
    }
    const pid = text(tokens2[0]);
    const stamp = text(tokens2[1]);
    // parse the timestamp
    if (stamp != "0") {
        dt = moment.utc(stamp, 'YYYYMMDDHHmm');
        irealtime = false;
    }
    $("#products").val(pid).trigger("change");
}

function addproducts(data) {
    // Add entries into the products dropdown
    const pp = $('select[name=products]');
    let groupname = '';
    let optgroup = null;
    $.each(data.products, (_i, item) => {
        if (groupname != item.groupname) {
            optgroup = $('<optgroup>');
            optgroup.attr('label', item.groupname);
            pp.append(optgroup);
            groupname = item.groupname;
        }
        optgroup.append($('<option>', {
            value: item.id,
            'data-avail_lag': item.avail_lag,
            'data-interval': item.interval,
            'data-sts': item.sts,
            'data-template': item.template,
            'data-time_offset': item.time_offset,
            text: item.name
        }));
    });
    // now turn it into a select2 widget
    pp.select2();
    pp.on('change', () => {
        rectifyTime();
        update();
    });
    // read the anchor URI
    readHashLink();
}
function rectifyTime() {
    // Make sure that our current dt matches what can be provided by the
    // currently selected option.
    const opt = getSelectedOption();
    const ets = moment();
    const sts = moment(opt.attr('data-sts'));
    const interval = parseInt(opt.attr('data-interval'), 10);
    const avail_lag = parseInt(opt.attr('data-avail_lag'), 10);
    if (avail_lag > 0) {
        // Adjust the ets such to account for this lag
        ets.add(0 - avail_lag, 'minutes');
    }
    const time_offset = parseInt(opt.attr('data-time_offset'), 10);
    ets.subtract(time_offset, 'minutes');
    // Check 1: Bounds check
    if (dt < sts) {
        dt = sts;
    }
    if (dt > ets) {
        dt = ets;
    }
    // Check 2: If our modulus is OK, we can quit early
    if ((dt.utc().hours() * 60 + dt.minutes()) % interval == 0) {
        return;
    }

    // Check 3: Place dt on a time that works for the given interval
    if (interval > 1440) {
        dt.utc().startOf('month');
    } else if (interval >= 60) {
        // minute has to be zero
        dt.utc().startOf('hour');
        if (interval != 60) {
            dt.utc().startOf('day');
        }
    } else {
        dt.utc().startOf('hour');
    }
}
function update() {
    // called after a slider event, button clicked, realtime refresh
    // or new product selected
    const opt = getSelectedOption();
    // adjust the sliders
    const sts = moment(opt.attr('data-sts'));
    const now = moment();
    const tpl = text(opt.attr('data-template'));
    // We support %Y %m %d %H %i %y
    const url = tpl.replace(/%Y/g, dt.utc().format('YYYY'))
        .replace(/%y/g, dt.utc().format('YY'))
        .replace(/%m/g, dt.utc().format('MM'))
        .replace(/%d/g, dt.utc().format('DD'))
        .replace(/%H/g, dt.utc().format('HH'))
        .replace(/%i/g, dt.utc().format('mm'));
    $('#year_slider').slider({
        min: sts.year(),
        max: now.year(),
        value: dt.utc().year()
    }).slider('pips', 'refresh');
    $('#day_slider').slider({
        value: dt.utc().dayOfYear()
    });
    $('#hour_slider').slider({
        value: dt.utc().hour()
    });
    $('#minute_slider').slider({
        value: dt.utc().minute()
    });
    if (opt.attr('data-interval') > 60) {
        $('#minute_slider').css('display', 'none');
    } else {
        $('#minute_slider').css('display', 'block');
    }
    if (opt.attr('data-interval') > 1440) {
        $('#hour_slider').css('display', 'none');
    } else {
        $('#hour_slider').css('display', 'block');
    }

    $('#imagedisplay').attr('src', url);
    window.location.href = `#${text(opt.val())}.${dt.utc().format('YYYYMMDDHHmm')}`;
    updateUITimestamp();
}
function updateUITimestamp() {
    const opt = getSelectedOption();
    if (opt.attr('data-interval') >= 1440) {
        $('#utctime').html(dt.utc().format('MMM Do YYYY'));
        $('#localtime').html(dt.utc().format('MMM Do YYYY'));
    } else {
        $('#utctime').html(dt.utc().format('MMM Do YYYY, HH:mm'));
        $('#localtime').html(dt.local().format('MMM Do YYYY, h:mm a'));
    }
}
function getSelectedOption() {
    return $('#products :selected');
}
function buildUI() {
    //year
    $("#year_slider").slider({
        slide(_event, ui) {
            dt.year(ui.value);
            rectifyTime();
            update();
            irealtime = false;
        }
    }).slider("pips").slider("float");
    //hour
    $("#hour_slider").slider({
        min: 0,
        max: 23,
        slide(_event, ui) {
            dt.hour(ui.value);
            rectifyTime();
            update();
            irealtime = false;
        }
    }).slider("pips").slider("float");
    //hour
    $("#minute_slider").slider({
        min: 0,
        max: 59,
        slide(_event, ui) {
            dt.minute(ui.value);
            rectifyTime();
            update();
            irealtime = false;
        }
    }).slider("pips").slider("float");
    //day
    $("#day_slider").slider({
        min: 1,
        max: 367,
        slide(_event, ui) {
            dt.dayOfYear(ui.value);
            rectifyTime();
            update();
            irealtime = false;
        }
    }).slider("pips", {
        rest: 'label',
        last: 'pip',
        formatLabel: function (val) {
            return moment(dt.format("YYYY") + "0101", "YYYYMMDD").add(val - 1, 'days').format("MMM D");
        }
    }).slider("float", {
        formatLabel: function (val) {
            return moment(dt.format("YYYY") + "0101", "YYYYMMDD").add(val - 1, 'days').format("MMM D");
        }
    });


    // Listen for click
    $('.btn').on('click', function () {
        if (this.id == 'next') {
            const opt = getSelectedOption();
            dt.add(parseInt(opt.attr('data-interval'), 10), 'minutes');
        } else if (this.id == 'prev') {
            const opt = getSelectedOption();
            dt.add(0 - parseInt(opt.attr('data-interval'), 10), 'minutes');
        } else if (this.id == 'realtime') {
            irealtime = true;
            dt = moment();
        } else {
            dt.add(parseInt($(this).attr('data-offset'), 10), $(this).attr('data-unit'));
        }
        rectifyTime();
        update();
        irealtime = false;
        return false;
    });

    // stop depressed buttons
    $(".btn").mouseup(function () {
        $(this).blur();
    });
}
function refresh() {
    if (irealtime) {
        dt = moment();
        rectifyTime();
        update();
    }
}
function onReady() {
    buildUI();
    $.ajax("/json/products.json", {
        success: (data) => {
            addproducts(data);
        }
    });
    //Start the timer
    window.setTimeout(refresh, 300000);
}

// When ready
$(onReady);
