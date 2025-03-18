/* global $ */

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

$(document).ready(() => {
    $("#save").click(() => {
        const content = $("#datatable").text().split(/\\n/).slice(2).join("\\n");

        const link = document.createElement('a');
        link.setAttribute('download', 'isusm.csv');
        link.setAttribute('href', `data:text/plain;charset=utf-8,${escapeHTML(content)}`);
        link.click(); 
    });
});