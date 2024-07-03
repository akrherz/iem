<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "JSON(P) Web Services";

$services = array();

$services[] = array(
    "title" => "United States Drought Monitor",
    "url" => "/geojson/usdm.py?date={date}",
    "desc" => "The US Drought Monitor valid for the given date.  You do not" .
        " need to specify the exact date on which the Drought Monitor was issued." .
        " The service will compute the date on which the Drought Monitor was issued" .
        " given the provided date.  Not specifying a date will provide the current" .
        " Drought Monitor. Archive begins on Jan 2000.",
    "vars" => array(
        "date" => "Date (optional)"
    ),
    "example" => array(
        "{date}" => "2017-07-18"
    )
);


$services[] = array(
    "title" => "Single Station Last Observation",
    "url" => "/json/current.py?station={station}&amp;network={network}",
    "desc" => "The most recent observation for an IEM tracked site.",
    "vars" => array(
        "station" => "Station Identifier",
        "network" => "Network Identifier",
    ),
    "example" => array(
        "{station}" => "AMW",
        "{network}" => "IA_ASOS",
    )
);

$services[] = array(
    "title" => "Oregon State PRISM Grid Cell Daily Sample",
    "url" => "/json/prism/{lon}/{lat}/{date_or_daterange}",
    "desc" => "Produces a daily time series for a grid cell that covers" .
        " the specified latitude and longitude (negative E values)." .
        " Credit: <a href='http://prism.oregonstate.edu'>PRISM Climate Group</a>," .
        " Oregon State University, created 4 Feb 2004.",
    "vars" => array(
        "lat" => "Latitude (deg N)",
        "lon" => "Longitude (deg E)",
        "date_or_daterange" => "YYYYmmdd or YYYYmmdd-YYYYmmdd (inclusive)",
    ),
    "example" => array(
        "{lat}" => "41.99",
        "{lon}" => "-95.55",
        "{date_or_daterange}" => "20151215-20160115"
    )
);

$services[] = array(
    "title" => "NCEP Stage IV Hourly Precipitation",
    "url" => "/json/stage4/{lon}/{lat}/{utc_date}",
    "desc" => "This service provides a grid point sampling of the NCEP" .
        " Stage IV product.  The date provided the service is a UTC date. Note" .
        " that the hourly stage IV data does not receive the level of QC that" .
        " the 6, 12, and 24 hour summaries do.",
    "vars" => array(
        "lat" => "Latitude (deg N)",
        "lon" => "Longitude (deg E)",
        "utc_date" => "YYYY-mm-dd",
    ),
    "example" => array(
        "{lat}" => "41.99",
        "{lon}" => "-95.55",
        "{utc_date}" => "2017-08-21"
    )
);

$services[] = array(
    "title" => "Local Storm Reports for One Storm Based Warning",
    "url" => "/geojson/lsr.php?year={year}&amp;wfo={wfo}" .
        "&amp;eventid={eventid}&amp;phenomena={phenomena}" .
        "&amp;significance={significance}",
    "desc" => "Produces the storm reports that spatially and temporally
          coincide with a given Storm Based Warning. This only works for
          warnings that had polygons associated with them and not other VTEC
          products.",
    "vars" => array(
        "wfo" => "3 character NWS Office",
        "year" => "Year of VTEC Issuance",
        "phenomena" => "2 character VTEC Phenomena Code",
        "significance" => "1 character VTEC Significance Code",
        "eventid" => "VTEC Event ID",
    ),
    "example" => array(
        "{wfo}" => "DVN",
        "{year}" => "2015",
        "{phenomena}" => "TO",
        "{significance}" => "W",
        "{eventid}" => 10,
    )
);

$services[] = array(
    "title" => "Local Storm Reports for a given period",
    "url" => "/geojson/lsr.php?sts={sts}&amp;ets={ets}" .
        "&amp;wfos={wfos}",
    "desc" => "Produces the storm reports for a given office or offices
          valid for a specified period (inclusive).",
    "vars" => array(
        "wfo" => "3 character NWS Office " .
            "(comma seperated for multiple, leave blank for all)",
        "sts" => "UTC Start Timestamp YYYYmmddHHMM",
        "ets" => "UTC End Timestamp YYYYmmddHHMM",
    ),
    "example" => array(
        "{wfos}" => "DVN,DMX,ARX",
        "{sts}" => "201605100000",
        "{ets}" => "201605110000",
    )
);


