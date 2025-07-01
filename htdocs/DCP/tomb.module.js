
// Vanilla JS table filter for #table1
document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('table1');
    if (!table) return;

    // Create filter input
    const filterDiv = document.createElement('div');
    filterDiv.className = 'mb-2';
    const label = document.createElement('label');
    label.textContent = 'Filter Table By: ';
    label.setAttribute('for', 'table1-filter');
    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'table1-filter';
    input.className = 'form-control form-control-sm d-inline-block';
    input.style.width = '200px';
    label.appendChild(input);
    filterDiv.appendChild(label);

    // Insert filter above table
    table.parentNode.insertBefore(filterDiv, table);

    input.addEventListener('input', () => {
        const filter = input.value.trim().toLowerCase();
        const rows = table.tBodies[0].rows;
        for (const row of rows) {
            const text = row.textContent.toLowerCase();
            row.style.display = filter === '' || text.includes(filter) ? '' : 'none';
        }
    });
});
