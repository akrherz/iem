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