$services[] = array(
    "title" => "Archived or Current NEXRAD Storm Attribute Table",
    "url" => "/geojson/nexrad_attr.geojson?help",
);


$services[] = array(
    "title" => "IEM Tracked Networks Metadata",
    "url" => "/geojson/networks.geojson",
    "desc" => "A GeoJSON listing of IEM labelled networks.",
    "vars" => array(),
    "example" => array()
);

$services[] = array(
    "title" => "NWS Impact Based Warnings Tags",
    "url" => "/json/ibw_tags.py?year={year}&amp;wfo={wfo}",
    "desc" => "Produces a listing of Impact Warning Tags used in Severe " .
        "Thunderstorm, Tornado, Marine, and Flash Flood Warnings " .
        "warnings by NWS Forecast Office and Year.",
    "vars" => array(
        "wfo" => "3 character NWS Office",
        "year" => "Year of interest"
    ),
    "example" => array(
        "{wfo}" => "DVN",
        "{year}" => "2015"
    )
);

$services[] = array(
    "title" => "Iowa Winter Road Conditions",
    "url" => "/geojson/winter_roads.geojson",
    "desc" => "This service provides the most recent Iowa Winter Road
          Conditions.",
    "vars" => array(),
    "example" => array()
);

$services[] = array(
    "title" => "NWS COOP Station Climatology",
    "url" => "/json/climodat_stclimo.py?station={station}&amp;syear={syear}&amp;eyear={eyear}",
    "desc" => "Produces a listing of daily climatology for an IEM tracked
          long term climodat site in the midwestern US.",
    "vars" => array(
        "station" => "6 character station identifier",
        "syear" => "Inclusive start year of the period of interest",
        "eyear" => "Exclusive end year of the period of interest"
    ),
    "example" => array(
        "{station}" => "IA0200",
        "{syear}" => "1800",
        "{eyear}" => "2016",
    )
);

$services[] = array(
    "title" => "NWS COOP Network Climatology for one day",
    "url" => "/geojson/climodat_dayclimo.py?network={network}&amp;day={day}&amp;month={month}&amp;syear={syear}&amp;eyear={eyear}",
    "desc" => "Produces a listing of climatology for a single state
          for a single day.",
    "vars" => array(
        "network" => "state network identifier",
        "month" => "Numeric month of interest (1-12)",
        "day" => "Numeric day of interest (1-31)",
        "syear" => "Inclusive start year of the period of interest",
        "eyear" => "Exclusive end year of the period of interest"
    ),
    "example" => array(
        "{network}" => "IACLIMATE",
        "{month}" => "4",
        "{day}" => "3",
        "{syear}" => "1800",
        "{eyear}" => "2016",
    )
);

$services[] = array(
    "title" => "NWS VTEC Maximum Event ID by Year",
    "url" => "/json/vtec_max_etn.py?year={year}",
    "desc" => "Produces a listing of the maximum eventid used for each " .
        "NWS Forecast Office, VTEC Phenomena and VTEC Significance.",
    "vars" => array(
        "year" => "YYYY year"
    ),
    "example" => array(
        "{year}" => "2015"
    )
);


$services[] = array(
    "title" => "NWS VTEC Event Geometries",
    "url" => "/geojson/vtec_event.py?wfo={wfo}&year={year}" .
        "&phenomena={phenomena}&etn={etn}&significance={significance}",
    "desc" => "Produces GeoJSON for a given VTEC Event.",
    "vars" => array(
        "wfo" => "3 or 4 character WFO identifier",
        "year" => "YYYY year",
        "etn" => "VTEC Event ID",
        "phenomena" => "2 Character VTEC Phenomena Code",
        "significance" => "1 Character VTEC Significance Code",
        "sbw" => "1 or 0, flag to return Storm Based Polygon(1) or Counties",
        "lsrs" => "1 or 0, flag to return local storm reports",
    ),
    "example" => array(
        "{wfo}" => "DMX",
        "{year}" => "2015",
        "{etn}" => "10",
        "{significance}" => "W",
        "{phenomena}" => "TO",
        "{lsrs}" => '0',
        "{sbw}" => '1',
    )
);

