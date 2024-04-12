/* global Cookies */
/*
 * NWS Text Product Finder
 *  - uses cookies and hashlinks to save info
 */
const NO_DATE_SET = 'No Limit';

function text(str){
    // XSS shim
    return $("<p>").text(str).html();
}

function readAnchorTags() {
    const tokens = window.location.href.split("#");
    if (tokens.length !== 2) {
        return;
    }
    $(text(tokens[1]).split(",")).each((_idx, pil_limit) => {
        const tokens2 = pil_limit.split("-");
        if (tokens2.length === 1) {
            tokens2.push(1);
        }
        addTab(text(tokens2[0]), "", "", text(tokens2[1]), NO_DATE_SET, NO_DATE_SET, false);
    });
}
function readCookies() {
    const afospils = Cookies.get('afospils');
    if (afospils === undefined || afospils === '') {
        return;
    }
    $(afospils.split(",")).each((_idx, pil_limit) => {
        const tokens = pil_limit.split("-");
        if (tokens.length == 1) {
            tokens.push(1);
        }
        addTab(tokens[0], "", "", tokens[1], NO_DATE_SET, NO_DATE_SET, false);
    });
}
function saveCookies() {
    const afospils = [];
    $(".nav-tabs li[data-pil]").each((_idx, li) => {
        // these are currently temporary
        if ($(li).data('sdate') != NO_DATE_SET) {
            return;
        }
        afospils.push(`${$(li).data('pil')}-${$(li).data('limit')}`);
    });

    Cookies.set('afospils', afospils.join(","), {
        'path': '/wx/afos/',
        'expires': 3650
    });
    window.location.href = `#${afospils.join(",")}`;
};

function loadTabContent(div, pil, center, ttaaii, limit, sdate, edate) {
    div.html('<img src="/images/wait24trans.gif"> Searching the database ...');
    sdate = (sdate === NO_DATE_SET) ? "" : sdate;
    edate = (edate === NO_DATE_SET) ? "" : edate;
    $.ajax({
        method: 'GET',
        url: `/cgi-bin/afos/retrieve.py?fmt=html&pil=${pil}&center=${center}&limit=${limit}&sdate=${sdate}&edate=${edate}&ttaaii=${ttaaii}`,
        success: (txt) => {
            div.html(txt);
        },
        failure: (txt) => {
            div.html(txt);
        }
    });
}

function refreshActiveTab() {
    //refresh the content found in the active tab
    const pil = $(".nav-tabs li.active").data('pil');
    const limit = $(".nav-tabs li.active").data('limit');
    const center = $(".nav-tabs li.active").data('center');
    const ttaaii = $(".nav-tabs li.active").data('ttaaii');
    const sdate = $(".nav-tabs li.active").data('sdate');
    const edate = $(".nav-tabs li.active").data('edate');
    if (pil === undefined) {
        return;
    }
    const tabid = $(".nav-tabs li.active a").attr('href');
    const tabdiv = $(tabid);
    loadTabContent(tabdiv, pil, center, ttaaii, limit, sdate, edate);
}

function addTab(pil, center, ttaaii, limit, sdate, edate, doCookieSave) {
    // Make sure the pil is something
    if (pil === null || pil === "") {
        return;
    }
    // Make sure this isn't a dup
    if ($(`#thetabs .nav-tabs li[data-pil='${pil}']`).length > 0) {
        return;
    }
    const pos = $(".nav-tabs").children().length;
    $("#thetabs .nav-tabs").append(`<li data-center="${text(center)}" data-sdate="${text(sdate)}" data-edate="${text(edate)}" data-ttaaii="${text(ttaaii)}" data-limit="${text(limit)}" data-pil="${text(pil)}"><a href="#tab${pos}" data-toggle="tab">${text(pil)}</a></li>`);
    $('.tab-content').append(`<div class="tab-pane" id="tab${pos}"></div>`);
    const newdiv = $(`#tab${pos}`);
    $(`.nav-tabs li:nth-child(${pos + 1}) a`).click();
    loadTabContent(newdiv, pil, center, ttaaii, limit, sdate, edate);
    if (doCookieSave) {
        saveCookies();
    }
}
// eslint-disable-next-line no-unused-vars
function dlbtn(btn, fmt) {
    const pil = $(".nav-tabs li.active").data('pil');
    if (pil === undefined) {
        return;
    }
    const limit = $(".nav-tabs li.active").data('limit');
    const center = $(".nav-tabs li.active").data('center');
    const ttaaii = $(".nav-tabs li.active").data('ttaaii');
    let sdate = $(".nav-tabs li.active").data('sdate');
    let edate = $(".nav-tabs li.active").data('edate');
    sdate = (sdate === NO_DATE_SET) ? "" : sdate;
    edate = (edate === NO_DATE_SET) ? "" : edate;
    window.location = `/cgi-bin/afos/retrieve.py?dl=1&fmt=${fmt}&pil=${pil}&center=${center}&limit=${limit}&sdate=${sdate}&edate=${edate}&ttaaii=${ttaaii}`;
    $(btn).blur();
}
function buildUI() {
    // listen for refresh clicks
    $("#toolbar-refresh").click(function () { // this
        refreshActiveTab();
        $(this).blur();
    });
    // Print!
    $("#toolbar-print").click(function () { // this
        $(this).blur();
        const pil = $(".nav-tabs li.active").data('pil');
        if (pil === undefined) {
            return;
        }
        const tabid = $(".nav-tabs li.active a").attr('href');
        // https://stackoverflow.com/questions/33732739
        const divToPrint = $(tabid)[0];
        const newWin = window.open('', 'Print-Window');
        newWin.document.open();
        newWin.document.write(`<html><body onload="window.print()">${divToPrint.innerHTML}</body></html>`);
        newWin.document.close();
        setTimeout(() => { newWin.close(); }, 10);
    });
    // Close
    $("#toolbar-close").click(function () { // this
        $(this).blur();
        const pil = $(".nav-tabs li.active").data('pil');
        if (pil === undefined) {
            return;
        }
        const tabid = $(".nav-tabs li.active a").attr('href');
        $(".nav-tabs li.active").remove();
        $(tabid).remove();
        $(".nav-tabs li a").last().click();
        saveCookies();
    });
    $("#myform-submit").click(() => {
        const pil = $("#myform input[name='pil']").val().toUpperCase();
        const center = $("#myform input[name='center']").val().toUpperCase();
        const ttaaii = $("#myform input[name='ttaaii']").val().toUpperCase();
        const limit = parseInt($("#myform input[name='limit']").val(), 10);
        const sdate = $("#sdate").val();
        const edate = $("#edate").val();
        addTab(pil, center, ttaaii, limit, sdate, edate, true);
        $(this).blur();
    });
    $("#sdate").datepicker({
        dateFormat: "yy-m-d",
        minDate: new Date(1983, 0, 1),
        maxDate: new Date(),
        defaultDate: new Date(1983, 0, 1)
    });
    $("#edate").datepicker({
        dateFormat: "yy-m-d",
        minDate: new Date(1983, 0, 2),
        maxDate: new Date(new Date().getTime() + 24 * 60 * 60 * 1000),
        defaultDate: new Date(new Date().getTime() + 24 * 60 * 60 * 1000)
    });
}

$(() => {
    // jquery on-ready
    buildUI();
    readAnchorTags();
    readCookies();
    saveCookies();
});
