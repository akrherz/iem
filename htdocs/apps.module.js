
// Vanilla JS table filter for #table1 using #appFilter
window.addEventListener('DOMContentLoaded', () => {
    const filterInput = document.getElementById('appFilter');
    const table = document.getElementById('table1');
    if (!filterInput || !table) return;
    filterInput.addEventListener('input', (event) => {
        const filter = event.target.value.trim().toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = filter === '' || text.includes(filter) ? '' : 'none';
        });
    });
});