$services[] = array(
    "title" => "NWS VTEC Event Metadata",
    "url" => "/json/vtec_event.py?wfo={wfo}&year={year}" .
        "&phenomena={phenomena}&etn={etn}&significance={significance}",
    "desc" => "Produces metadata on a given VTEC Event.",
    "vars" => array(
        "wfo" => "3 or 4 character WFO identifier",
        "year" => "YYYY year",
        "etn" => "VTEC Event ID",
        "phenomena" => "2 Character VTEC Phenomena Code",
        "significance" => "1 Character VTEC Significance Code",
    ),
    "example" => array(
        "{wfo}" => "DMX",
        "{year}" => "2015",
        "{etn}" => "10",
        "{significance}" => "W",
        "{phenomena}" => "TO",
    )
);

$services[] = array(
    "title" => "NWS VTEC Event Listing by WFO by Year",
    "url" => "/json/vtec_events.py?wfo={wfo}&year={year}",
    "desc" => <<<EOM
Produces a listing of VTEC Events (watch, warning,advisories) by year by weather
forecast office.  You can optionally pass a <code>phenomena=XX</code> and
<code>significance=X</code> to the service to only return that VTEC event
type for the given WFO and year.  Additionally, there is a one-off feature
flag of <code>combo=1</code>, which has the service return and Tornado,
Severe Thunderstorm, and Flash Flood Watches/Warnings in chronological order.
EOM,
    "vars" => array(
        "wfo" => "3 character WFO identifier",
        "year" => "YYYY year"
    ),
    "example" => array(
        "{wfo}" => "DMX",
        "{year}" => "2015"
    )
);

$services[] = array(
    "title" => "NWS VTEC Event Listing by State by Year",
    "url" => "/json/vtec_events_bystate.py?state={state}&year={year}",
    "desc" => "Produces a listing of VTEC Events (watch, warning,
    advisories) by year by state.",
    "vars" => array(
        "state" => "2 character State identifier",
        "year" => "YYYY year"
    ),
    "example" => array(
        "{state}" => "IA",
        "{year}" => "2015"
    )
);

$services[] = array(
    "title" => "NWS VTEC Event Listing by WFO valid during Given Period",
    "url" => "/json/vtec_events_bywfo.py?wfo={wfo}&start={start}&end={end}",
    "desc" => "Produces a listing of VTEC Events (watch, warning,
    advisories) by wfo with UGC information enumerated.",
    "vars" => array(
        "wfo" => "3 character WFO identifier",
        "start" => "ISO Start Datetime UTC (YYYY-MM-DDTHH:MM)",
        "end" => "ISO End Datetime UTC (YYYY-MM-DDTHH:MM)",
    ),
    "example" => array(
        "{wfo}" => "DMX",
        "{start}" => "2022-06-14T00:00",
        "{end}" => "2022-06-15T00:00",
    )
);

$services[] = array(
    "title" => "NWS Text Products by AWIPS ID and Time Period",
    "url" => "/json/nwstext_search.py?sts={sts}&ets={ets}&awipsid={awipsid}",
    "desc" => "Search of NWS Issued Text Products by a time period (in 
          UTC) and an AWIPS ID (sometime called AFOS PIL).  If you specify
          the AWIPS ID to be only three characters, the interruptation is to
          search of that base product identifier from any issuance center. For
          example, setting LSR would return all LSRXXX products.",
    "vars" => array(
        "sts" => "YYYY-mm-ddTHH:MMZ Inclusive start period (UTC)",
        "ets" => "YYYY-mm-ddTHH:MMZ end time period (UTC)",
        "awipsid" => "6 character or less AWIPS ID / AFOS PIL.",
    ),
    "example" => array(
        "{sts}" => "2014-11-24T00:00Z",
        "{ets}" => "2014-11-25T00:00Z",
        "{awipsid}" => "AFDDMX",
    )
);

$services[] = array(
    "title" => "Daily NWS Climate (CLI Product) Summaries",
    "url" => "/geojson/cli.py?dt={dt}&fmt={fmt}",
    "desc" => "Provides a GeoJSON response summarizing all of the atomic
          processed data from the NWS issued CLI reports.  These reports contain
          daily temperature, precipitation, and snow data from the primary 
          climate sites.",
    "vars" => array(
        "dt" => "YYYY-mm-dd Date you want data for (optional)",
        "fmt" => "Return format (optional) geojson (default) or csv",
    ),
    "example" => array(
        "{dt}" => "2014-10-09",
        "{fmt}" => "geojson",
    )
);

