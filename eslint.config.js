// Legacy CommonJS ESLint configuration for pre-commit compatibility
const js = require("@eslint/js");
const globals = require("globals");

module.exports = [
    // Configuration for ESLint config file itself (Node.js environment)
    {
        files: ["eslint.config.js"],
        languageOptions: {
            ecmaVersion: 2020,
            sourceType: "script",
            globals: {
                ...globals.node
            }
        },
        rules: {
            "no-console": "off"
        }
    },
    // Ignore other problematic files
    {
        ignores: ["htdocs/vtec/assets/*.js", "htdocs/lsr/static.js"]
    },
    js.configs.recommended,
    // Configuration for traditional script files (.js)
    {
        files: ["**/*.js"],
        ignores: ["src/iemjs/**/*.js"],
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
                "flowplayer": "readonly",
                "bootstrap": "readonly"
            }
        },
        rules: {
            // jQuery prohibition rules
            "no-restricted-globals": [
                "warn",
                {
                    "name": "$",
                    "message": "jQuery should not be used. Use vanilla JavaScript instead."
                },
                {
                    "name": "jQuery",
                    "message": "jQuery should not be used. Use vanilla JavaScript instead."
                }
            ],

            // Modernization hints
            "no-restricted-syntax": [
                "warn",
                {
                    "selector": "CallExpression[callee.property.name='substr']",
                    "message": "substr() is deprecated. Use substring() or slice() instead."
                },
                {
                    "selector": "CallExpression > Identifier[name='undefined']:last-child",
                    "message": "Avoid explicitly passing 'undefined' as the last argument. Omit the argument instead - it defaults to undefined."
                },
                // Encourage optional chaining over && in conditionals
                {
                    "selector": "IfStatement[test.type='LogicalExpression'][test.operator='&&'][test.right.type='MemberExpression']",
                    "message": "Use optional chaining (?.) instead of && for null checks before property access."
                },
                {
                    "selector": "IfStatement[test.type='LogicalExpression'][test.operator='&&'][test.right.type='CallExpression'][test.right.callee.type='MemberExpression']",
                    "message": "Use optional chaining (?.) instead of && for null checks before method calls."
                },
                {
                    "selector": "ConditionalExpression[test.type='LogicalExpression'][test.operator='&&'][test.right.type='MemberExpression']",
                    "message": "Use optional chaining (?.) instead of && in conditional expressions for property access."
                },
                {
                    "selector": "ConditionalExpression[test.type='LogicalExpression'][test.operator='&&'][test.right.type='CallExpression'][test.right.callee.type='MemberExpression']",
                    "message": "Use optional chaining (?.) instead of && in conditional expressions for method calls."
                },
                {
                    "selector": "IfStatement[consequent.type='BlockStatement'][consequent.body.length=1][consequent.body.0.type='ReturnStatement'][consequent.body.0.argument.type='Literal'][consequent.body.0.argument.value=true][alternate.type='BlockStatement'][alternate.body.length=1][alternate.body.0.type='ReturnStatement'][alternate.body.0.argument.type='Literal'][alternate.body.0.argument.value=false]",
                    "message": "Found complex boolean return - return the boolean expression directly instead of if/else with true/false."
                },
                {
                    "selector": "IfStatement[consequent.type='ReturnStatement'][consequent.argument.type='Literal'][consequent.argument.value=true][alternate.type='ReturnStatement'][alternate.argument.type='Literal'][alternate.argument.value=false]",
                    "message": "Found complex boolean return - return the boolean expression directly instead of if/else with true/false."
                },
                {
                    "selector": "TemplateLiteral[expressions.length=0]",
                    "message": "Template Literal Found - use single quotes instead of template literals when no interpolation is needed."
                }
            ],

            // Code quality
            "eqeqeq": "error",
            "no-console": "warn",
            "no-debugger": "error",
            "one-var": ["error", "never"], // Require one variable declaration per line
            "init-declarations": ["error", "always"], // Require variables to be initialized when declared
            "object-shorthand": "warn", // Use shorthand property syntax for object literals (e.g., {foo} instead of {foo: foo})


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

            // Block-scoped declarations
            "no-inner-declarations": ["error", "both"], // Function or var declarations in nested blocks is not preferred

            // Additional code quality rules to catch common issues
            "no-implicit-coercion": "warn",
            "no-return-assign": "error",
            "array-callback-return": "error",
            "no-unused-expressions": ["error", { "allowShortCircuit": true, "allowTernary": true }],
            "prefer-arrow-callback": "warn", // Consider using arrow functions for callbacks
            "prefer-template": "warn", // Template Literal Found - use template literals instead of string concatenation
            "prefer-const": "warn", // Use const declarations for variables that are never reassigned
            "default-case": "warn", // No default cases in switch statements
            "complexity": ["warn", { "max": 15 }], // Function with cyclomatic complexity higher than threshold
            "no-unused-vars": ["warn", {
                "vars": "all",
                "args": "after-used",
                "ignoreRestSiblings": false,
                "argsIgnorePattern": "^_",
                "varsIgnorePattern": "^_",
                "caughtErrors": "all"
            }], // Found unused objects

            // Avoid usage of `this` in JavaScript code (IEM rule)
            "no-invalid-this": "error",
            "consistent-this": ["error", "self"],
            "class-methods-use-this": "warn", // Warn when class methods don't use `this` and could be static

            // Disable some rules that might be too strict for legacy code
            "no-redeclare": "off"
        }
    },

    // Configuration for ES modules (.module.js and IEM utilities)
    {
        files: ["**/*.module.js", "src/iemjs/**/*.js"],
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: "module",
            globals: {
                ...globals.browser
            }
        },
        rules: {
            // Base ES5+ compliance rules
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
            "prefer-const": "error", // Use const declarations for variables that are never reassigned
            "object-shorthand": "error",
            "no-return-await": "error", // Prevent unnecessary return await (performance issue)


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
                },
                {
                    "selector": "IfStatement[test.type='LogicalExpression'][test.operator='&&'][test.left.type='Identifier'][test.right.type='CallExpression'][test.right.callee.type='MemberExpression']",
                    "message": "Use optional chaining (?.) instead of && for null checks before method calls."
                },
                {
                    "selector": "IfStatement[consequent.type='BlockStatement'][consequent.body.length=1][consequent.body.0.type='ReturnStatement'][consequent.body.0.argument.type='Literal'][consequent.body.0.argument.value=true][alternate.type='BlockStatement'][alternate.body.length=1][alternate.body.0.type='ReturnStatement'][alternate.body.0.argument.type='Literal'][alternate.body.0.argument.value=false]",
                    "message": "Found complex boolean return - return the boolean expression directly instead of if/else with true/false."
                },
                {
                    "selector": "IfStatement[consequent.type='ReturnStatement'][consequent.argument.type='Literal'][consequent.argument.value=true][alternate.type='ReturnStatement'][alternate.argument.type='Literal'][alternate.argument.value=false]",
                    "message": "Found complex boolean return - return the boolean expression directly instead of if/else with true/false."
                },
                {
                    "selector": "TemplateLiteral[expressions.length=0]",
                    "message": "Template Literal Found - use single quotes instead of template literals when no interpolation is needed."
                }
            ],

            // Code quality
            "eqeqeq": "error",
            "no-console": "warn",
            "no-debugger": "error",
            "one-var": ["error", "never"], // Require one variable declaration per line
            "init-declarations": ["error", "always"], // Require variables to be initialized when declared

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

            // Block-scoped declarations
            "no-inner-declarations": ["error", "both"], // Function or var declarations in nested blocks is not preferred

            // Additional code quality rules (stricter for modules)
            "no-implicit-coercion": "error",
            "no-return-assign": "error",
            "array-callback-return": "error",
            "no-unused-expressions": ["error", { "allowShortCircuit": true, "allowTernary": true }],
            "require-await": "error", // Async functions must contain await expressions
            "default-case": "error", // No default cases in switch statements
            "complexity": ["error", { "max": 15 }], // Function with cyclomatic complexity higher than threshold
            "no-unused-vars": ["error", {
                "vars": "all",
                "args": "after-used",
                "ignoreRestSiblings": false,
                "argsIgnorePattern": "^_",
                "varsIgnorePattern": "^_",
                "caughtErrors": "all"
            }], // Found unused objects

            // Avoid usage of `this` in JavaScript code (IEM rule)
            "no-invalid-this": "error",
            "consistent-this": ["error", "self"],

            // Disable some rules that might be too strict
            "no-redeclare": "off"
        }
    },

    // Configuration for test files - allow console usage for test output
    {
        files: ["**/tests/**/*.js", "**/*.test.js", "**/*.spec.js"],
        languageOptions: {
            globals: {
                ...globals.node  // Add Node.js globals like process, Buffer, etc.
            }
        },
        rules: {
            "no-console": "off",  // Console output is essential for test feedback
            "require-await": "off",  // Test runners often have async functions with await in loops
            "complexity": ["error", { "max": 30 }], // Function with cyclomatic complexity higher than threshold
        }
    }
];
