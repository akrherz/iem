/* global $ */
$(document).ready(() => {
    $("#save").click(() => {
        const content = $("#datatable").text().split(/\\n/).slice(2).join("\\n");

        const link = document.createElement('a');
        link.setAttribute('download', 'isusm.csv');
        link.setAttribute('href', `data:text/plain;charset=utf-8,${encodeURIComponent(content)}`);
        link.click(); 
    });
});