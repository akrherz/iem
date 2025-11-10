<?php
/*
 * RSS Feed of new IEM added station tables
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 37);
require_once "../../include/database.inc.php";
require_once "../../include/memcache.php";


$cached_rss = cacheable("newstations_rss", 3600)(function () {

    global $EXTERNAL_BASEURL;
    // Get the actual request URL for self-link
    $protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? "https://" : "http://";
    $self_url = $protocol . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];

    $conn = iemdb("mesosite");
    $rs = pg_query(
        $conn,
        "SELECT s.*, ST_x(geom) as lon, ST_y(geom) as lat, t.name as netname " .
            "from stations s JOIN networks t ON (t.id = s.network) " .
            "WHERE s.elevation > -990 ORDER by iemid DESC LIMIT 50"
    );

    $s = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n";
    $s .= "<feed xmlns=\"http://www.w3.org/2005/Atom\" xmlns:georss=\"http://www.georss.org/georss\">\n";
    $s .= "<title>Iowa Environmental Mesonet - New Stations</title>\n";
    $s .= "<subtitle>Recently added weather stations to the IEM network collection</subtitle>\n";
    $s .= "<link rel=\"alternate\" type=\"text/html\" href=\"{$EXTERNAL_BASEURL}/sites/locate.php\" />\n";
    $s .= "<link rel=\"self\" type=\"application/atom+xml\" href=\"" . htmlspecialchars($self_url, ENT_XML1, 'UTF-8') . "\" />\n";
    $s .= "<updated>" . gmdate('Y-m-d\\TH:i:s\\Z') . "</updated>\n";
    $s .= "<id>{$EXTERNAL_BASEURL}/sites/new-rss.php</id>\n";
    $s .= "<author><name>daryl herzmann</name><email>akrherz@iastate.edu</email></author>\n";

    while ($row = pg_fetch_assoc($rs)) {
        $station_id = htmlspecialchars($row["id"], ENT_XML1, 'UTF-8');
        $station_name = htmlspecialchars($row["name"], ENT_XML1, 'UTF-8');
        $network = htmlspecialchars($row["network"], ENT_XML1, 'UTF-8');
        $netname = htmlspecialchars($row["netname"], ENT_XML1, 'UTF-8');
        $lat = htmlspecialchars($row["lat"], ENT_XML1, 'UTF-8');
        $lon = htmlspecialchars($row["lon"], ENT_XML1, 'UTF-8');
        $elevation = htmlspecialchars($row["elevation"], ENT_XML1, 'UTF-8');

        $link = "{$EXTERNAL_BASEURL}/sites/site.php?station={$station_id}&amp;network={$network}";

        // Build HTML content (properly escaped)
        $cbody = "&lt;dl&gt;";
        $cbody .= "&lt;dt&gt;Station ID&lt;/dt&gt;&lt;dd&gt;{$station_id}&lt;/dd&gt;";
        $cbody .= "&lt;dt&gt;Name&lt;/dt&gt;&lt;dd&gt;{$station_name}&lt;/dd&gt;";
        $cbody .= "&lt;dt&gt;Latitude&lt;/dt&gt;&lt;dd&gt;{$lat}&lt;/dd&gt;";
        $cbody .= "&lt;dt&gt;Longitude&lt;/dt&gt;&lt;dd&gt;{$lon}&lt;/dd&gt;";
        $cbody .= "&lt;dt&gt;Elevation&lt;/dt&gt;&lt;dd&gt;{$elevation} m&lt;/dd&gt;";
        $cbody .= "&lt;dt&gt;Network&lt;/dt&gt;&lt;dd&gt;{$netname} ({$network})&lt;/dd&gt;";
        $cbody .= "&lt;/dl&gt;";

        $modified_time = strtotime($row["modified"]);
        $updated = gmdate('Y-m-d\\TH:i:s', $modified_time) . 'Z';

        $s .= "<entry>\n";
        $s .= "<title>{$station_name} [{$station_id}]</title>\n";
        $s .= "<link rel=\"alternate\" type=\"text/html\" href=\"{$link}\" />\n";
        $s .= "<id>{$link}</id>\n";
        $s .= "<published>{$updated}</published>\n";
        $s .= "<updated>{$updated}</updated>\n";
        $s .= "<content type=\"html\">{$cbody}</content>\n";
        $s .= "<georss:point>{$lat} {$lon}</georss:point>\n";
        $s .= "</entry>\n";
    }
    $s .= "</feed>\n";
    return $s;
});

header("Content-type: text/xml");
echo $cached_rss();
