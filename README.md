# Iowa Environmental Mesonet

    If using this code causes your server to have kittens, it is your own fault.

This monolith drives much of the ingest, processing, product generation, and
web presence of the [IEM](https://mesonet.agron.iastate.edu).  Hopefully it can
be found useful for others to at least look at to see how some of the magic happens.

Limited integration testing is done on Github Actions: [![Build Status](https://github.com/akrherz/iem/workflows/IEM%20CI/badge.svg)](https://github.com/akrherz/iem)
[![DeepSource](https://app.deepsource.com/gh/akrherz/iem.svg/?label=active+issues&show_trend=true&token=WvZunVBligt7HgkO2JGg5uMe)](https://app.deepsource.com/gh/akrherz/iem/)
[![codecov](https://codecov.io/gh/akrherz/iem/graph/badge.svg?token=zKXnLZdxIk)](https://codecov.io/gh/akrherz/iem)

See [@akrherz Github Profile](https://github.com/akrherz) for an overview of
repositories found here and how the fit together.

## Requirements

    - Python 3.10+ (CI tests with 3.13)
    - PHP 8
