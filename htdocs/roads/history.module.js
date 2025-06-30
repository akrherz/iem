// Roads History Tabulator implementation - Bootstrap 5 compatible
import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.js';

document.addEventListener('DOMContentLoaded', () => {
    const tableElement = document.getElementById('table1');

    if (tableElement) {
        // Small delay to ensure DOM is fully rendered
        setTimeout(() => {
            // Get existing table headers
            const headers = Array.from(tableElement.querySelectorAll('thead th')).map(th => th.textContent.trim());
            
            new Tabulator(tableElement, {
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
        }, 100);
    }
});
