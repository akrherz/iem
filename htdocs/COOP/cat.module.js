// Vanilla JavaScript - no jQuery
let currentmode = true;

/**
 * Toggle visibility of table rows without data
 */
function hiderows() {
    const noDataRows = document.querySelectorAll('tr.nodata');
    const rowShower = document.getElementById('rowshower');
    
    if (currentmode) {
        noDataRows.forEach(row => {
            row.style.display = 'none';
        });
        if (rowShower) {
            rowShower.value = 'Show rows without data';
        }
    } else {
        noDataRows.forEach(row => {
            row.style.display = '';
        });
        if (rowShower) {
            rowShower.value = 'Hide rows without data';
        }
    }
    currentmode = !currentmode;
}

document.addEventListener('DOMContentLoaded', () => {
    const rowShower = document.getElementById('rowshower');
    if (rowShower) {
        rowShower.addEventListener('click', hiderows);
    }
});