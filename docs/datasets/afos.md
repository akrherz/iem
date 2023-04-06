## <a name="afos"></a> NWS Text Product Archive

### Summary

This archive consists of raw ASCII text products issued by the National
Weather Service.  Some places on the website will refer to this as "AFOS", which
is an archaic old abbreviation associated with this dataset.  The realtime source
of this dataset is the processing of text products sent over the NOAAPort SBN, but
archives have been backfilled based on what exists at NCEI and also some archives
provided by the University of Wisconsin.

* __Download Interface__: [IEM On-Demand](https://mesonet.agron.iastate.edu/wx/afos/)
* __Spatial Domain__: Generally US NWS Offices that issue text products.
* __Temporal Domain__: Some data back to 1996, but archive quality and completeness
greatly improves for dates after 1998.

### Justification for processing

While the Internet provides many places to view current NWS Text Products, archives of these are much more difficult to find.  One of the primary goals of the IEM website is to maintain stable URLs, so when links are generates to NWS Text Products, they need to work into the future!  Many of these text products have very useful information in them for researchers and others in the public.

### Other Sources of Information

The [NCEI Site](https://www.ncei.noaa.gov) would be an authoritative source, but their archives of this data are very painful to work with.  There are a number of other sites that have per-UTC day files with some text products included.  For example [Oklahoma Mesonet](http://www.mesonet.org/data/public/noaa/text/archive/).

### Processing and Quality Control

Generally, some quality control is done to ensure that the data is ASCII format and not filled with control characters.  There are also checks that product timestamps are sane and represent a timestamp that is close to reality.  For example over the NOAAPort SBN feed, there is about one product per day that is a misfire or some other error that is not allowed to be inserted into the database.

This database culls some of the more frequently issued text products.  The reason being to save space and some of the text products are not very appropriate for long term archives.  The most significant deletion are the SHEF products, which would overwhelm my storage system if I attempted to save the data! [The script](https://github.com/akrherz/iem/blob/main/scripts/dbutil/clean_afos.py) that does the database culling each day contains the exact AWIPS IDs used for this cleaning.

### <a name="faq"></a> Frequently Asked Questions

1. How can I bulk download the data?

Sadly, this is not well done at the moment.  The [WX AFOS](https://mesonet.agron.iastate.edu/wx/afos/) is about the best option as it has a "Download Text" button.

2. Please describe any one-offs within the archive?

The `RRM` product is generally SHEF and thus was culled from the database to conserve space.
An IEM user requested that this product be retained, so the culling of it stopped on 31
March 2023.  So this product's archive only dates back till then.
