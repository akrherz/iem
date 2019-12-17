# <a name="vtec"></a> NWS Valid Time Extent Code (VTEC) Archives

## Summary

The National Weather Service uses a rather complex and extensive suite of products and methodologies to issue watch, warnings, and advisories (WWA).  Back in the 1990s and early 2000s, the automated processing of these products was extremely difficult and rife with errors.  To help with automated parsing, the NWS implemented a system called Valid Time Extent Code (VTEC) which provides a more programatic description of what an individual WWA product is doing.  The implementation of began in 2005 and was mostly wrapped up by 2008.  The IEM attempts to do high fidelity processing of this data stream and has a number of Internet unique archives and applications to view this information.

* __Download Interface__: [Shapefile/KML Download](https://mesonet.agron.iastate.edu/request/gis/watchwarn.phtml)
* __Spatial Domain__: United States, including Guam, Puerto Rico and some other islands
* __Temporal Domain__: Most WWA types back to 2008 or 2005, an archive of Flash Flood Warnings goes back to 2002 or so, and Tornado / Severe Thunderstorm Warnings goes back to 1986

## Justification for processing

NWS issued WWA alerts are an important environmental hazard dataset and has broad interest in the research and insurance industries.  Even in 2017, there are very few places that you can find long term archives of this information in usable formats.

## Other Sources of Information

The [National Center for Environmental Information](https://www.ncei.noaa.gov) has raw text product archives that do not contain processed atomic data of the actual WWA alerts.  So the user is left to the adventure of text parsing the products.  Otherwise, it is not clear if any other archive exists on the Internet of this information.

## Processing and Quality Control

The [pyIEM](https://github.com/akrherz/pyIEM) python package is the primary code that does the text parsing and databasing of the WWA products.  A large number of unit tests exist against the various variations and quirks found with processing the WWA data stream since the mid 2000s.  New quirks and edge cases are still found today with minor corrections made to the archive when necessary.  The IEM continuously alerts and annoys the NWS when various issues are found, hoping to get the NWS to correct their products.  While it has been a long and frustrating process, things do eventually get fixed leading to more robust data archives.

The pyIEM parsers send emails to the IEM developer when issues are found.  The parser alerts when the following errors are encountered:

* VTEC Event IDs (ETNs) being used that are out of sequential order.
* Warning product segments are missing or have invalid Universal Geographic Code (UGC) encoding
* Product segment has invalid VTEC encoding
* Polygons included in the warning are invalid or counterclockwise
* Timestamps are formatted incorrectly
* The UGC / VTEC sequence of a particular product contains logical errors, for example a UGC zone silently drops out or into a warning.
* Products are expired outside of the acceptable temporal bounds
* Any other type of error and/or code bug that caused a processing fault

## <a name="faq"></a> Frequently Asked Questions

1. Please fully describe the schema used within the downloaded shapefiles.

    Grab some coffee and headache medicine as I am going to try to explain how the IEM processes these events into the database.  The first concept to understand is that when the NWS issues a Watch, Warning, Advisory (WaWA) event, this event undergoes a lifecycle.  The NWS can issue updates that modify the start and end times of the event and the spatial extent of the event.  They can also do upgrades on the event, for example moving from a watch into a warning.  The IEM database does not necessary fully document the event's lifecycle, but provides the metadata for the last known state of the event.

    For the context of IEM provided shapefiles, here is a discussion of what each DBF column represents.  We will go into an example afterwards attempting to illustrate what each column means.

    But first, the timestamps.  The presented timestamps are always in UTC timezone.  The timestamp is represented by a 12 character string in the form of year, month, day, 24-hour,minute.  To my knowledge, there is no timestamp data type in DBF, so this is the pain we have to live with.

    | DBF Column  | Type | Description |
| ------------- | ------------- | ----- |
| WFO | 3 Char | This is the three character NWS Office/Center identifier.  For CONUS locations, this is the 4 character ID dropping the first `K`.  For non-CONUS sites, this is the identifier dropping the `P`. |
| ISSUED  | 12 Char | This timestamp represents the start time of the event.  When an event's lifecycle begins, this issued value can be updated as the NWS issues updates.  The value presented represents the last known state of the event start time.|
| EXPIRED  | 12 Char  | Similiar to the ISSUED column above, this represents the products event end time.  Again, this value is updated as the event lifecycle happens with updates made by the NWS. |
| INIT_ISS | 12 Char | This is timestamp of the NWS Text Product that started the event.  This timestamp is important for products like Winter Storm Watch, which have a begin time a number of days/hours into the future, but are typically considered to be in effect at the time of the text product issuace.  Yeah, this is where the headaches start.  This timestamp can also be used to form a canonical URL back to the IEM to fetch the raw NWS Text for this event. It is **not** updated during the event's lifecycle. |
| INIT_EXP | 12 Char | Similiar to `INIT_ISS` above, this is the expiration of the event denoted with the first issuance of the event.  It is **not** updated during the event's lifecycle. |
| PHENOM or TYPE | 2 Char | This is the two character NWS identifier used to denote the VTEC event type.  For example, `TO` for Tornado and `SV` for Severe Thunderstorm.  A lookup table of these codes exists [here](https://github.com/akrherz/pyIEM/blob/master/src/pyiem/nws/vtec.py). |
| SIG | 1 Char | This is the one character NWS identifier used to denote the VTEC significance.  The same link above for `PHENOM` has a lookup table for these. |
| GTYPE | 1 Char | Either `P` for polygon or `C` for county/zone/parish.  The shapefiles you download could contain both so-called storm-based (polygon) events and traditional county/zone based events. |
| ETN | Int | The VTEC event identifier.  A tracking number that should be unique for this event, but sometimes it is not.  Yes, more headaches. Note that the uniqueness is not based on the combination of a UGC code, but the issuance center and a continuous spatial region for the event. |
| STATUS | 3 Char | The VTEC status code denoting the state the event is during its life cycle.  This is purely based on any updates the event got and not some logic on the IEM's end denoting if the event is in the past or not. |
| NWS_UGC | 6 Char | For county,zone,parish warnings `GTYPE=C`, the Universal Geographic Code that the NWS uses.  Sadly, this is not exactly FIPS. |
| AREA_KM2 | Number | The IEM computed area of this event, this area computation is done in Albers (EPSG:2163). |
| UPDATED | 12 Char | The timestamp when this event's lifecycle was last updated by the NWS. |

    Whew, so let us do a practical example to try to illustrate what the above schema is attempting to capture.  The NWS in Des Moines `wfo=DMX` issues a Winter Storm Watch `phenom=WS` `sig=A` for Story County (`nws_ugc=IAZ048`).  This product was issued at noon on 19 March 2019 `INIT_ISS=201903191700` and goes into effect at 6 PM on 20 March `ISSUE=201903202300` `INIT_ISS=201903202300` until 6 AM 21 March `EXPIRE=201903211100` `INIT_EXP=201903211100`.  At 7 PM on 19 March, DMX decides to upgrade the event to a Winter Storm Warning.  The Winter Storm Watch then gets updated with `EXPIRE=201903200000` `UPDATED=201903200000` `STATUS=UPG`.  So the confusing aspect here becomes that the database representation has an `EXPIRE` that is before the `ISSUE` column.  This is just tricky to resolve, so good luck.  It is a long standing annoyance of how NWS handles VTEC events like this with `ISSUE` times well into the future.  For all practical purposes, once a winter storm watch is issued, it is valid **now**, but the encoding does not follow this.

1. How do Severe Thunderstorm, Flash Flood, or Tornado warnings have VTEC codes for dates prior to implementation?

    Good question!  A number of years ago, a kind NWS manager provided a database dump of their curated WWA archive for dates between 1986 and 2005.  While not perfect, this archive was the best/only source that was known at the time.  The IEM did some logic processing and attempted to back-compute VTEC ETNs for this archive of warnings.  The database was atomic to a local county/parish, so some logic was done to merge multiple counties when they spatially touched and had similiar issuance timestamps.  Again from the above, automated machine parsing of the raw text is next to impossible.  The ETNs were assigned as a convience so that various IEM apps and plots would present this data online.

1. The database has Weather Forecast Offices (WFOs) issuing WWA products for dates prior to the office even existing?  How can this be!?!?

    Yeah, this is somewhat poor, but was done to again provide some continuity with current day operations.  The archive database provided to the IEM did not contain the issuance forecast office, so without a means to properly attribute these, the present day WFOs were used.  This issue is rarely raised by IEM users, but it is good to document.  Maybe someday, a more authoritative archive will be made and these old warnings and be assigned to the various WSOs, etc that existed at the time.

1. What are the VTEC phenomena and significance codes?

    The phenomena code (two characters) and significance code (one character) denote the particular WWA hazzard at play with the product. The [NWS VTEC Site](http://www.nws.noaa.gov/om/vtec/) contains a one pager PDF that documents these codes.  The NWS uses these codes to color encode their WAWA Map found on their homepage.  You can find a lookup reference table of these codes and colors [here](https://github.com/akrherz/pyIEM/blob/master/src/pyiem/nws/vtec.py).

1. How do polygon warnings exist in the IEM archive prior to being official?

    The NWS offices started experimenting with polygons beginning in 2002.  These polygons were included with the warnings, but sometimes were not geographically valid and/or leaked well outside of a local office's CWA bounds.  On 1 October 2007, these polygons became the official warning for some VTEC types.  In general, the IEM's data ingestor attempts to save these polygons whenever found.
