## <a name="climodat"></a> IEM Climodat Reports and Data

### Summary

This document describes the once daily climate dataset that provides observations and estimates of high and low temperature, precipitation, snowfall, and snow depth.  Parts of this dataset have been curated over the years by a number of Iowa State employees including Dr Shaw, Dr Carlson, and Dr Todey.

* __Download Interface__: [IEM On-Demand](https://mesonet.agron.iastate.edu/request/coop/fe.phtml)
* __Spatial Domain__: United States
* __Temporal Domain__: varies by station
* __Variables Provided__: Once daily high and low temperature, precipitation, snowfall, snow depth

### Justification for processing

The most basic and important long term climate record are the once daily reports of high and low temperature along with precipitation and sometimes snow.  The most commonly asked question of the IEM datasets are climate related, so curating a long-term dataset of daily observations is necessary.

### Other Sources of Information

A great source of much of the same type of data is [Regional Climate Centers ACIS](http://www.rcc-acis.org/).  The complication when comparing IEM Climodat data to other sources is the difference in station identifiers used.  The history of station identifiers is long and complicated.  The National Center for Environmental Information (NCEI) has made strides in attempting to straighten the identifiers out.  This continues to be complicated as the upstream data source of information uses a completely different set of identifiers known as National Weather Service Location Identifiers (NWSLI), which are different than what NCEI or the IEM uses for our climate datasets.

### Processing and Quality Control

There is nothing easy or trivial about processing or quality control of this dataset. After decades of work, plenty of issues remain.  Having human observers be the primary driver of this dataset is both a blessing and a curse.  The good aspects include the archive dating back to the late 1800s for some locations and relatively high data quality.  The bad aspects include lots of metadata issues due to observation timing, station moves, and equipment siting.

The primary data source for this dataset is the National Weather Service COOP observers.  These reports come to the IEM over a variety of paths:

* Realtime reports found in NWS SHEF Text Products, processed in realtime by the IEM
* Via manually downloaded data archives provided by NCEI
* Via web services provided by RCC ACIS

The merging of these four datasets creates a bit of a nightmare to manage.

Snowfall and snow depth data is always problematic.  First, lets clarify what the terms mean.  "Snowfall" is the amount of snow that fell from the sky over the previous 24 hour period.  "Snow depth" is the amount of snow measured to be on the ground due to previous snowfalls.  These numbers may sometimes contradict with snowfall amounts being larger than snow depth due to melting and/or compaction.  Care should be used when analyzing the snowfall and snow depth reports.

### <a name="faq"></a> Frequently Asked Questions

1. This data contains 'Statewide' and 'Climate District' observations, where do they come from?

    The IEM produces gridded analyses of observed variables.  A GIS-style weighted spatial sampling is done from this grid to derive averaged values over geographies like states and climate districts.  Of course, when you average something like precipitation over a large area, you end up with rates that are lower than peak station rates and also with more precipitation events than individual stations within the region.

1. The download provides only a date, what time period does this represent?

    Almost always, this date *does not* represent a local calendar date's worth of data.  This date represents the date on which the observation was taken.  Typically, this observation is taken at about 7 AM and so represents a 24 hour period prior to 7 AM.  Explicitly providing the time of observation is a future and necessary enhancement to this dataset, but just tricky to do.  Some observation locations have switched times over the years and some even observe 24 hour precipitation totals at a different time than the temperature values.  Nothing is ever easy with this dataset...

1. Where does the radiation data come from?

    The NWS COOP Network does not provide observations of daily solar radiation, but this variable is extremely important to many folks that use this information for modelling.  As a convience, the IEM processes a number of reanalysis datasets and produces point sampling from the gridded information to provide "daily" radiation totals.  A major complication is that the 'daily' COOP observations are typically at 7 AM and the gridded solar radiation data is extracted on close to a local calendar day basis.  In general, the 7 AM value is for the previous day.

1. Where does the non-radiation data come from?

    This information is primarily driven by the realtime processing of NWS COOP observations done by the IEM.  For data older than the past handful of years, it is taken from the NCEI databases and now the ACIS web services.  Some manual work is done to meld the differences in site identifiers used between the various online resources.

1. How do I know which variables have been estimated and which are observations?

    The download interface for this dataset provides an option to include a flag for which observations have estimated temperatures or precipitation.  Presently, a general flag is provided for both high and low temperature and no flag is provided for the snowfall and snow depth information.
