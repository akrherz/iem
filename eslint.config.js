import js from "@eslint/js";
import globals from "globals";

export default [
    js.configs.recommended,
    // Configuration for traditional script files (.js)
    {
        files: ["**/*.js"],
        languageOptions: {
            ecmaVersion: 2020,
            sourceType: "script",
            globals: {
                ...globals.browser,
                // Prohibited globals (set to false to trigger errors)
                "$": false,
                "jQuery": false,
                // Allowed globals for traditional scripts
                "ol": "readonly",
                "Ext": "readonly",
                "iemdata": "readonly",
                "moment": "readonly",
                "google": "readonly",
                "flowplayer": "readonly"
            }
        },
        rules: {
            // Enforce your coding rules
            "no-undef": "error",
            "no-unused-vars": "warn",
            "prefer-const": "error",
            "no-var": "error",
            
            // jQuery prohibition rules
            "no-restricted-globals": [
                "error",
                {
                    "name": "someday$",
                    "message": "jQuery should not be used. Use vanilla JavaScript instead."
                },
                {
                    "name": "somedayjQuery",
                    "message": "jQuery should not be used. Use vanilla JavaScript instead."
                }
            ],
            
            // Modern JavaScript preferences
            "prefer-arrow-callback": "warn",
            "prefer-template": "warn",
            "object-shorthand": "warn",
            
            // Deprecated method warnings
            "no-restricted-syntax": [
                "warn",
                {
                    "selector": "CallExpression[callee.property.name='substr']",
                    "message": "substr() is deprecated. Use substring() or slice() instead."
                }
            ],
            
            // Code quality
            "eqeqeq": "error",
            "no-console": "warn",
            "no-debugger": "error",
            
            // Avoid usage of `this` in JavaScript code (IEM rule)
            "no-invalid-this": "error",
            "consistent-this": ["error", "self"],
            
            // Disable some rules that might be too strict for legacy code
            "no-redeclare": "off"
        }
    },
    // Special configuration for ExtJS files
    {
        files: ["**/DCP/plot.js", "**/*extjs*.js", "**/*ext*.js"],
        languageOptions: {
            ecmaVersion: 2020,
            sourceType: "script",
            globals: {
                ...globals.browser,
                // Prohibited globals
                "$": false,
                "jQuery": false,
                // Allowed globals for ExtJS
                "Ext": "readonly",
                "ol": "readonly"
            }
        },
        rules: {
            // Basic rules still apply
            "no-undef": "error",
            "no-unused-vars": "warn",
            "prefer-const": "error",
            "no-var": "error",
            "eqeqeq": "error",
            "no-console": "warn",
            "no-debugger": "error",
            
            // jQuery prohibition still applies
            "no-restricted-globals": [
                "error",
                {
                    "name": "$",
                    "message": "jQuery should not be used. Use vanilla JavaScript instead."
                },
                {
                    "name": "jQuery",
                    "message": "jQuery should not be used. Use vanilla JavaScript instead."
                }
            ],
            
            // ALLOW `this` usage in ExtJS files - framework requires it
            "no-invalid-this": "off",
            "consistent-this": "off",
            
            // ExtJS uses function declarations extensively
            "prefer-arrow-callback": "off",
            
            // ExtJS has its own patterns that may conflict with modern rules
            "no-redeclare": "off"
        }
    },
    // Configuration for ES Module files (.mjs)
    {
        files: ["**/*.module.js"],
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: "module",
            globals: {
                ...globals.browser,
                // Prohibited globals (jQuery should not be used in modules either)
                "$": false,
                "jQuery": false
            }
        },
        rules: {
            // All the same rules as scripts, plus module-specific ones
            "no-undef": "error",
            "no-unused-vars": "warn",
            "prefer-const": "error",
            "no-var": "error",
            
            // jQuery prohibition rules
            "no-restricted-globals": [
                "error",
                {
                    "name": "$",
                    "message": "jQuery should not be used. Use vanilla JavaScript instead."
                },
                {
                    "name": "jQuery", 
                    "message": "jQuery should not be used. Use vanilla JavaScript instead."
                }
            ],
            
            // Modern JavaScript preferences (more strict for modules)
            "prefer-arrow-callback": "error",
            "prefer-template": "error",
            "object-shorthand": "error",
            
            // Code quality
            "eqeqeq": "error",
            "no-console": "warn",
            "no-debugger": "error",
            
            // Avoid usage of `this` in JavaScript code (IEM rule) - stricter for modules
            "no-invalid-this": "error",
            "consistent-this": ["error", "self"]
        }
    },
    
    // Configuration for config files (like this file)
    {
        files: ["*.config.js", "*.config.mjs"],
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: "module",
            globals: {
                ...globals.node
            }
        },
        rules: {
            "no-undef": "error",
            "no-unused-vars": "warn",
            "prefer-const": "error",
            "no-var": "error"
        }
    }
];
