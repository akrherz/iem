import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.js';
import { requireElement } from '/js/iemjs/domUtils.js';

document.addEventListener('DOMContentLoaded', () => {
    const tableElement = requireElement('table1');

    // Get existing table headers
    const headers = Array.from(tableElement.querySelectorAll('thead th')).map(th => th.textContent.trim());
    
    window.hs = new Tabulator(tableElement, {
        layout: "fitColumns",
        pagination: "local",
        paginationSize: 25,
        headerFilter: true,
        columns: headers.map((header, index) => ({
            title: header,
            field: `col_${index}`,
            formatter: index === 1 || index === 2 ? "html" : undefined,
        })),
    });
});
