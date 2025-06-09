// TypeScript declarations for domUtils.js

/**
 * Escape HTML special characters to prevent XSS attacks
 */
export function escapeHTML(val: string): string;

/**
 * Safely get an element by ID with type checking
 */
export function getElement<T extends HTMLElement = HTMLElement>(
    id: string,
    ElementType?: new (...args: any[]) => T
): T | null;

/**
 * Get an element and throw if not found (for required elements)
 */
export function requireElement<T extends HTMLElement = HTMLElement>(
    id: string,
    ElementType?: new (...args: any[]) => T
): T;

/**
 * Get an input element by ID
 */
export function getInputElement(id: string): HTMLInputElement | null;

/**
 * Get a required input element by ID
 */
export function requireInputElement(id: string): HTMLInputElement;

/**
 * Get a select element by ID
 */
export function getSelectElement(id: string): HTMLSelectElement | null;

/**
 * Get a required select element by ID
 */
export function requireSelectElement(id: string): HTMLSelectElement;

/**
 * Get a button element by ID
 */
export function getButtonElement(id: string): HTMLButtonElement | null;

/**
 * Get a required button element by ID
 */
export function requireButtonElement(id: string): HTMLButtonElement;

/**
 * Get multiple elements by ID with type checking
 */
export function getElements<T extends HTMLElement = HTMLElement>(
    ids: string[],
    ElementType?: new (...args: any[]) => T
): (T | null)[];

/**
 * Get multiple required elements by ID
 */
export function requireElements<T extends HTMLElement = HTMLElement>(
    ids: string[],
    ElementType?: new (...args: any[]) => T
): T[];

/**
 * Add event listeners to multiple elements by ID
 */
export function addEventListeners<T extends HTMLElement = HTMLElement>(
    ids: string[],
    event: string,
    handler: EventListener,
    ElementType?: new (...args: any[]) => T
): void;

/**
 * Get value from a form element safely
 */
export function getElementValue(id: string, defaultValue?: string): string;

/**
 * Set value on a form element safely
 */
export function setElementValue(id: string, value: string): boolean;

/**
 * Interface for elements that have been enhanced with TomSelect
 */
export interface TomSelectElement extends HTMLElement {
    tomselect: any; // Using 'any' since tom-select types may not be available
}

/**
 * Get an element that has been enhanced with TomSelect
 */
export function getTomSelectElement(id: string): TomSelectElement | null;

/**
 * Get a required element that has been enhanced with TomSelect
 */
export function requireTomSelectElement(id: string): TomSelectElement;
