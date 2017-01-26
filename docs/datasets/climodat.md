## <a name="climodat"></a> IEM Climodat Reports and Data [WIP]

### Summary

This document describes the once daily climate dataset that provides observations and estimates of high and low temperature, precipitation, snowfall, and snow depth.  Parts of this dataset have been curated over the years by a number of Iowa State employees including Dr Shaw, Dr Carlson, and Dr Todey.

* __Download Interface__: [IEM On-Demand](https://mesonet.agron.iastate.edu/request/coop/fe.phtml)
* __Spatial Domain__: Midwestern US
* __Temporal Domain__: 1893-today
* __Variables Provided__: Once daily high and low temperature, precipitation, snowfall, snow depth

### Justification for processing

The most basic and important long term climate record are the once daily reports of high and low temperature along with precipitation and sometimes snow.  The most commonly asked question of the IEM datasets are climate related, so curating a long-term dataset of daily observations is necessary.

### Other Sources of Information

A great source of much of the same type of data is [Regional Climate Centers ACIS](http://www.rcc-acis.org/).

### Processing and Quality Control

There is nothing easy or trivial about processing or quality control of this dataset. After centuries of work, plenty of issues remain.  Having human observers be the primary driver of this dataset is both a blessing and a curse.  The good aspects include the archive dating back to the late 1800s for some locations and relatively high data quality.  The bad aspects include lots of metadata issues due to observation timing, station moves, and equipment siting.

The primary data source for this dataset is the National Weather Service COOP observers.  These reports come to the IEM over a variety of paths:

- Realtime reports found in NWS SHEF Text Products, processed in realtime by the IEM
- Quality controlled reports sent to the IEM by the State of Iowa Climatologist
- Via manually downloaded data archives provided by NCEI
- Via web services provided by RCC ACIS

The merging of these four datasets creates a bit of a nightmare to manage.

### <a name="faq"></a> Frequently Asked Questions

1. Where does the radiation data come from?

 Well, there is a long story!

1. Where does the non-radiation data come from?

 Well, ther eis another story?