$services[] = array(
    "title" => "Yearly NWS Climate (CLI Product) Summaries for One Station",
    "url" => "/json/cli.py?station={station}&year={year}&fmt={fmt}",
    "desc" => "Provides a JSON response summarizing all of the atomic
    processed data from the NWS issued CLI reports for a single station and
    given year.  You can optionally set <code>fmt=csv</code> to get a CSV
    response.",
    "vars" => array(
        "year" => "YYYY desired",
        "station" => "ICAO 4-character station identifier",
        "fmt" => "Return format (optional) json (default) or csv",
    ),
    "example" => array(
        "{year}" => "2019",
        "{station}" => "KDSM",
        "{fmt}" => "json",
    )
);

$services[] = array(
    "title" => "IEM Tile Map Service Metadata",
    "url" => "/json/tms.json",
    "desc" => "Provides metadata about the currently available Tile Map
          Services provided by the IEM.  This is useful to determine how to 
          call back to the Tile Map Services.",
    "vars" => array(),
    "example" => array()
);

$services[] = array(
    "title" => "Current Storm Based Warnings",
    "url" => "/geojson/sbw.geojson?ts={ts}",
    "desc" => <<<EOM
Provides a geojson format of current National Weather Service
storm based warnings.  There is a 15 second caching done by the server
to ease load.  The generation_time attribute is set on the output 
to diagnose when the file is valid.  You can provide a timestamp
to provide archived warnings back to 2002 or so.  The polygons returned are the
actualy ones valid at the given timestamp or realtime, so any polygon updates
done with warning event are included here.  There should only be one polygon
per warning event. You can optionally pass a <code>wfo=WFO3Char</code> to
limit the polygons to a single office.
EOM
    ,
    "vars" => array(
        "ts" => "ISO-8601 Timestamp YYYY-mm-ddTHH:MI:SSZ (optional)"
    ),
    "example" => array(
        "{ts}" => "2011-04-27T22:00:00Z"
    )
);

$services[] = array(
    "title" => "Storm Based Warnings Issued Between Interval",
    "url" => "/geojson/sbw.geojson?help",
);


$services[] = array(
    "title" => "Search for Storm Based Warnings by Lat/Lon Point",
    "url" => "/json/sbw_by_point.py?lon={longitude}&lat={latitude}",
    "desc" => "Provides a listing of storm based (polygon) warnings 
          based on the provided latitude and longitude pair for warnings 
        dating back to 1 Jan 2005.",
    "vars" => array(
        "lat" => "Latitude in degrees",
        "lon" => "Longitude in (degrees east)"
    ),
    "example" => array(
        "{latitude}" => "42.5",
        "{longitude}" => "-95.0"
    )
);

$services[] = array(
    "title" => "Search for Storm Based Warnings by Lat/Lon Point by Time",
    "url" => "/json/sbw_by_point.py?lon={longitude}&lat={latitude}&valid={valid}",
    "desc" => "Provides a listing of storm based (polygon) warnings 
    based on the provided latitude and longitude pair for warnings 
  dating back to 1 Jan 2005.  You also provide an ISO-8601
  <code>valid</code> parameter to get any storm based warnings active
  at the given UTC time and location.",
    "vars" => array(
        "lat" => "Latitude in degrees",
        "lon" => "Longitude in (degrees east)",
        "valid" => "UTC ISO-8601 timestamp"
    ),
    "example" => array(
        "{latitude}" => "42.5",
        "{longitude}" => "-95.0",
        "{valid}" => "2014-09-01T00:29Z"
    )
);

$services[] = array(
    "title" => "Search for VTEC Events by Lat/Lon Point",
    "url" => "/json/vtec_events_bypoint.py?lon={longitude}&lat={latitude}&sdate={sdate}&edate={edate}",
    "desc" => "Provides a listing of VTEC events that were valid for
          a given latitude and longitude point.",
    "vars" => array(
        "lat" => "Latitude in degrees",
        "lon" => "Longitude in (degrees east)",
        "sdate" => "YYYY-mm-dd Start Date (UTC)",
        "edate" => "YYYY-mm-dd End Date (UTC)",
        "fmt" => "(optional) Format to download as: json (default) or xlsx"
    ),
    "example" => array(
        "{latitude}" => "42.5",
        "{longitude}" => "-95.0",
        "{sdate}" => "2015-06-01",
        "{edate}" => "2015-07-01",
    )
);

