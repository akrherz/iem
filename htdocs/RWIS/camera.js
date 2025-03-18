/* global $ */
//http://stackoverflow.com/questions/5802461/javascript-which-browsers-support-parsing-of-iso-8601-date-string-with-date-par
(() => {
    //ISO-8601 Date Matching
    const reIsoDate = /^(\d{4})-(\d{2})-(\d{2})((T)(\d{2}):(\d{2})(:(\d{2})(\.\d*)?)?)?(Z)?$/;
    Date.parseISO = (val) => {
        if (typeof val !== 'string') return null;
        const mm = val.match(reIsoDate);
        if (mm) return new Date(Date.UTC(Number(mm[1]), Number(mm[2]) - 1, Number(mm[3]), Number(mm[6]) || 0, Number(mm[7]) || 0, Number(mm[9]) || 0, parseInt((Number(mm[10])) * 1000, 10) || 0));
        return null;
    }
})();

/**
 * Replace HTML special characters with their entity equivalents
 * @param string val 
 * @returns string converted string
 */
function escapeHTML(val) {
    return val.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}

function fetchtimes(findtime) {
    const cid = $('select[name=cid]').val();
    const mydate = $('#realdate').val();
    $('select[name=times]').html("<option value='-1'>Loading...</option>");
    $.getJSON(`/json/webcam.py?cid=${cid}&date=${mydate}`, (data) => {
        let html = '';
        const len = data.images.length;
        for (let i = 0; i < len; i++) {
            let ts = Date.parseISO(data.images[i].valid);

            const result = new Array();
            result[0] = $.datepicker.formatDate('M dd ', ts);
            if (ts.getHours() > 12) {
                result[2] = ts.getHours() - 12;
            } else if (ts.getHours() === 0) {
                result[2] = "12";
            } else {
                result[2] = ts.getHours();
            }
            result[3] = (ts.getMinutes() < 10 ? ":0" : ":") + ts.getMinutes();

            if (ts.getHours() >= 12) {
                result[4] = " PM";
            } else {
                result[4] = " AM";
            }

            ts = result.join('');

            html += '<option ts="' + data.images[i].valid + '" value="' + data.images[i].href + '">' + ts + '</option>';
        }
        if (len === 0) {
            html += "<option value='-1'>No Images Found!</option>";
        }
        $('select[name=times]').html(html);
        if (findtime) {
            $(`select[name=times] option[ts="${findtime}"]`).attr('selected', 'selected');
            getimage();
        }
    });
}

function getimage() {
    const href = escapeHTML($('select[name=times]').val());
    if (href && href !== '-1') {
        const fn = href.split('/');
        window.location.href = `#${fn[fn.length - 1]}`;
        $('#theimage').attr('src', href);
    }
}

$(document).ready(() => {
    $("#datepicker").datepicker({
        dateFormat: "DD, d MM, yy",
        altFormat: "yymmdd", altField: "#realdate",
        minDate: new Date(2009, 11, 19)
    });
    $("#datepicker").datepicker('setDate', new Date());

    $('select[name=times]').change(function () {
        getimage();
    });

    // See if we have a anchor HREF already
    let tokens = window.location.href.split("#");
    if (tokens.length === 2) {
        const fn = tokens[1];
        tokens = fn.split("_");
        if (tokens.length === 2) {
            const cid = tokens[0];
            const tpart = tokens[1];
            /* Set camera ID */
            $(`select[name=cid] option[value=${cid}]`).attr("selected", "selected");
            const dstr = `${tpart.substr(4, 2)}/${tpart.substr(6, 2)}/${tpart.substr(0, 4)}`;
            $("#datepicker").datepicker("setDate", new Date(dstr)); // mm/dd/yyyy
            const isotime = `${tpart.substr(0, 4)}-${tpart.substr(4, 2)}-${tpart.substr(6, 2)}T${tpart.substr(8, 2)}:${tpart.substr(10, 2)}:00Z`;
            fetchtimes(isotime);
        } else {
            fetchtimes(false);
        }
    } else {
        fetchtimes(false);
    }

    $('select[name=cid]').change(() => {
        fetchtimes(false);
    });
    $("#datepicker").change(() => {
        fetchtimes(false);
    });

});
