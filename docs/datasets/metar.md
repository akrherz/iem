## <a name="metar"></a>ASOS/AWOS Global METAR Archives

### Summary

The primary format that worldwide airport weather station data is reported in is called METAR. This format is somewhat archaic, but well known and utilized in the community.  The IEM gets a feed of this data from [Unidata's IDD](http://unidata.ucar.edu) data stream.  The weather stations included are typically called "Automated Surface Observation System (ASOS)".  The term "Automated Weather Observation System (AWOS)" is often used inter-changably.

* __Download Interface__: [IEM On-Demand](https://mesonet.agron.iastate.edu/request/download.phtml)
* __Spatial Domain__: Worldwide
* __Temporal Domain__: 1928-present

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

3. Please explain the temperature units, storage and processing.

This is why we can not have nice things.  The following discussion generally applies to the US observation sites.  No matter what you see in various data feeds, the ASOS stations internally store their temperatures in **whole degree Fahrenheit**. The issues happen when the station transmits the data in whole degree Celsius and thus not have enough precision to covert back to Fahrenheit.  For example, if the station observed a 78F temperature and then transmitted a 26C value, that 26C value converts back to 78.8F, which rounds to 79F.  And down the rabbit-hole we go!

The IEM's archive of ASOS/METAR data comes from 3 main sources and some minor auxillary ones.  The main source is the NOAA satellite feed, called NOAAPort.  This feed provides data in METAR format, so the transmitted units are always whole degree Celsius, but sometimes the METAR `T-group` is included, so there is enough added precision to reliabily convert back to whole degree Fahrenheit.  The IEM's processing attempts to prioritize those METARs that include the `T-group`, so that reliable Fahrenheit storage can occur.

The next main source is from the MADIS 5-minute ASOS dataset, previously called High Frequency METAR.  This data feed has a significant issue whereby the transmitted data from the FAA to the NWS is only in whole degree Celsius.  Such data can not be reliably converted back to whole degree Fahrenheit.  For this reason, the IEM database stores these values as missing and they are not included in the data download.  BUT, for those that really want this information, these values are included in the IEM-encoded raw METAR string that you can download with the data.  You can find further discussion on this [IEM News Item](https://mesonet.agron.iastate.edu/onsite/news.phtml?id=1290).

The third main source is from the [NCEI ISD](https://www.ncdc.noaa.gov/isd).  At this time, there are no known issues with the temperature data in this feed being reliable for whole degree Fahrenheit.