$services[] = array(
    "title" => "Storm Prediction Center Mesoscale Convection Discussions by Lat/Lon Point",
    "url" => "/json/spcmcd.py?lon={longitude}&amp;lat={latitude}",
    "desc" => "Provides a listing of Mesoscale Convective Discussions (MCD)s dating back to" .
        " October 2008.",
    "vars" => array(
        "lat" => "Latitude in degrees",
        "lon" => "Longitude in (degrees east)",
    ),
    "example" => array(
        "{latitude}" => "42.5",
        "{longitude}" => "-95.0",
    )
);

$services[] = array(
    "title" => "Storm Prediction Center Convective Outlooks by Lat/Lon Point",
    "url" => "/json/spcoutlook.py?lon={longitude}&amp;lat={latitude}&amp;last={last}&amp;day={day}&amp;cat={cat}",
    "desc" => "Provides a listing of convective outlooks dating back to" .
        " March 2002.",
    "vars" => array(
        "lat" => "Latitude in degrees",
        "lon" => "Longitude in (degrees east)",
        "last" => "(Optional) Include only the last number of outlooks for each category, 0 is all",
        "day" => "(Optional) Which outlook day to request, defaults to 1",
        "cat" => "(Optional) Which outlook category to request, defaults to CATEGORICAL",
    ),
    "example" => array(
        "{latitude}" => "42.5",
        "{longitude}" => "-95.0",
        "{last}" => "0",
        "{day}" => "1",
        "{cat}" => "CATEGORICAL",
    )
);
$services[] = array(
    "title" => "Storm Prediction Center Convective Outlooks by Lat/Lon Point by Time",
    "url" => "/json/spcoutlook.py?lon={longitude}&amp;lat={latitude}&amp;time={time}&amp;day={day}&amp;cat={cat}",
    "desc" => "Provides a listing of convective outlooks dating back to" .
        " March 2002 for a given timestamp.",
    "vars" => array(
        "lat" => "Latitude in degrees",
        "lon" => "Longitude in (degrees east)",
        "time" => "Return the outlook valid at that time.  This time can be a generic" .
            " 'now' or some ISO-ish timestamp in the format YYYY-mm-ddTHH:MMZ.",
        "day" => "(Optional) Which outlook day to request, defaults to 1",
        "cat" => "(Optional) Which outlook category to request, defaults to CATEGORICAL",
    ),
    "example" => array(
        "{latitude}" => "42.5",
        "{longitude}" => "-95.0",
        "{time}" => "2014-06-29T14:00Z",
        "{day}" => "1",
        "{cat}" => "CATEGORICAL",
    )
);

$services[] = array(
    "title" => "Special Weather Statements (SPS) Polygons in GeoJSON Format",
    "url" => "/geojson/sps.geojson?help",
);

