# IEM Repo

Every time you choose to apply a rule(s), explicitly state the rule(s) in the
output. You can abbreviate the rule description to a single word or phrase.

## Code Stack

- PHP 8.4
- Tabulator JavaScript library for interactive tables
- Python 3.14
- PostgreSQL 18
- Bootstrap 5
- OpenLayers for interactive maps

## Code Organization and Abstractions

- Before creating new utility functions, check if similar functionality exists
  in `/htdocs/js/iemjs/` or `/src/iemjs/`.
- When refactoring for complexity, prefer creating reusable abstractions
  in `/htdocs/js/iemjs/` or `/src/iemjs/`.
- Look for patterns that appear across multiple modules and extract them to
  shared utilities.
- When fixing ESLint complexity warnings, prioritize creating shared utilities 
  over module-specific helper functions.
- Always search the codebase for similar patterns before creating new functions.
- Common patterns that should be abstracted:
  - Form validation and input handling
  - URL parameter parsing/updating and hash migration
  - API request handling with error management and loading states
  - DOM element selection and manipulation beyond what's in domUtils.js
  - Date/time formatting and parsing utilities
  - Table/data processing and formatting
  - Keyboard navigation and event handling patterns

## Refactoring Strategy

- When asked to "address complexity", first analyze if the complexity comes from:
  1. **Reusable logic** → extract to shared utilities in `/src/iemjs/`
  2. **Module-specific orchestration** → break into smaller, focused functions
  3. **Repetitive patterns** → create abstractions that multiple modules can use
- Before creating 3+ similar helper functions across different modules, 
  consolidate into a shared utility.
- When creating shared utilities, design them to handle the most common use cases
  across the codebase, not just the immediate problem.

**Note**: This abstraction strategy applies only to ES modules (files using `import`/`export`). 
Legacy JavaScript files should keep complexity-reducing functions within their own modules.

## Rules

- It is not acceptable to rewrite a file by creating a new file and then overwriting
  the original file with the new file.  Instead, you should edit the original file
  directly.
- Jquery should not be used and any instances of it should be replaced
  with vanilla JavaScript.
- Code comments should explain functionality, not detail why the code was
  added.
- JavaScript code should not be embedded in HTML files.
- Jquery-UI should not be used and any instances of it should be replaced
  with vanilla JavaScript.
- Avoid usage of `this` in JavaScript code, as it can lead to confusion
  and bugs. Use arrow functions or bind methods to the correct context instead.
- When you suggest URLs to open for testing, you should use the domain name
  of `iem.local` instead of `localhost`.  HTTPS is required.

## ESLint Usage

- **ALWAYS use `npx eslint <filepath>` for linting individual files.**
- Use the direct ESLint command to get accurate, file-specific linting results.

## Project Context

This repo does a lot of different things with weather data modification.

## Code Style and Structure

```text
cgi-bin/     # One line front end references to pylib application code
config/      # PHP configuration
data/        # Stuff used by PHP and python scripts
deployment/  # Stuff associated with deployment of this code
docs/        # centralized docs
htdocs/      # The apache webroot with mostly PHP stuff and python pointers
             # to things within pylib
├── agclimate/ # ISU Soil Moisture Network
include/     # PHP include scripts
pylib/       # python library stuff used within this repo only
scripts/     # python cron jobs that process data, these are not web accessible
src/iemjs/   # Centralized `iemjs` npm ES package, used by this repo and friends.
             # This is where new utility functions should be added.
tests/       # Python testing code mostly for pylib and for integration tests
```

## Code Quality and Technical Debt

- Avoid creating many small, single-purpose functions when a more general 
  utility would serve multiple modules.
- When fixing the same type of complexity issue across multiple files, 
  step back and create a shared solution.
- If you find yourself writing similar JSDoc comments across different modules,
  that's a signal the functionality should be abstracted.
- Consider the maintenance burden: 10 lines of shared utility code is better
  than 50 lines of duplicated helper functions across 5 modules.

## Decision Making Process

- When approaching complexity refactoring:
  1. First, semantic_search for similar patterns in other modules
  2. Check existing utilities in `/src/iemjs/` and `/htdocs/js/iemjs/`
  3. If pattern exists 2+ times, create shared utility
  4. If truly module-specific, create focused helper functions
  5. Document the decision rationale in comments
