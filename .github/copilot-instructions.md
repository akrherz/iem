# IEM Repo

Every time you choose to apply a rule(s), explicitly state the rule(s) in the output. You can abbreviate the rule description to a single word or phrase.

## Rules

- Jquery should not be used and any instances of it should be replaced
  with vanilla JavaScript.
- Code comments should explain functionality, not detail why the code was
  added.
- JavaScript code should not be embedded in HTML files.
- Jquery-UI should not be used and any instances of it should be replaced
  with vanilla JavaScript.
- Avoid usage of `this` in JavaScript code, as it can lead to confusion
  and bugs. Use arrow functions or bind methods to the correct context instead.

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
scripts/     # python cron jobs that process data
tests/       # Python testing code mostly for pylib and for integration tests 
```