$services[] = array(
    "title" => "Search for Warnings by UGC Code and Date Interval",
    "url" => "/json/vtec_events_byugc.py?ugc={ugc}&edate={edate}&sdate={sdate}",
    "desc" => "Provides a json response of archived warnings valid for the
          given UGC code and date interval (UTC time, end date exclusive). The date
          of product issuance is used for the date filtering.",
    "vars" => array(
        "ugc" => "Five character UGC identifier used by the NWS",
        "sdate" => "YYYY-mm-dd Start Date (UTC)",
        "edate" => "YYYY-mm-dd End Date (UTC)",
        "fmt" => "(optional) Format to download as: json (default) or xlsx"
    ),
    "example" => array(
        "{ugc}" => "IAC001",
        "{sdate}" => "1990-06-01",
        "{edate}" => "1990-07-01",
    )
);
$services[] = array(
    "title" => "Storm Prediction Center Watches by Time",
    "url" => "/json/spcwatch.py?ts={timestamp}",
    "desc" => "Provides a geojson format of SPC watches valid at given time
        or current time if no time specified.",
    "vars" => array(
        "timestamp" => "YYYYMMDDHHMI UTC Timestamp (optional)"
    ),
    "example" => array(
        "{timestamp}" => "201104280000"
    )
);
$services[] = array(
    "title" => "Storm Prediction Center Watches by Point",
    "url" => "/json/spcwatch.py?lon={lon}&lat={lat}",
    "desc" => "Provides a geojson format of SPC watches valid for a " .
        "give latitude and longitude pair.  Note that these polygons are not " .
        "the official watch boundaries.",
    "vars" => array(
        "lat" => "Latitude in degrees",
        "lon" => "Longitude in (degrees east)",
    ),
    "example" => array(
        "{lat}" => "42.5",
        "{lon}" => "-95.0",
    )
);
$services[] = array(
    "title" => "RAOB Soundings",
    "url" => "/json/raob.py?ts={timestamp}&station={station}",
    "desc" => "When provided a station and timestamp, returns a single
          RAOB profile.  When provided no station and a timestamp, returns
          all profiles in the database for that timestamp.  When provided a
          pressure [mb], returns just that pressure level's data.  Realtime data
        from this service is typically available within 2 hours of observation
        time.  For some RAOB sites, the IEM has a special identifier that merges
        period of record data for a general location.  For example, _OAX merges
        the long term data for KOMA, KOAX, and KOVN.",
    "vars" => array(
        "sid" => "3 or 4 character site ID used in North America",
        "timestamp" => "YYYYMMDDHHMI UTC Timestamp"
    ),
    "example" => array(
        "{timestamp}" => "199905031200",
        "{station}" => "KOUN",
    )
);

$services[] = array(
    "title" => "SHEF Station Variables",
    "url" => "/json/dcp_vars.php?station={station}",
    "desc" => "Provides SHEF variables provided by this station.",
    "vars" => array(
        "station" => "National Weather Service Location Identifier (nwsli)",
    ),
    "example" => array(
        "{station}" => "AMWI4",
    )
);

$services[] = array(
    "title" => "Data Collection Network Details",
    "url" => "/geojson/network.py?network={network}",
    "desc" => "The IEM bunches observation stations into networks. This
service provides metadata for sites within a network.  A listing of networks
can be found on <a href='/sites/locate.php'>this page.</a>",
    "vars" => array(
        "network" => "IEM Network Identifier",
    ),
    "example" => array(
        "{network}" => "IA_ASOS",
    )
);

$services[] = array(
    "title" => "IEM Archived Data Products",
    "url" => "/json/products.php",
    "desc" => "The IEM generates and archives a large number of products.
 This service provides some metadata details necessary to build programic URIs
 against this archive of data.  This service drives the <a href='/timemachine'>Timemachine</a>
 application.",
    "vars" => array(),
    "example" => array()
);

$services[] = array(
    "title" => "GOES East/West Available Scans",
    "url" => "/json/goes.py?operation=list&amp;start={start}&amp;end={end}&amp;bird={bird}&amp;product={product}",
    "desc" => "This service returns a listing of available GOES scan
          times for a period of time. This service will default to the past 
          four hours worth of data when start and end times are not specified.",
    "vars" => array(
        "operation" => "Currently always 'list'",
        "start" => "ISO-8601 UTC Timestamp (optional)",
        "end" => "ISO-8601 UTC Timestamp (optional)",
        "bird" => "GOES EAST or GOES WEST",
        "product" => "GOES Channel IR, VIS, or WV",
    ),
    "example" => array(
        "{start}" => "2014-12-02T00:00:00Z",
        "{end}" => "2014-12-04T00:00:00Z",
        "{operation}" => "list",
        "{bird}" => "EAST",
        "{product}" => "VIS",
    )
);

$services[] = array(
    "title" => "RIDGE Single Site Available NEXRADs",
    "url" => "/json/radar?operation=available&amp;lat={lat}&amp;lon={lon}&amp;start={start}",
    "desc" => "This service returns an estimate of which NEXRAD RADARs have
imagery available for the timestamp and latitude / longitude location you specify.",
    "vars" => array(
        "lat" => "Point location latitude (degrees north)",
        "lon" => "Point location longitude (degrees east)",
        "start" => "ISO-8601 UTC Timestamp"
    ),
    "example" => array(
        "{lat}" => 41.99,
        "{lon}" => 93.50,
        "{start}" => "2012-12-01T00:00:00Z",
    )
);

