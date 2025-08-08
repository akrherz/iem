/* global TomSelect */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.iemselect2').forEach(el => {
        // Check if the original element has width styling
        const computedStyle = window.getComputedStyle(el);
        const inlineStyle = el.style.minWidth || el.style.width;
        
        const config = {
            searchField: ['text', 'value'],
            maxOptions: 1000,
            allowEmptyOption: false,
            selectOnTab: false,
        };
        
        const ts = new TomSelect(el, config);
        let defaultValue = null;
        ts.on("dropdown_open", () => {
            defaultValue = ts.getValue();
            // Clear out the search field
            ts.clear();
        });
        ts.on("dropdown_close", () => {
            // Reset if no options are selected
            if (ts.getValue().length === 0) {
                ts.setValue(defaultValue);
            }
        });
        
        // Apply width from original element if it exists
        if (inlineStyle || computedStyle.minWidth !== 'auto') {
            const wrapper = ts.wrapper;
            if (inlineStyle) {
                if (el.style.minWidth) wrapper.style.minWidth = el.style.minWidth;
                if (el.style.width) wrapper.style.width = el.style.width;
            }
        }
        
        window.ts = ts;
    });
});
