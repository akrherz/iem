APSIM Weather Files for FACTS
=====

Behold there is some overly complex code in this folder for the preparation of climate files for APSIM.  Here is the basic gist of what the workflow is.

 1. For each location of interest, we have a QC'd baseline of data that is initially used
 2. This baseline file provides data from 1980 till the current year.  We then replace the data for each year for the Jan 1 to yesterday period with the observations from the current year.  These observations come from either ISU Soil Moisture Network stations or a research weather station (in the case of COBS) or from IEM Climodat estimates.
 3. The data for today and out 3 days for only the current year is replaced by the NDFD forecast data.
 4. The period after the NDFD replacement till the end of the year is replaced with CFS extracted forecast.

So the result is a climate file that has yearly scenarios representing the combination of this year's observations plus a previous years data plus a CFS forecast for the current year.  The APSIM runs then aren't year specific, but each previous year represents an ensemble member of sort.  The thought is that each of the previous year's time series represents a scenario that could potentially happen this year.

The complexity in `yieldfx_workflow.py` comes from keeping track of which replacements should happen when and what happens when there is missing data in any of these replacements.
