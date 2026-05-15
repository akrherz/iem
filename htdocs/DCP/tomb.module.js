
// Vanilla JS table filter for #table1
document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('table1');
    if (!table) {return;}
    const rows = [...table.tBodies[0].rows];

    const updateCount = (countNode, visible, total) => {
        countNode.textContent = `${visible} of ${total} rows shown`;
    };

    // Create filter input
    const filterDiv = document.createElement('div');
    filterDiv.className = 'row g-2 align-items-end mb-3';
    const controlCol = document.createElement('div');
    controlCol.className = 'col-sm-8 col-md-6 col-lg-4';
    const label = document.createElement('label');
    label.textContent = 'Filter Table By';
    label.setAttribute('for', 'table1-filter');
    label.className = 'form-label';
    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'table1-filter';
    input.className = 'form-control';
    input.setAttribute('placeholder', 'Filter by NWSLI, source, or product');
    input.setAttribute('aria-describedby', 'table1-filter-count');
    const count = document.createElement('div');
    count.id = 'table1-filter-count';
    count.className = 'form-text';
    label.appendChild(input);
    controlCol.appendChild(label);
    controlCol.appendChild(count);
    filterDiv.appendChild(controlCol);

    // Insert filter above table
    table.parentNode.insertBefore(filterDiv, table);
    updateCount(count, rows.length, rows.length);

    input.addEventListener('input', () => {
        const filter = input.value.trim().toLowerCase();
        let visibleRows = 0;
        for (const row of rows) {
            const text = row.textContent.toLowerCase();
            const matches = filter === '' || text.includes(filter);
            row.style.display = matches ? '' : 'none';
            if (matches) {
                visibleRows += 1;
            }
        }
        updateCount(count, visibleRows, rows.length);
    });
});
