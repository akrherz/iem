## <a name="vtec"></a> NWS Valid Time Extent Code (VTEC) Archives

### Summary

The National Weather Service uses a rather complex and extensive suite of products and methodologies to issue watch, warnings, and advisories (WWA).  Back in the 1990s and early 2000s, the automated processing of these products was extremely difficult and rife with errors.  To help with automated parsing, the NWS implemented a system called Valid Time Extent Code (VTEC) which provides a more programatic description of what an individual WWA product is doing.  The implementation of began in 2005 and was mostly wrapped up by 2008.  The IEM attempts to do high fidelity processing of this data stream and has a number of Internet unique archives and applications to view this information.

* __Download Interface__: [Shapefile/KML Download](https://mesonet.agron.iastate.edu/request/gis/watchwarn.phtml)
* __Spatial Domain__: United States, including Guam, Puerto Rico and some other islands
* __Temporal Domain__: Most WWA types back to 2008 or 2005, an archive of Flash Flood Warnings goes back to 2002 or so, and Tornado / Severe Thunderstorm Warnings goes back to 1986

### Justification for processing

NWS issued WWA alerts are an important environmental hazard dataset and has broad interest in the research and insurance industries.  Even in 2017, there are very few places that you can find long term archives of this information in usable formats.

### Other Sources of Information

The [National Center for Environmental Information](https://www.ncei.noaa.gov) has raw text product archives that do not contain processed atomic data of the actual WWA alerts.  So the user is left to the adventure of text parsing the products.  Otherwise, it is not clear if any other archive exists on the Internet of this information.

### Processing and Quality Control

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


### <a name="faq"></a> Frequently Asked Questions

1. How do Severe Thunderstorm, Flash Flood, or Tornado warnings have VTEC codes for dates prior to implementation?

    Good question!  A number of years ago, a kind NWS manager provided a database dump of their curated WWA archive for dates between 1986 and 2005.  While not perfect, this archive was the best/only source that was known at the time.  The IEM did some logic processing and attempted to back-compute VTEC ETNs for this archive of warnings.  The database was atomic to a local county/parish, so some logic was done to merge multiple counties when they spatially touched and had similiar issuance timestamps.  Again from the above, automated machine parsing of the raw text is next to impossible.  The ETNs were assigned as a convience so that various IEM apps and plots would present this data online.

1. The database has Weather Forecast Offices (WFOs) issuing WWA products for dates prior to the office even existing?  How can this be!?!?

    Yeah, this is somewhat poor, but was done to again provide some continuity with current day operations.  The archive database provided to the IEM did not contain the issuance forecast office, so without a means to properly attribute these, the present day WFOs were used.  This issue is rarely raised by IEM users, but it is good to document.  Maybe someday, a more authoritative archive will be made and these old warnings and be assigned to the various WSOs, etc that existed at the time.

1. What are the VTEC phenomena and significance codes?

    The phenomena code (two characters) and significance code (one character) denote the particular WWA hazzard at play with the product. The [NWS VTEC Site](http://www.nws.noaa.gov/om/vtec/) contains a one pager PDF that documents these codes.  The NWS uses these codes to color encode their WAWA Map found on their homepage.  You can find a lookup reference table of these codes and colors [here](https://github.com/akrherz/pyIEM/blob/master/pyiem/nws/vtec.py).

