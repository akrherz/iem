## <a name="metar"></a>ASOS/AWOS Global METAR Archives

### Summary

The primary format that worldwide airport weather station data is reported in is called METAR. This format is somewhat archaic, but well known and utilized in the community.  The IEM gets a feed of this data from [Unidata's IDD](http://unidata.ucar.edu) data stream.  The weather stations included are typically called "Automated Surface Observation System (ASOS)".  The term "Automated Weather Observation System (AWOS)" is often used inter-changably.

* __Download Interface__: [IEM On-Demand](https://mesonet.agron.iastate.edu/request/download.phtml)
* __Spatial Domain__: Worldwide
* __Temporal Domain__: 1928-present (US), 2012-present (Worldwide)

### Justification for processing

The highest quality weather information comes from the ASOS sites.  These stations get routine maintenance, considerable quality control, and is the baseline hourly interval dataset used by all kinds of folks.  The data stream processed by the IEM contains global stations, so extending the ingest to the entire data stream was not significant effort.

### Other Sources of Information

[NCEI Integrated Surface Database (ISD)](https://www.ncdc.noaa.gov/isd) is likely the most authoritative source of this information.

### Processing and Quality Control

A Python based ingestor using the metar package processes this information into the IEM database.

### <a name="faq"></a> Frequently Asked Questions

1. Why is precipitation data all missing / zero for non-US locations?

It is the IEM's understanding that precipitation is not included in the global data streams due to previous data distribution agreements.  The precipitation data is considered of very high value as it can be used to model and predict the status of agricultural crops in the country.  Such information could push commodity markets.  For the present day, other satellite datasets likely negate some of these advantages, but alas.

2. How are "daily" precipitation totals calculated?

In general, the ASOS stations operate in local standard time for the entire year round. This has some implications with computation of various daily totals as during daylight saving time, the calendar day total will represent a 1 AM to 1 AM local daylight time period.  For the context of this METAR dataset, not all METAR reporting sites will generate a total that can be used for assignment of a calendar day's total.  So the IEM uses a number of approaches to arrive at this total.

* A script manually totals up the hourly precipitation reports and computes a true local calendar day total for the station, this total may later be overwritten by either of the below.
* A real-time ingest process gleans the daily totals from the Daily Summary Message (DSM) issued by some ASOS sites.
* A real-time ingest process gleans the daily totals from the Climate Report (CLI) that is issued for some ASOS sites by their respective local NWS Forecast Offfice.

Not all stations have DSM and/or CLI products, so the manual totaling provides a minimum accounting.  The complication is that this total does not cover the same period that a CLI/DSM product does.  So complicated!

