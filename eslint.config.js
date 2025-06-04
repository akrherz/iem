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
                },
                {
                    "selector": "ArrowFunctionExpression > AssignmentExpression",
                    "message": "Avoid assignment operations in arrow function implicit returns. Use block statements with curly braces for side effects."
                },
                {
                    "selector": "CallExpression > Identifier[name='undefined']:last-child",
                    "message": "Avoid explicitly passing 'undefined' as the last argument. Omit the argument instead - it defaults to undefined."
                },
                {
                    "selector": "IfStatement[test.type='LogicalExpression'][test.operator='&&'][test.left.type='Identifier'][test.right.type='MemberExpression']",
                    "message": "Use optional chaining (?.) instead of && for null checks before property access."
                }
            ],
            
            // Code quality
            "eqeqeq": "error",
            "no-console": "warn",
            "no-debugger": "error",
            
            // Variable shadowing detection
            "no-shadow": ["error", { 
                "builtinGlobals": false,
                "hoist": "functions",
                "allow": ["err", "error", "resolve", "reject", "cb", "callback", "done"]
            }],
            
            // Duplicate assignment detection
            "no-self-assign": "error",
            "no-sequences": "error",
            "no-unreachable": "error",
            
            // Additional code quality rules to catch common issues
            "no-implicit-coercion": "warn",
            "no-return-assign": "error",
            "array-callback-return": "error",
            "no-unused-expressions": ["error", { "allowShortCircuit": true, "allowTernary": true }],
            
            // Avoid usage of `this` in JavaScript code (IEM rule)
            "no-invalid-this": "error",
            "consistent-this": ["error", "self"],
            
            // Disable some rules that might be too strict for legacy code
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
            
            // Deprecated method warnings for modules too
            "no-restricted-syntax": [
                "warn",
                {
                    "selector": "CallExpression[callee.property.name='substr']",
                    "message": "substr() is deprecated. Use substring() or slice() instead."
                },
                {
                    "selector": "ArrowFunctionExpression > AssignmentExpression",
                    "message": "Avoid assignment operations in arrow function implicit returns. Use block statements with curly braces for side effects."
                },
                {
                    "selector": "CallExpression > Identifier[name='undefined']:last-child",
                    "message": "Avoid explicitly passing 'undefined' as the last argument. Omit the argument instead - it defaults to undefined."
                },
                {
                    "selector": "IfStatement[test.type='LogicalExpression'][test.operator='&&'][test.left.type='Identifier'][test.right.type='MemberExpression']",
                    "message": "Use optional chaining (?.) instead of && for null checks before property access."
                }
            ],
            
            // Code quality
            "eqeqeq": "error",
            "no-console": "warn",
            "no-debugger": "error",
            
            // Variable shadowing detection  
            "no-shadow": ["error", { 
                "builtinGlobals": false,
                "hoist": "functions",
                "allow": ["err", "error", "resolve", "reject", "cb", "callback", "done"]
            }],
            
            // Duplicate assignment detection
            "no-self-assign": "error",
            "no-sequences": "error",
            
            // Additional code quality rules (stricter for modules)
            "no-implicit-coercion": "error",
            "no-return-assign": "error", 
            "array-callback-return": "error",
            "no-unused-expressions": ["error", { "allowShortCircuit": true, "allowTernary": true }],
            
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
