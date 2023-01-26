
//http://stackoverflow.com/questions/5802461/javascript-which-browsers-support-parsing-of-iso-8601-date-string-with-date-par
(() => {
    //ISO-8601 Date Matching
    const reIsoDate = /^(\d{4})-(\d{2})-(\d{2})((T)(\d{2}):(\d{2})(:(\d{2})(\.\d*)?)?)?(Z)?$/;
    Date.parseISO = (val) => {
        const m = typeof val === 'string' && val.match(reIsoDate);
        if (m) return new Date(Date.UTC(+m[1], +m[2] - 1, +m[3], +m[6] || 0, +m[7] || 0, +m[9] || 0, parseInt((+m[10]) * 1000) || 0));
        return null;
    }

    //MS-Ajax Date Matching
    const reMsAjaxDate = /^\\?\/Date\((\-?\d+)\)\\?\/$/;
    Date.parseAjax = (val) => {
        const m = typeof val === 'string' && val.match(reMsAjaxDate);
        if (m) return new Date(+m[1]);
        return null;
    }
})();

function text(str) {
    // XSS
    return $("<p>").text(str).html();
}

function fetchtimes(findtime) {
    const cid = $('select[name=cid]').val();
    const mydate = $('#realdate').val();
    $('select[name=times]').html("<option value='-1'>Loading...</option>");
    $.getJSON(`/json/webcam.py?cid=${cid}&date=${mydate}`, function (data) {
        let html = '';
        const len = data.images.length;
        for (var i = 0; i < len; i++) {
            let ts = Date.parseISO(data.images[i].valid);

            let result = new Array();
            result[0] = $.datepicker.formatDate('M dd ', ts);
            if (ts.getHours() > 12) {
                result[2] = ts.getHours() - 12;
            } else if (ts.getHours() == 0) {
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
        if (len == 0) {
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
    const href = text($('select[name=times]').val());
    if (href && href != '-1') {
        const fn = href.split('/');
        window.location.href = `#${fn[fn.length - 1]}`;
        $('#theimage').attr('src', href);
    }
}

$(document).ready(function () {
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
            var dstr = `${tpart.substr(4, 2)}/${tpart.substr(6, 2)}/${tpart.substr(0, 4)}`;
            $("#datepicker").datepicker("setDate", new Date(dstr)); // mm/dd/yyyy
            var isotime = `${tpart.substr(0, 4)}-${tpart.substr(4, 2)}-${tpart.substr(6, 2)}T${tpart.substr(8, 2)}:${tpart.substr(10, 2)}:00Z`;
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
