// Global type declarations for IEM project
// This file provides type definitions for global libraries

// OpenLayers is loaded as a global script, so we declare it as a global
// Note: We could use import type from 'ol' if we converted to ES modules
declare const ol: typeof import('ol');

// Other global declarations
declare const iemdata: any;
declare const moment: any;
declare const google: any;
