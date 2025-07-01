/* global TomSelect */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.iemselect2').forEach((el) => {
        window.ts = new TomSelect(el, {
            searchField: ['text', 'value'],
	    maxOptions: 1000,
            allowEmptyOption: false
        });
    });
});
