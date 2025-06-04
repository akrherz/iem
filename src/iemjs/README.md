# IEM JavaScript Utilities

A collection of JavaScript utilities for weather data applications from the Iowa Environmental Mesonet.

## Installation

```bash
npm install iemjs
```

## Usage

### ES Modules (Node.js/bundlers)

```javascript
// Import specific utilities
import { escapeHTML, requireSelectElement } from 'iemjs/domUtils';
import { iemdata } from 'iemjs/iemdata';

// Or import everything
import * as IEM from 'iemjs';
```

### Browser ES Modules (direct import)

```javascript
// Import from web-accessible location
import { escapeHTML, requireSelectElement } from '/js/iemjs/domUtils.js';
import { iemdata } from '/js/iemjs/iemdata.js';
```

## Modules

### domUtils

Utilities for safe DOM manipulation:

- `escapeHTML(text)` - Escape HTML to prevent XSS
- `getElementById(id, ElementType)` - Safe element retrieval with type checking
- `requireSelectElement(id)` - Get select element or throw error
- `requireInputElement(id)` - Get input element or throw error
- `setSelectValue(selectElement, value)` - Set select value with validation
- `clearSelect(selectElement, placeholder)` - Clear and reset select options
- `addSelectOption(selectElement, value, text, selected)` - Add option to select
- `createElementWithText(tag, text, className)` - Create element with text content
- `showElement(element)` / `hideElement(element)` - Show/hide elements
- `removeAllChildren(element)` - Remove all child nodes

### iemdata

Weather and climate data constants:

- `iemdata.states` - US states list
- `iemdata.vtec_phenomena_dict` - Weather event phenomena
- `iemdata.vtec_significance_dict` - Weather event significance levels
- Plus many other meteorological constants and lookup tables

## Development

This package follows IEM coding standards:

- No jQuery dependencies
- Vanilla JavaScript ES modules
- Avoids usage of `this` keyword
- Comprehensive JSDoc documentation

## License

Apache-2.0
