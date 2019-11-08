<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "API Documentation";

$srv = Array();
$srv[] = Array(
    "title" => "Current Observations",
    "api_version" => "1",
    "service" => "currents",
    "desc" => "This service provides the most recent set of observations for ".
    "a station or set of stations of your choice.",
    "endpoints" => Array(
        "/api/1/currents.txt?network=IA_ASOS" => "Get currents for Iowa ASOS Network",
        "/api/1/currents.txt?networkclass=COOP&wfo=DMX" => "Get all COOP reports for WFO DMX",
        "/api/1/currents.txt?state=IA" => "Get all currents within the state of Iowa",
        "/api/1/currents.txt?wfo=DMX" => "Get all currents within NWS WFO DMX",
        "/api/1/currents.txt?station=DSM&station=AMW" => "Get a exact station(s) for its data",
    ),

    "schema" => Array(
        "station" => "IEM used station identifier",
        "name" => "Free-form station name",
        "county" => "For US stations, the county the station resides",
        "state" => "For US/Canadian stations, the state/province the station resides",
        "network" => "IEM used network identifier",
        "local_date" => "Local date of last current observation",
        "snow" => "Snowfall reported [inch]",
        "snowd" => "Snow depth reported [inch]",
        "snoww" => "Snow Water Equivalent reported [inch]",
        "utc_valid" => "ISO Formatted timestamp of last observation [UTC]", 
        "local_valid" => "ISO Formatted timestamp of last observation (local time)",
        "tmpf" => "Air Temperature [F]",
        "max_tmpf" => "Local Calendar Day maximum temperature [F]",
        "min_tmpf" => "Locla Calendar Day minimum temperature [F]",
        "dwpf" => "Dew Point Temperature [F]",
        "relh" => "Relative Humidity [%]",
        "vsby" => "Visibility [miles]",
        "sknt" => "Wind Speed [knots], height of observation varies",
        "drct" => "Wind Direction [deg North], height of observation varies",
        "c1smv" => "Level 1 Volumetric Soil Moisture, depth varies",
        "c2smv" => "Level 2 Volumetric Soil Moisture, depth varies",
        "c3smv" => "Level 3 Volumetric Soil Moisture, depth varies",
        "c4smv" => "Level 4 Volumetric Soil Moisture, depth varies",
        "c5smv" => "Level 5 Volumetric Soil Moisture, depth varies",
        "c1tmpf" => "Level 1 Soil Temperature [F], depth varies",
        "c2tmpf" => "Level 2 Soil Temperature [F], depth varies",
        "c3tmpf" => "Level 3 Soil Temperature [F], depth varies",
        "c4tmpf" => "Level 4 Soil Temperature [F], depth varies",
        "c5tmpf" => "Level 5 Soil Temperature [F], depth varies",
        "ob_pday" => "Local Caledar Day Precipitation [inch]",
        "ob_pmonth" => "Local Calendar Day's Month to date precipitation [inch]",
        "s.pmonth" => "Local Calendar Day's Month to date precipitation [inch]",
        "max_sknt" => "Local Calendar Day Max Wind Speed [knots]",
        "max_gust" => "Local Calendar Day Max Wind Gust [knots]",
        "gust" => "Current Wind Gust [knots]",
        "mslp" => "Sea-level Pressure [mb]",
        "pres" => "Atmospheric Surface Pressure [inch]",
        "scond0" => "Road Pavement Surface Condition 0",
        "scond1" => "Road Pavement Surface Condition 1",
        "scond2" => "Road Pavement Surface Condition 2",
        "scond3" => "Road Pavement Surface Condition 3",
        "srad" => "Solar Radiation [w/m2]",
        "tsf0" => "Road Pavement Temperature [F] 0", 
        "tsf1" => "Road Pavement Temperature [F] 1",
        "tsf2" => "Road Pavement Temperature [F] 2",
        "tsf3" => "Road Pavement Temperature [F] 3",
        "rwis_subf" => "RWIS Sub-grade temperature [F]",
        "raw" => "A raw form of the observation processed, sometimes METAR",
        "phour" => "Reported observed hourly precipitation total [inch]",
        "skyl1" => "Sky Coverage Level 1 [kft]",
        "skyl2" => "Sky Coverage Level 2 [kft]",
        "skyl3" => "Sky Coverage Level 3 [kft]",
        "skyl4" => "Sky Coverage Level 4 [kft]",
        "skyc1" => "Sky Coverage Amount 1 [string]",
        "skyc2" => "Sky Coverage Amount 2 [string]",
        "skyc3" => "Sky Coverage Amount 3 [string]",
        "skyc4" => "Sky Coverage Amount 4 [string]",
        "alit" => "Pressure Altimeter [inch]",
        "wxcodes" => "Space separated METAR weather codes reported",
        "utc_max_gust_ts" => "Time of maximum wind gust in UTC",
        "local_max_gust_ts" => "Time of maximum wind gust in local time",
        "utc_max_sknt_ts" => "Time of maximum wind speed in UTC",
        "local_max_sknt_ts" => "Time of maximum wind speed in local time",
        "pday" => "Local Calendar Day Precipitation [inch]",
        )
    );