$services[] = array(
    "title" => "RIDGE Current Metadata by Product",
    "url" => "/json/ridge_current.py?product={product}",
    "desc" => "This service returns a listing of the most recent image for
          a given product from all collected RADAR sites.",
    "vars" => array(
        "product" => "Level III Product {N0B, N0S, N0U, N0Z, NET}"
    ),
    "example" => array(
        "{product}" => 'N0B'
    )
);

$services[] = array(
    "title" => "RIDGE Single Site Available Products for single NEXRAD",
    "url" => "/json/radar?operation=products&amp;radar={radar}&amp;start={start}",
    "desc" => "This service returns available NEXRAD level 3 products for
a given RADAR and date.",
    "vars" => array(
        "radar" => "NEXRAD 3 character identifier",
        "start" => "ISO-8601 UTC Timestamp"
    ),
    "example" => array(
        "{radar}" => 'DMX',
        "{start}" => "2012-12-01T00:00:00Z",
    )
);

$services[] = array(
    "title" => "RIDGE Single Site Available Volume Scan Times",
    "url" => "/json/radar?operation=list&amp;radar={radar}&amp;product={product}&amp;start={start}&amp;end={end}",
    "desc" => "This service returns NEXRAD volume scan times for a given
RADAR, level 3 product, and start/end timestamp.",
    "vars" => array(
        "radar" => "NEXRAD 3 character identifier",
        "product" => "Three character level 3 NEXRAD product identifier.",
        "start" => "ISO-8601 UTC Timestamp",
        "end" => "ISO-8601 UTC Timestamp"
    ),
    "example" => array(
        "{radar}" => 'DMX',
        "{product}" => 'N0Q',
        "{start}" => "2012-12-01T00:00:00Z",
        "{end}" => "2012-12-01T23:59:59Z",
    )
);

$services[] = array(
    "title" => "NWS State UGC Codes",
    "url" => "/json/state_ugc.php?state={state}",
    "desc" => "This service returns metadata for UGC codes used by the
National Weather Service to issue warnings for in a given state.",
    "vars" => array(
        "state" => "Two character state identifier",
    ),
    "example" => array(
        "{state}" => 'IA'
    )
);

$services[] = array(
    "title" => "NWS Text Product",
    "url" => "/json/nwstext.py?product_id={product_id}",
    "desc" => "This service returns the raw text of a NWS Text Product.",
    "vars" => array(
        "product_id" => "String that uniquely (not fully) indentifies a text product.",
    ),
    "example" => array(
        "{product_id}" => '201302241745-KDMX-FXUS63-AFDDMX'
    )
);

$services[] = array(
    "title" => "IEM Tracked Station Metadata Changes",
    "url" => "/json/stations.php?date={date}",
    "desc" => "This service returns metadata for any IEM tracked
station locations with changed metadata since the given date.  This provides
a programic mechanism to keep up with metadata updates done on a daily basis.",
    "vars" => array(
        "date" => "Request changes since this date",
    ),
    "example" => array(
        "{date}" => date('Y-m-d')
    )
);

