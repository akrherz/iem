/**
 * @fileoverview Iowa Environmental Mesonet JavaScript Utilities
 * Main entry point for the IEM JS package
 */

// Re-export all utilities for convenient importing
export * from './domUtils.js';

// Re-export iemdata - both individual exports and legacy object
export { 
    vtec_phenomena,
    vtec_significance,
    wfos,
    states
} from './iemdata.js';