$table = "";
foreach($srv as $unused => $ws){
    $table .= sprintf("<div class='sect'><strong><a href=\"#%s\">".
        "<i class=\"fa fa-bookmark\"></i></a> <a name=\"%s\">%s</a></strong>".
        "<br /><strong>Description:</strong> %s",
        urlencode($ws["service"]), urlencode($ws["service"]),
        $ws["title"], $ws["desc"]);
    $table .= <<<EOM
    <p><strong>Service Endpoint Examples</strong>
<table class="table table-condensed table-striped">
EOM;
    foreach($ws['endpoints'] as $key => $ep){
        $table .= sprintf("<tr><th>%s%s</th><td>%s</td></tr>", ROOTURL,
            $key, $ep);
    }
    $table .= <<<EOM
</table>

<p><span class="badge">Returns JSON Table Schema</span> This service
uses <a href="https://frictionlessdata.io/specs/table-schema/">JSON Table Schema</a>
for returned content. Here's a description of the column identifiers used.
<table class="table table-condensed table-striped">
EOM;
    foreach($ws['schema'] as $key => $desc){
        $table .= sprintf("<tr><th>%s</th><td>%s</td></tr>", $key, $desc);
    }
    $table .= "</table>";
    $table .= "</div>\n";
}

$t->content = <<< EOF

<h3>IEM API</h3>
		
<p>For what it is worth, this page attempts to document various APIs available
to access IEM processed datasets.</p>

<h3>But first, perhaps there are better alternatives</h3>

<p>The following is a list of other web service providers.  They all do a better
job than this website does.  Some of these are commercial and this listing should
not be implied as an endorsement. Of course, you can just search google for
<a href="https://www.google.com/search?q=weather+api">Weather API</a> :)</p>

<ul>
 <li><a href="https://www.aerisweather.com/develop/">Aeris Weather</a></li>
 <li><a href="https://darksky.net/dev/">DarkSky</a></li>
 <li><a href="https://realearth.ssec.wisc.edu/doc/api.php">SSEC RealEarth API</a></li>
 <li><a href="https://www.wunderground.com/weather/api/">Wunderground API</a></li>
</ul>

<h3>Some IEM API concepts</h3>

<p>The basic URI form is<br />
<code>https://mesonet.agron.iastate.edu/api/&lt;api_version&gt;/&lt;service&gt;.&lt;format&gt;?GETVARS&amp;&lt;callback=callback&gt;</code>

<br><strong>Where</strong>
<ul>
 <li><strong>api_version</strong> is some number the versions what is available for GETVARS and resulting 
schema</li>
 <li><strong>service</strong> is the service endpoint</li>
 <li><strong>format</strong> is the type of data returned, ie json, geojson, txt, kml, etc</li>
 <li><strong>GETVARS</strong> paramaters passed on the URL by HTTP GET</li>
 <li><strong>callback=callback</strong> <i>Optional</i>, for the context of JSON, GeoJSON, the callback
function used for JSON(P).</li>
</ul>
		
<p>Okay, so you are all set for documentation on what services are available!

{$table}

EOF;

$t->render('single.phtml');

?>