$services[] = array(
    "title" => "IEM Webcam Availability",
    "url" => "/json/webcams.php?network={network}&amp;ts={ts}",
    "desc" => "This service returns metadata on available webcam imagery
for a given network that collects webcams and a UTC timestamp.",
    "vars" => array(
        "network" => "IEM Webcam network (KCCI, KELO, KCRG, IDOT)",
        "ts" => "UTC Timestamp that you want images for",
    ),
    "example" => array(
        "{network}" => "KCCI",
        "{ts}" => "201212070600",
    )
);
$table = "";
$TABLE_SCHEMA = <<<EOM
<br /><span class="badge">Returns JSON Table Schema</span> This service
uses <a href="https://frictionlessdata.io/specs/table-schema/">JSON Table Schema</a>
for returned content.
EOM;
foreach ($services as $key => $ws) {
    $url = $ws['url'];
    if (strpos($url, "?help") !== FALSE) {
        $table .= sprintf(
            '<div class="panel panel-default">' .
                '<div class="panel-heading">' .
                '<h3 class="panel-title"><strong><a href="#%s">' .
                '<i class="fa fa-bookmark"></i></a> <a name="%s">%s</a></strong></h3>' .
                '</div>' .
                '<div class="panel-body">' .
                'This service has a dedicated help page, <a href="%s">click here</a>.' .
                '</div>' .
                '</div>',
            urlencode($ws["title"]),
            urlencode($ws["title"]),
            $ws["title"],
            $ws["url"],
        );
        continue;
    }
    $uriadd = (strpos($url, "?") === FALSE) ? "?" : "&amp;";
    $ts = array_key_exists("table_schema", $ws) ? $TABLE_SCHEMA : "";
    $tc = '';
    foreach ($ws['vars'] as $key2 => $vs) {
        $tc .= sprintf("<tr><th>%s</th><td>%s</td></tr>", $key2, $vs);
    }
    foreach ($ws['example'] as $key2 => $vs) {
        $url = str_replace($key2, $vs, $url);
    }
    $td = sprintf(
        "<a class=\"btn btn-default\" href=\"%s%s\">Example JSON</a>" .
            "&nbsp; <a class=\"btn btn-default\" " .
            "href=\"%s%s%scallback=gotData\">Example JSONP</a>",
        ROOTURL,
        $url,
        ROOTURL,
        $url,
        $uriadd
    );
    $table .= sprintf(
        '<div class="panel panel-default">' .
            '<div class="panel-heading">' .
            '<h3 class="panel-title"><strong><a href="#%s">' .
            '<i class="fa fa-bookmark"></i></a> <a name="%s">%s</a></strong></h3>' .
            '</div>' .
            '<div class="panel-body">' .
            '%s' .
            '<br /><strong>URI Pattern:</strong><code>%s%s%scallback=gotData</code>' .
            '<br /><strong>Description:</strong> %s' .
            '%s' .
            '<br /><strong>Method GET Parameters:</strong>' .
            '<br /><table class="table table-condensed table-bordered">' .
            '%s' .
            '</table>' .
            '</div>' .
            '</div>',
        urlencode($ws["title"]),
        urlencode($ws["title"]),
        $ws["title"],
        $td,
        ROOTURL,
        $ws["url"],
        $uriadd,
        $ws["desc"],
        $ts,
        $tc
    );
}

$t->content = <<<EOF
<h3>IEM Provided JSON-P Webservices</h3>

<p>This page is an attempt to document the various JSON-P web services the
 IEM uses to drive its various applications.  These services are provided without
 warranty and may be disabled without warning if "bad things happen". We do
 try our best to keep them running, so please <a href="/info/contacts.php">Contact Us</a>
 if you have difficulties.
 
 <p>These services support <a href="http://en.wikipedia.org/wiki/JSONP">JSONP</a>,
 which is a technique that allows the deliver of data from a cross-domain origin.
 The technique involves placing or injecting &lt;script&gt; tags into your webpage
 and specifying a javascript function to callback.  For example,
 <br /><pre>
 &lt;script type="text/javascript"&gt;
  function gotData(data){
     console.log(data);
  }
 &lt;/script&gt;
 &lt;script type="text/javascript"
         src="https://mesonet.agron.iastate.edu/json/example.php?callback=gotData"&gt;
 
 </pre>

 <p>This &lt;script&gt; tag above that requests data from this server will return
 javascript that looks like:
 <br /><pre>
 gotData({"Name": "daryl", "Profession": "nerd", "Age": 99});
 </pre>

<p>These services are generally legacy with more modern services being
provided in <a class="btn btn-primary" href="/api/1/docs">
<i class="fa fa-file"></i> our API</a>.</p>

<h3>But first, perhaps there are better alternatives</h3>

<p>The following is a list of other web service providers.  They all do a better
job than this website does.  Some of these are commercial and this listing should
not be implied as an endorsement. Of course, you can just search google for
<a href="https://www.google.com/search?q=weather+api">Weather API</a> :)</p>

<ul>
 <li><a href="https://www.aerisweather.com/develop/">Aeris Weather</a></li>
 <li><a href="https://cs-docs.dtn.com/apis/">DTN</a></li>
 <li><a href="https://realearth.ssec.wisc.edu/doc/api.php">SSEC RealEarth API</a></li>
 <li><a href="https://www.wunderground.com/weather/api/">Wunderground API</a></li>
</ul>

 <p>Okay, so you are all set for documentation on what services are available!
{$table}

 <p>That is all for now. Enjoy!

EOF;
$t->render('single.phtml');
