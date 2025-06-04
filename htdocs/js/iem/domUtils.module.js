// DOM utility functions to reduce boilerplate

/**
 * Escape HTML special characters to prevent XSS attacks
 * @param {string} val - String to escape
 * @returns {string} HTML-escaped string
 */
export function escapeHTML(val) {
    return val
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Safely get an element by ID with type checking
 * @param {string} id - Element ID
 * @param {Function} [ElementType] - Expected element constructor (e.g., HTMLInputElement)
 * @returns {HTMLElement | null} The element or null if not found/wrong type
 */
export function getElement(id, ElementType) {
    const element = document.getElementById(id);
    if (!element) {
        return null;
    }
    
    // If no ElementType provided, return as HTMLElement
    if (!ElementType) {
        return element;
    }
    
    if (!(element instanceof ElementType)) {
        return null;
    }
    return element;
}

/**
 * Get an element and throw if not found (for required elements)
 * @param {string} id - Element ID
 * @param {Function} [ElementType] - Expected element constructor
 * @returns {HTMLElement} The element (guaranteed to exist)
 * @throws {Error} If element not found or wrong type
 */
export function requireElement(id, ElementType) {
    const element = getElement(id, ElementType);
    if (!element) {
        throw new Error(`Required element '${id}' not found or wrong type`);
    }
    return element;
}

// Specialized helper functions for common element types

/**
 * Get an input element by ID
 * @param {string} id - Element ID
 * @returns {HTMLInputElement | null}
 */
export function getInputElement(id) {
    return /** @type {HTMLInputElement | null} */ (getElement(id, HTMLInputElement));
}

/**
 * Get a required input element by ID
 * @param {string} id - Element ID
 * @returns {HTMLInputElement}
 * @throws {Error} If element not found or wrong type
 */
export function requireInputElement(id) {
    return /** @type {HTMLInputElement} */ (requireElement(id, HTMLInputElement));
}

/**
 * Get a select element by ID
 * @param {string} id - Element ID
 * @returns {HTMLSelectElement | null}
 */
export function getSelectElement(id) {
    return /** @type {HTMLSelectElement | null} */ (getElement(id, HTMLSelectElement));
}

/**
 * Get a required select element by ID
 * @param {string} id - Element ID
 * @returns {HTMLSelectElement}
 * @throws {Error} If element not found or wrong type
 */
export function requireSelectElement(id) {
    return /** @type {HTMLSelectElement} */ (requireElement(id, HTMLSelectElement));
}

/**
 * Get a button element by ID
 * @param {string} id - Element ID
 * @returns {HTMLButtonElement | null}
 */
export function getButtonElement(id) {
    return /** @type {HTMLButtonElement | null} */ (getElement(id, HTMLButtonElement));
}

/**
 * Get a required button element by ID
 * @param {string} id - Element ID
 * @returns {HTMLButtonElement}
 * @throws {Error} If element not found or wrong type
 */
export function requireButtonElement(id) {
    return /** @type {HTMLButtonElement} */ (requireElement(id, HTMLButtonElement));
}

/**
 * Get multiple elements by ID with type checking
 * @param {string[]} ids - Array of element IDs
 * @param {Function} [ElementType] - Expected element constructor
 * @returns {(HTMLElement | null)[]} Array of elements (null for missing/wrong type)
 */
export function getElements(ids, ElementType) {
    return ids.map(id => getElement(id, ElementType));
}

/**
 * Get multiple required elements by ID
 * @param {string[]} ids - Array of element IDs
 * @param {Function} [ElementType] - Expected element constructor
 * @returns {HTMLElement[]} Array of elements (guaranteed to exist)
 * @throws {Error} If any element not found or wrong type
 */
export function requireElements(ids, ElementType) {
    return ids.map(id => requireElement(id, ElementType));
}

/**
 * Add event listeners to multiple elements by ID
 * @param {string[]} ids - Array of element IDs
 * @param {string} event - Event type
 * @param {EventListener} handler - Event handler
 * @param {Function} [ElementType] - Expected element constructor
 */
export function addEventListeners(ids, event, handler, ElementType) {
    ids.forEach(id => {
        const element = getElement(id, ElementType);
        if (element) {
            element.addEventListener(event, handler);
        }
    });
}

/**
 * Get value from a form element safely
 * @param {string} id - Element ID
 * @param {string} [defaultValue=''] - Default value if element not found
 * @returns {string} Element value or default
 */
export function getElementValue(id, defaultValue = '') {
    const element = getInputElement(id);
    return element ? element.value : defaultValue;
}

/**
 * Set value on a form element safely
 * @param {string} id - Element ID
 * @param {string} value - Value to set
 * @returns {boolean} True if successful
 */
export function setElementValue(id, value) {
    const element = getInputElement(id);
    if (element) {
        element.value = value;
        return true;
    }
    return false;
}

/**
 * Interface for elements that have been enhanced with TomSelect
 * @typedef {HTMLElement & { tomselect: import('tom-select').default }} TomSelectElement
 */

/**
 * Get an element that has been enhanced with TomSelect
 * @param {string} id - Element ID
 * @returns {TomSelectElement | null}
 */
export function getTomSelectElement(id) {
    const element = getElement(id);
    if (element && 'tomselect' in element) {
        return /** @type {TomSelectElement} */ (element);
    }
    return null;
}

/**
 * Get a required element that has been enhanced with TomSelect
 * @param {string} id - Element ID
 * @returns {TomSelectElement}
 * @throws {Error} If element not found or doesn't have tomselect property
 */
export function requireTomSelectElement(id) {
    const element = getTomSelectElement(id);
    if (!element) {
        throw new Error(`Required TomSelect element '${id}' not found or not initialized`);
    }
    return element;
}
