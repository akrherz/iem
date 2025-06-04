# iemjs Tests

This directory contains tests for the iemjs package.

## Test Files

- **`test-imports.js`** - Validates ES module imports and function exports
- **`test-exports.js`** - Validates package.json exports and file structure  
- **`runner.js`** - Test runner with nice output formatting

## Running Tests

```bash
# Run all tests
npm test

# Run individual test suites
npm run test:syntax   # JavaScript syntax validation
npm run test:imports  # ES module import validation
npm run test:exports  # Package structure validation

# Run with the fancy test runner
node tests/runner.js
```

## Test Coverage

The test suite validates:

✅ **Syntax** - All JavaScript files are syntactically valid
✅ **Imports** - ES modules import correctly and export expected functions
✅ **Exports** - package.json exports configuration is valid
✅ **Structure** - All referenced files exist and package metadata is complete
✅ **Cross-platform** - Tests run on Linux, Windows, and macOS (via CI)

## Adding New Tests

When adding new utility functions to iemjs:

1. Add function validation to `test-imports.js`
2. Update expected exports in package.json if needed
3. Run `npm test` to ensure everything works
