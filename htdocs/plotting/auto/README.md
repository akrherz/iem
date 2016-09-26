IEM Autoplot Framework
======================

##Purpose

If I am going to create all of these fancy pants plotting interfaces, it would
be best to not have to reinvent the HTML controller for each.  So this provides
a PHP framework to manage building wrapper interfaces into the Python based
plotting applications.

###How it works

The PHP `index.phtml` first makes a HTTP localhost request back to the
`plotmeta.py` script asking for a listing of all available plotting apps.
This listing is directly taken from the content of `scripts/__init__.py`.
The page then lists these out as available plot options.

Once the user selects one of these options, the `index.phtml` makes another
request to the `plotmeta.py` script asking for the specific context of how
to call the choosen script.  With that context in hand, it iterates through
the provided arguments and generates the HTML form interface.

Once the user selects which options to set on the plot, the `index.phtml`
then builds a URI that the client browser can use to directly call the
plotting application.  This API call may do one of the following:

    * ask for a PNG, SVG image or PDF file
    * ask for a CSV or Excel formatted dataframe
    * ask for javascript to drive a highcharts display

Of course, it all can't be that simple and there is some very hairy logic
found in the `index.phtml` code to keep everything in order.

###Python Example

A basic layout of the python code is as follows.  This code is simply run as
`ExecCGI` style python scripts.  This keeps things less efficient, but no
worries about thread safety and memory issues with my code or the many, many
different python modules at play here.

```python
import matplotlib.pyplot as plt
import pandas as pd

def get_description():
    """ How does this script get called, I return a dictionary that
    later becomes a JSON object sent to PHP"""
    d = dict()
    d['description'] = """Description used on the interface."""
    # does this code return a pandas dataframe
    d['data'] = True
    # how am I called
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station'),
        dict(type='select', name='type', default='max-high',
             label='Which metric to plot?', options=PDICT),
        dict(type='float', name='threshold', default=-99,
             label='Threshold (optional, specify when appropriate):'),
    ]
    return d

def highcharts(fdict):
	""" called in the case of get_description() object having highcharts set
	to True.  fdict is a dictionary of CGI parameters"""
	return """javascript text"""
	
def plotter(fdict):
    """ called in the case of asking for a dataframe or plot.
    fdict is a dictionary of CGI parameters
    """
    (fig, ax) = plt.subplots(1, 1)
    df = pd.DataFrame()
    return fig, df
```

So the python scripts are sequentially numbered for no good reason other than
how I set it up.  The `scripts/` folder contains numbers 1 to 99 and then the
`scripts100/` folder contains 100 to 199.  etc.  I split up the folders just
to keep the directories from getting too big.  I plan on having thousands of
plotting apps at the rate I am creating them :)
