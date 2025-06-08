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

// Or import everything
import * as IEM from 'iemjs';
```

### Browser ES Modules (direct import from this repo)

```javascript
// Import from web-accessible location
import { escapeHTML, requireSelectElement } from '/js/iemjs/domUtils.js';
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
- `iemdata.vtec_phenomena` - Weather event phenomena
- `iemdata.vtec_significance` - Weather event significance levels

## License

MIT
