<?php 
  require_once "../../config/settings.inc.php";
  require_once "../../include/myview.php";
  $t = new MyView();
  $t->title = "JSON(P) Web Services";


  $services = array();

  $services[] = Array(
      "title" => "United States Drought Monitor",
      "url" => "/geojson/usdm.py?date={date}",
      "desc" => "The US Drought Monitor valid for the given date.  You do not".
      " need to specify the exact date on which the Drought Monitor was issued.".
      " The service will compute the date on which the Drought Monitor was issued".
      " given the provided date.  Not specifying a date will provide the current".
      " Drought Monitor. Archive begins on Jan 2000.",
      "vars" => Array(
          "date" => "Date (optional)"
          ),
      "example" => Array(
          "{date}" => "2017-07-18"
          )
      );

  $services[] = Array(
      "table_schema" => TRUE,
      "title" => "United States Drought Monitor by Point",
      "url" => "/api/1/usdm_bypoint.json?sdate={sdate}&amp;edate={edate}&amp;".
        "lon={lon}&amp;lat={lat}",
      "desc" => "The US Drought Monitor query by latitude and longitude point.".
      " The start and end dates are optional and default to period of record ".
      "data. The archive begins on Jan 2000.",
      "vars" => Array(
          "sdate" => "Start Date (optional)",
          "edate" => "End Date (optional)",
          "lon" => "East Longitude (deg)",
          "lat" => "North Latitude (deg)"
          ),
      "example" => Array(
          "{sdate}" => "2014-01-01",
          "{edate}" => "2016-01-01",
          "{lon}" => -96.54,
          "{lat}" => 43.21,
          )
      );
  
  $services[] = Array(
  		"title" => "Single Station Last Observation",
  		"url" => "/json/current.py?station={station}&amp;network={network}",
  		"desc" => "The most recent observation for an IEM tracked site.",
  		"vars" => Array(
  				"station" => "Station Identifier",
  				"network" => "Network Identifier",
  				),
  		"example" => Array(
  				"{station}" => "AMW",
  				"{network}" => "IA_ASOS",
  				)
  		);
  
  $services[] = Array(
  		"title" => "Oregon State PRISM Grid Cell Daily Sample",
  		"url" => "/json/prism/{lon}/{lat}/{date_or_daterange}",
  		"desc" => "Produces a daily time series for a grid cell that covers".
  		" the specified latitude and longitude (negative E values).".
  		" Credit: <a href='http://prism.oregonstate.edu'>PRISM Climate Group</a>,".
  		" Oregon State University, created 4 Feb 2004.",
  		"vars" => Array(
  				"lat" => "Latitude (deg N)",
  				"lon" => "Longitude (deg E)",
  				"date_or_daterange" => "YYYYmmdd or YYYYmmdd-YYYYmmdd (inclusive)",
  				),
  		"example" => Array(
  				"{lat}" => "41.99",
  				"{lon}" => "-95.55",
  				"{date_or_daterange}" => "20151215-20160115"
  				)
  		);
  
  $services[] = Array(
      "title" => "NCEP Stage IV Hourly Precipitation",
      "url" => "/json/stage4/{lon}/{lat}/{utc_date}",
      "desc" => "This service provides a grid point sampling of the NCEP".
      " Stage IV product.  The date provided the service is a UTC date. Note".
      " that the hourly stage IV data does not receive the level of QC that".
      " the 6, 12, and 24 hour summaries do.",
      "vars" => Array(
          "lat" => "Latitude (deg N)",
          "lon" => "Longitude (deg E)",
          "utc_date" => "YYYY-mm-dd",
          ),
      "example" => Array(
          "{lat}" => "41.99",
          "{lon}" => "-95.55",
          "{utc_date}" => "2017-08-21"
          )
      );
  
  $services[] = Array(
  		"title" => "Local Storm Reports for One Storm Based Warning",
  		"url" => "/geojson/lsr.php?year={year}&amp;wfo={wfo}".
  			"&amp;eventid={eventid}&amp;phenomena={phenomena}".
  			"&amp;significance={significance}",
  		"desc" => "Produces the storm reports that spatially and temporally
  		coincide with a given Storm Based Warning. This only works for
  		warnings that had polygons associated with them and not other VTEC
  		products.",
  		"vars" => Array(
  				"wfo" => "3 character NWS Office",
  				"year" => "Year of VTEC Issuance",
  				"phenomena" => "2 character VTEC Phenomena Code",
  				"significance" => "1 character VTEC Significance Code",
  				"eventid" => "VTEC Event ID",
  				),
  		"example" => Array(
  				"{wfo}" => "DVN",
  				"{year}" => "2015",
  				"{phenomena}" => "TO",
  				"{significance}" => "W",
  				"{eventid}" => 10,
  				)
  		);

  $services[] = Array(
  		"title" => "Local Storm Reports for a given period",
  		"url" => "/geojson/lsr.php?sts={sts}&amp;ets={ets}".
  		"&amp;wfos={wfos}",
  		"desc" => "Produces the storm reports for a given office or offices
  		valid for a specified period (inclusive).",
  		"vars" => Array(
  				"wfo" => "3 character NWS Office ".
  					"(comma seperated for multiple, leave blank for all)",
  				"sts" => "UTC Start Timestamp YYYYmmddHHMM",
  				"ets" => "UTC End Timestamp YYYYmmddHHMM",
  				),
  		"example" => Array(
  				"{wfos}" => "DVN,DMX,ARX",
  				"{sts}" => "201605100000",
  				"{ets}" => "201605110000",
  				)
  		);
  
  
  $services[] = Array(
  		"title" => "Current NEXRAD Storm Attribute Table",
  		"url" => "/geojson/nexrad_attr.geojson",
  		"desc" => "A GeoJSON summary of current NEXRAD Storm Attributes",
  		"vars" => Array(
  				),
  		"example" => Array(
  				)
  		);
  
  $services[] = Array(
  		"title" => "Archived NEXRAD Storm Attribute Table",
  		"url" => "/geojson/nexrad_attr.geojson?valid={valid}",
  		"desc" => "A GeoJSON summary of archived NEXRAD Storm Attributes.".
  		" For the supplied UTC timestamp, the closest scan time within a 20 minute".
  		" window is found for each RADAR.  That scan time is returned.",
  		"vars" => Array(
  				"valid" => "ISO-8601 timestamp YYYY-mm-ddTHH:MM:SSZ"
  				),
  		"example" => Array(
  				"{valid}" => "2016-05-10T00:01:00Z"
  				)
  		);
  
  $services[] = Array(
  		"title" => "IEM Tracked Networks Metadata",
  		"url" => "/geojson/networks.geojson",
  		"desc" => "A GeoJSON listing of IEM labelled networks.",
  		"vars" => Array(
  				),
  		"example" => Array(
  				)
  		);
  
  $services[] = Array(
  		"title" => "NWS Impact Based Warnings Tags",
  		"url" => "/json/ibw_tags.py?year={year}&amp;wfo={wfo}",
  		"desc" => "Produces a listing of Impact Warning Tags used in Severe ".
		  "Thunderstorm, Tornado, Marine, and Flash Flood Warnings ". 
		  "warnings by NWS Forecast Office and Year.",
  		"vars" => Array(
  				"wfo" => "3 character NWS Office",
  				"year" => "Year of interest"
  		),
  		"example" => Array(
  				"{wfo}" => "DVN",
  				"{year}" => "2015"
  		)
  );

  $services[] = Array(
  		"title" => "Iowa Winter Road Conditions",
  		"url" => "/geojson/winter_roads.geojson",
  		"desc" => "This service provides the most recent Iowa Winter Road
  		Conditions.",
  		"vars" => Array(
  				),
  		"example" => Array(
  				)
  		);
  
          $services[] = Array(
            "title" => "MRMS Max Estimated Hail Size (MESH) Contours",
            "url" => "/data/gis/shape/4326/us/mrms_mesh_1440min.geojson",
            "desc" => "This static file provides MRMS MESH Hail Contours. It
            is updated every 2 minutes and you can also find a 2min, 30min,
            and 60min interval file.",
            "vars" => Array(
                    ),
            "example" => Array(
                    )
            );

  $services[] = Array(
  		"title" => "NWS COOP Station Climatology",
  		"url" => "/json/climodat_stclimo.py?station={station}&amp;syear={syear}&amp;eyear={eyear}",
  		"desc" => "Produces a listing of daily climatology for an IEM tracked
  		long term climodat site in the midwestern US.",
  		"vars" => Array(
  				"station" => "6 character station identifier",
  				"syear" => "Inclusive start year of the period of interest",
  				"syear" => "Exclusive end year of the period of interest"
  		),
  		"example" => Array(
  				"{station}" => "IA0200",
  				"{syear}" => "1800",
  				"{eyear}" => "2016",
  		)
  );

  $services[] = Array(
  		"title" => "NWS COOP Network Climatology for one day",
  		"url" => "/geojson/climodat_dayclimo.py?network={network}&amp;day={day}&amp;month={month}&amp;syear={syear}&amp;eyear={eyear}",
  		"desc" => "Produces a listing of climatology for a single state
  		for a single day.",
  		"vars" => Array(
  				"network" => "state network identifier",
  				"month" => "Numeric month of interest (1-12)",
  				"day" => "Numeric day of interest (1-31)",
  				"syear" => "Inclusive start year of the period of interest",
  				"syear" => "Exclusive end year of the period of interest"
  		),
  		"example" => Array(
  				"{network}" => "IACLIMATE",
  				"{month}" => "4",
  				"{day}" => "3",
  				"{syear}" => "1800",
  				"{eyear}" => "2016",
  		)
  );
  
  $services[] = Array(
      "title" => "NWS VTEC Maximum Event ID by Year",
      "url" => "/json/vtec_max_etn.py?year={year}",
      "desc" => "Produces a listing of the maximum eventid used for each ".
      "NWS Forecast Office, VTEC Phenomena and VTEC Significance.",
      "vars" => Array(
          "year" => "YYYY year"
          ),
      "example" => Array(
          "{year}" => "2015"
          )
      );
  

  $services[] = Array(
      "title" => "NWS VTEC Event Geometries",
      "url" => "/geojson/vtec_event.py?wfo={wfo}&year={year}".
      "&phenomena={phenomena}&etn={etn}&significance={significance}",
      "desc" => "Produces GeoJSON for a given VTEC Event.",
      "vars" => Array(
          "wfo" => "3 or 4 character WFO identifier",
          "year" => "YYYY year",
          "etn" => "VTEC Event ID",
          "phenomena" => "2 Character VTEC Phenomena Code",
          "significance" => "1 Character VTEC Significance Code",
          "sbw" => "1 or 0, flag to return Storm Based Polygon(1) or Counties",
          "lsrs" => "1 or 0, flag to return local storm reports",
          ),
      "example" => Array(
          "{wfo}" => "DMX",
          "{year}" => "2015",
          "{etn}" => "10",
          "{significance}" => "W",
          "{phenomena}" => "TO",
          "{lsrs}" => '0',
          "{sbw}" => '1',
          )
      );
  
  $services[] = Array(
      "title" => "NWS VTEC Event Metadata",
      "url" => "/json/vtec_event.py?wfo={wfo}&year={year}".
        "&phenomena={phenomena}&etn={etn}&significance={significance}",
      "desc" => "Produces metadata on a given VTEC Event.",
      "vars" => Array(
          "wfo" => "3 or 4 character WFO identifier",
          "year" => "YYYY year",
          "etn" => "VTEC Event ID",
          "phenomena" => "2 Character VTEC Phenomena Code",
          "significance" => "1 Character VTEC Significance Code",
          ),
      "example" => Array(
          "{wfo}" => "DMX",
          "{year}" => "2015",
          "{etn}" => "10",
          "{significance}" => "W",
          "{phenomena}" => "TO",
          )
      );
  
  $services[] = Array(
  		"title" => "NWS VTEC Event Listing by WFO by Year",
  		"url" => "/json/vtec_events.py?wfo={wfo}&year={year}",
		  "desc" => <<<EOM
Produces a listing of VTEC Events (watch, warning,advisories) by year by weather
forecast office.  You can optionally pass a <code>phenomena=XX</code> and
<code>significance=X</code> to the service to only return that VTEC event
type for the given WFO and year.  Additionally, there is a one-off feature
flag of <code>combo=1</code>, which has the service return and Tornado,
Severe Thunderstorm, and Flash Flood Watches/Warnings in chronological order.
EOM
		 ,
  		"vars" => Array(
  				"wfo" => "3 character WFO identifier",
  				"year" => "YYYY year"
  		),
  		"example" => Array(
  				"{wfo}" => "DMX",
  				"{year}" => "2015"
  		)
  );

  $services[] = Array(
	"title" => "NWS VTEC Event Listing by State by Year",
	"url" => "/json/vtec_events_bystate.py?state={state}&year={year}",
	"desc" => "Produces a listing of VTEC Events (watch, warning,
	advisories) by year by state.",
	"vars" => Array(
			"state" => "2 character State identifier",
			"year" => "YYYY year"
	),
	"example" => Array(
			"{state}" => "IA",
			"{year}" => "2015"
	)
);

  
  $services[] = Array(
  		"title" => "NWS Text Products by AWIPS ID and Time Period",
  		"url" => "/json/nwstext_search.py?sts={sts}&ets={ets}&awipsid={awipsid}",
  		"desc" => "Search of NWS Issued Text Products by a time period (in 
  		UTC) and an AWIPS ID (sometime called AFOS PIL).  If you specify
  		the AWIPS ID to be only three characters, the interruptation is to
  		search of that base product identifier from any issuance center. For
  		example, setting LSR would return all LSRXXX products.",
  		"vars" => Array(
  				"sts" => "YYYY-mm-ddTHH:MMZ Inclusive start period (UTC)",
  				"ets" => "YYYY-mm-ddTHH:MMZ end time period (UTC)",
  				"awipsid" => "6 character or less AWIPS ID / AFOS PIL.",
  		),
  		"example" => Array(
  				"{sts}" => "2014-11-24T00:00Z",
  				"{ets}" => "2014-11-25T00:00Z",
  				"{awipsid}" => "AFDDMX",
  		)
  );
  
  $services[] = Array(
  		"title" => "Daily NWS Climate (CLI Product) Summaries",
  		"url" => "/geojson/cli.py?dt={dt}&fmt={fmt}",
  		"desc" => "Provides a GeoJSON response summarizing all of the atomic
  		processed data from the NWS issued CLI reports.  These reports contain
  		daily temperature, precipitation, and snow data from the primary 
  		climate sites.",
  		"vars" => Array(
  				"dt" => "YYYY-mm-dd Date you want data for (optional)",
  				"fmt" => "Return format (optional) geojson (default) or csv",
  		),
  		"example" => Array(
  				"{dt}" => "2014-10-09",
  				"{fmt}" => "geojson",
  		)
  );

  $services[] = Array(
	"title" => "Yearly NWS Climate (CLI Product) Summaries for One Station",
	"url" => "/json/cli.py?station={station}&year={year}&fmt={fmt}",
	"desc" => "Provides a JSON response summarizing all of the atomic
	processed data from the NWS issued CLI reports for a single station and
	given year.  You can optionally set <code>fmt=csv</code> to get a CSV
	response.",
	"vars" => Array(
			"year" => "YYYY desired",
			"station" => "ICAO 4-character station identifier",
			"fmt" => "Return format (optional) json (default) or csv",
	),
	"example" => Array(
			"{year}" => "2019",
			"{station}" => "KDSM",
			"{fmt}" => "json",
	)
);

  $services[] = Array(
  		"title" => "IEM Tile Map Service Metadata",
  		"url" => "/json/tms.json",
  		"desc" => "Provides metadata about the currently available Tile Map
  		Services provided by the IEM.  This is useful to determine how to 
  		call back to the Tile Map Services.",
  		"vars" => Array(
  		),
  		"example" => Array(
  		)
  );
  
  $services[] = Array(
  		"title" => "Current Storm Based Warnings",
  		"url" => "/geojson/sbw.geojson?ts={ts}",
  		"desc" => "Provides a geojson format of current National Weather Service
  		storm based warnings.  There is a 15 second caching done by the server
  		to ease load.  The generation_time attribute is set on the output 
  		to diagnose when the file is valid.  You can provide a timestamp
  		to provide archived warnings back to 2002 or so.",
  		"vars" => Array(
  				"ts" => "ISO-8601 Timestamp YYYY-mm-ddTHH:MI:SSZ (optional)"
  		),
  		"example" => Array(
  				"{ts}" => "2011-04-27T22:00:00Z"
  		)
  );
  
  $services[] = Array(
  		"title" => "Search for Storm Based Warnings by Lat/Lon Point",
  		"url" => "/json/sbw_by_point.py?lon={longitude}&lat={latitude}",
  		"desc" => "Provides a listing of storm based (polygon) warnings 
  		based on the provided latitude and longitude pair for warnings 
        dating back to 1 Jan 2005.",
  		"vars" => Array(
  				"lat" => "Latitude in degrees",
  				"lon" => "Longitude in (degrees east)"
  		),
  		"example" => Array(
  				"{latitude}" => "42.5",
  				"{longitude}" => "-95.0"
  		)
  );

  $services[] = Array(
    "title" => "Search for Storm Based Warnings by Lat/Lon Point by Time",
    "url" => "/json/sbw_by_point.py?lon={longitude}&lat={latitude}&valid={valid}",
    "desc" => "Provides a listing of storm based (polygon) warnings 
    based on the provided latitude and longitude pair for warnings 
  dating back to 1 Jan 2005.  You also provide an ISO-9660
  <code>valid</code> parameter to get any storm based warnings active
  at the given UTC time and location.",
    "vars" => Array(
            "lat" => "Latitude in degrees",
            "lon" => "Longitude in (degrees east)",
            "valid" => "UTC ISO-9660 timestamp"
    ),
    "example" => Array(
            "{latitude}" => "42.5",
            "{longitude}" => "-95.0",
            "{valid}" => "2014-09-01T00:29Z"
    )
);

  $services[] = Array(
  		"title" => "Search for VTEC Events by Lat/Lon Point",
  		"url" => "/json/vtec_events_bypoint.py?lon={longitude}&lat={latitude}&sdate={sdate}&edate={edate}",
  		"desc" => "Provides a listing of VTEC events that were valid for
  		a given latitude and longitude point.",
  		"vars" => Array(
  				"lat" => "Latitude in degrees",
  				"lon" => "Longitude in (degrees east)",
  				"sdate" => "YYYY-mm-dd Start Date (UTC)",
  		  		"edate" => "YYYY-mm-dd End Date (UTC)",
                "fmt" => "(optional) Format to download as: json (default) or xlsx"    
                ),
  		"example" => Array(
  				"{latitude}" => "42.5",
  				"{longitude}" => "-95.0",
  				"{sdate}" => "2015/06/01",
  				"{edate}" => "2015/07/01",
  				)
  		);
 
  $services[] = Array(
      "title" => "Storm Prediction Center Mesoscale Convection Discussions by Lat/Lon Point",
      "url" => "/json/spcmcd.py?lon={longitude}&amp;lat={latitude}",
      "desc" => "Provides a listing of Mesoscale Convective Discussions (MCD)s dating back to".
      " October 2008.",
      "vars" => Array(
          "lat" => "Latitude in degrees",
          "lon" => "Longitude in (degrees east)",
          ),
      "example" => Array(
          "{latitude}" => "42.5",
          "{longitude}" => "-95.0",
          )
      );
  
  $services[] = Array(
  		"title" => "Storm Prediction Center Convective Outlooks by Lat/Lon Point",
  		"url" => "/json/spcoutlook.py?lon={longitude}&amp;lat={latitude}&amp;last={last}&amp;day={day}&amp;cat={cat}",
  		"desc" => "Provides a listing of convective outlooks dating back to".
  		" March 2002.",
  		"vars" => Array(
  				"lat" => "Latitude in degrees",
  				"lon" => "Longitude in (degrees east)",
  				"last" => "(Optional) Include only the last number of outlooks for each category, 0 is all",
  				"day" => "(Optional) Which outlook day to request, defaults to 1",
  				"cat" => "(Optional) Which outlook category to request, defaults to CATEGORICAL",
  				),
  		"example" => Array(
  				"{latitude}" => "42.5",
  				"{longitude}" => "-95.0",
  				"{last}" => "0",
  				"{day}" => "1",
  				"{cat}" => "CATEGORICAL",
  				)
  		);
  $services[] = Array(
  		"title" => "Storm Prediction Center Convective Outlooks by Lat/Lon Point by Time",
  		"url" => "/json/spcoutlook.py?lon={longitude}&amp;lat={latitude}&amp;time={time}&amp;day={day}&amp;cat={cat}",
  		"desc" => "Provides a listing of convective outlooks dating back to".
  		" March 2002 for a given timestamp.",
  		"vars" => Array(
  				"lat" => "Latitude in degrees",
  				"lon" => "Longitude in (degrees east)",
  				"time" => "Return the outlook valid at that time.  This time can be a generic".
  				" 'now' or some ISO-ish timestamp in the format YYYY-mm-ddTHH:MMZ.",
  				"day" => "(Optional) Which outlook day to request, defaults to 1",
  				"cat" => "(Optional) Which outlook category to request, defaults to CATEGORICAL",
  				),
  		"example" => Array(
  				"{latitude}" => "42.5",
  				"{longitude}" => "-95.0",
  				"{time}" => "2014-06-29T14:00Z",
  				"{day}" => "1",
  				"{cat}" => "CATEGORICAL",
  				)
  		);
  
  $services[] = Array(
  		"title" => "Current Polygons from Special Weather Statements (SPS)",
  		"url" => "/geojson/sps.geojson",
  		"desc" => "Provides a geojson format of current National Weather Service
  		polygons that are included with some Special Weather Statements (SPS).",
  		"vars" => Array(
  		),
  		"example" => Array(
  		)
  );
  
  $services[] = Array(
  		"title" => "Search for Warnings by UGC Code and Date Interval",
  		"url" => "/json/vtec_events_byugc.py?ugc={ugc}&edate={edate}&sdate={sdate}",
  		"desc" => "Provides a json response of archived warnings valid for the
  		given UGC code and date interval (UTC time, end date exclusive). The date
  		of product issuance is used for the date filtering.",
  		"vars" => Array(
  				"ugc" => "Five character UGC identifier used by the NWS",
  				"sdate" => "YYYY/mm/dd Start Date (UTC)",
                "edate" => "YYYY/mm/dd End Date (UTC)",
                "fmt" => "(optional) Format to download as: json (default) or xlsx"    
  		),
  		"example" => Array(
  				"{ugc}" => "IAC001",
  				"{sdate}" => "1990/06/01",
  				"{edate}" => "1990/07/01",
  		)
  );
  $services[] = Array(
  		"title" => "Storm Prediction Center Watches by Time",
  		"url" => "/json/spcwatch.py?ts={timestamp}",
  		"desc" => "Provides a geojson format of SPC watches valid at given time
		or current time if no time specified.",
  		"vars" => Array(
  				"timestamp" => "YYYYMMDDHHMI UTC Timestamp (optional)"
  		),
  		"example" => Array(
  				"{timestamp}" => "201104280000"
  		)
      );
  $services[] = Array(
          "title" => "Storm Prediction Center Watches by Point",
          "url" => "/json/spcwatch.py?lon={lon}&lat={lat}",
          "desc" => "Provides a geojson format of SPC watches valid for a ".
      "give latitude and longitude pair.  Note that these polygons are not ".
      "the official watch boundaries.",
          "vars" => Array(
              "lat" => "Latitude in degrees",
              "lon" => "Longitude in (degrees east)",
              ),
          "example" => Array(
              "{lat}" => "42.5",
              "{lon}" => "-95.0",
              )
          );
  $services[] = Array(
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
  		"vars" => Array(
  				"sid" => "3 or 4 character site ID used in North America",
  				"timestamp" => "YYYYMMDDHHMI UTC Timestamp"
  		),
  		"example" => Array(
  				"{timestamp}" => "199905031200",
  				"{station}" => "KOUN",
  		)
  );
  
  $services[] = Array(
  		"title" => "SHEF Station Variables",
  		"url" => "/json/dcp_vars.php?station={station}",
  		"desc" => "Provides SHEF variables provided by this station.",
  		"vars" => Array(
  				"station" => "National Weather Service Location Identifier (nwsli)",
  		),
  		"example" => Array(
  				"{station}" => "AMWI4",
  		)
  );
  
  $services[] = Array(
  		"title" => "Data Collection Network Details",
  		"url" => "/geojson/network.py?network={network}",
  		"desc" => "The IEM bunches observation stations into networks. This
service provides metadata for sites within a network.  A listing of networks
can be found on <a href='/sites/locate.php'>this page.</a>",
  		"vars" => Array(
  				"network" => "IEM Network Identifier",
  		),
  		"example" => Array(
  				"{network}" => "IA_ASOS",
  		)
  );
  
  $services[] = Array(
  		"title" => "IEM Archived Data Products",
  		"url" => "/json/products.php",
  		"desc" => "The IEM generates and archives a large number of products.
 This service provides some metadata details necessary to build programic URIs
 against this archive of data.  This service drives the <a href='/timemachine'>Timemachine</a>
 application.",
  		"vars" => Array(
  		),
  		"example" => Array(
  		)
  );
  
  $services[] = Array(
  		"title" => "GOES East/West Available Scans",
  		"url" => "/json/goes.py?operation=list&amp;start={start}&amp;end={end}&amp;bird={bird}&amp;product={product}",
  		"desc" => "This service returns a listing of available GOES scan
  		times for a period of time. This service will default to the past 
  		four hours worth of data when start and end times are not specified.",
  		"vars" => Array(
  				"operation" => "Currently always 'list'",
  				"start" => "ISO-8601 UTC Timestamp (optional)",
  				"end" => "ISO-8601 UTC Timestamp (optional)",
  				"bird" => "GOES EAST or GOES WEST",
  				"product" => "GOES Channel IR, VIS, or WV",
  		),
  		"example" => Array(
  				"{start}" => "2014-12-02T00:00:00Z",
  				"{end}" => "2014-12-04T00:00:00Z",
  				"{operation}" => "list",
  				"{bird}" => "EAST",
  				"{product}" => "VIS",
  		)
  );
  
  $services[] = Array(
  		"title" => "RIDGE Single Site Available NEXRADs",
  		"url" => "/json/radar?operation=available&amp;lat={lat}&amp;lon={lon}&amp;start={start}",
  		"desc" => "This service returns an estimate of which NEXRAD RADARs have
imagery available for the timestamp and latitude / longitude location you specify.",
  		"vars" => Array(
  				"lat" => "Point location latitude (degrees north)",
  				"lon" => "Point location longitude (degrees east)",
  				"start" => "ISO-8601 UTC Timestamp"
  		),
  		"example" => Array(
  				"{lat}" => 41.99,
  				"{lon}" => 93.50,
  				"{start}" => "2012-12-01T00:00:00Z",
  		)
  );
  
  $services[] = Array(
  		"title" => "RIDGE Current Metadata by Product",
  		"url" => "/json/ridge_current.py?product={product}",
  		"desc" => "This service returns a listing of the most recent image for
  		a given product from all collected RADAR sites.",
  		"vars" => Array(
  				"product" => "Level III Product {N0Q, N0S, N0U, N0Z, NET}"
  		),
  		"example" => Array(
  				"{product}" => 'N0Q'
  		 )
  );
  
  $services[] = Array(
  		"title" => "RIDGE Single Site Available Products for single NEXRAD",
  		"url" => "/json/radar?operation=products&amp;radar={radar}&amp;start={start}",
  		"desc" => "This service returns available NEXRAD level 3 products for
a given RADAR and date.",
  		"vars" => Array(
  				"radar" => "NEXRAD 3 character identifier",
  				"start" => "ISO-8601 UTC Timestamp"
  		),
  		"example" => Array(
  				"{radar}" => 'DMX',
  				"{start}" => "2012-12-01T00:00:00Z",
  		)
  );
  
  $services[] = Array(
  		"title" => "RIDGE Single Site Available Volume Scan Times",
  		"url" => "/json/radar?operation=list&amp;radar={radar}&amp;product={product}&amp;start={start}&amp;end={end}",
  		"desc" => "This service returns NEXRAD volume scan times for a given
RADAR, level 3 product, and start/end timestamp.",
  		"vars" => Array(
  				"radar" => "NEXRAD 3 character identifier",
  				"product" => "Three character level 3 NEXRAD product identifier.",
  				"start" => "ISO-8601 UTC Timestamp",
  				"end" => "ISO-8601 UTC Timestamp"
  		),
  		"example" => Array(
  				"{radar}" => 'DMX',
  				"{product}" => 'N0Q',
  				"{start}" => "2012-12-01T00:00:00Z",
  				"{end}" => "2012-12-01T23:59:59Z",
  		)
  );
  
  $services[] = Array(
  		"title" => "NWS State UGC Codes",
  		"url" => "/json/state_ugc.php?state={state}",
  		"desc" => "This service returns metadata for UGC codes used by the
National Weather Service to issue warnings for in a given state.",
  		"vars" => Array(
  				"state" => "Two character state identifier",
  		),
  		"example" => Array(
  				"{state}" => 'IA'
  		)
  );
  
  $services[] = Array(
  		"title" => "NWS Text Product",
  		"url" => "/json/nwstext.py?product_id={product_id}",
  		"desc" => "This service returns the raw text of a NWS Text Product.",
  		"vars" => Array(
  				"product_id" => "String that uniquely (not fully) indentifies a text product.",
  		),
  		"example" => Array(
  				"{product_id}" => '201302241745-KDMX-FXUS63-AFDDMX'
  		)
  );
  
  $services[] = Array(
  		"title" => "IEM Tracked Station Metadata Changes",
  		"url" => "/json/stations.php?date={date}",
  		"desc" => "This service returns metadata for any IEM tracked
station locations with changed metadata since the given date.  This provides
a programic mechanism to keep up with metadata updates done on a daily basis.",
  		"vars" => Array(
  				"date" => "Request changes since this date",
  		),
  		"example" => Array(
  				"{date}" => date('Y-m-d')
  		)
  );
  
  $services[] = Array(
  		"title" => "IEM Webcam Availability",
  		"url" => "/json/webcams.php?network={network}&amp;ts={ts}",
  		"desc" => "This service returns metadata on available webcam imagery
for a given network that collects webcams and a UTC timestamp.",
  		"vars" => Array(
  				"network" => "IEM Webcam network (KCCI, KELO, KCRG, IDOT)",
  				"ts" => "UTC Timestamp that you want images for",
  		),
  		"example" => Array(
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
  foreach($services as $key => $ws){
  	$url = $ws['url'];
  	$uriadd = (strpos($url, "?") === FALSE) ? "?": "&amp;";
  	$ts = array_key_exists("table_schema", $ws) ? $TABLE_SCHEMA: "";
	  $tc = '';
	  foreach($ws['vars'] as $key2 => $vs){
		$tc .= sprintf("<tr><th>%s</th><td>%s</td></tr>", $key2, $vs);
	  }
  	  foreach($ws['example'] as $key2 => $vs){
		$url = str_replace($key2, $vs, $url);
	  }
	$td = sprintf("<a class=\"btn btn-default\" href=\"%s%s\">Example JSON</a>".
	   "&nbsp; <a class=\"btn btn-default\" ".
	   "href=\"%s%s%scallback=gotData\">Example JSONP</a>",
			ROOTURL, $url, ROOTURL, $url, $uriadd);
	$table .= sprintf('<div class="panel panel-default">'.
	  	'<div class="panel-heading">'.
		'<h3 class="panel-title"><strong><a href="#%s">'.
		'<i class="fa fa-bookmark"></i></a> <a name="%s">%s</a></strong></h3>'.
	  	'</div>'.
	  	'<div class="panel-body">'.
		  '%s'.
		  '<br /><strong>URI Pattern:</strong><code>%s%s%scallback=gotData</code>'.
		  '<br /><strong>Description:</strong> %s'.
		   '%s'.
		  '<br /><strong>Method GET Parameters:</strong>'.
		  '<br /><table class="table table-condensed table-bordered">'.
		  '%s'.
		  '</table>'.
		'</div>'.
		'</div>', urlencode($ws["title"]), urlencode($ws["title"]),
			  $ws["title"], $td,
			  ROOTURL, $ws["url"], $uriadd, $ws["desc"], $ts, $tc);
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
 ?>
