<?php
/* 
 * RSS Feed of new IEM added station tables
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 37);
require_once "../../include/database.inc.php";
require_once "../../include/memcache.php";


$cached_rss = cacheable("newstations_rss", 3600)(function () {

    $conn = iemdb("mesosite");
    $rs = pg_exec(
        $conn,
        "SELECT s.*, ST_x(geom) as lon, ST_y(geom) as lat, t.name as netname " .
            "from stations s JOIN networks t ON (t.id = s.network) " .
            "WHERE s.elevation > -990 ORDER by iemid DESC LIMIT 50"
    );

    $s = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n";
    $s .= "<feed xmlns=\"http://www.w3.org/2005/Atom\" xmlns:georss=\"http://www.georss.org/georss\">\n";
    $s .= "<title>Iowa Environmental Mesonet - New Stations GeoRSS</title>\n";
    $s .= "<subtitle>Iowa Environmental Mesonet - New Stations GeoRSS</subtitle>\n";
    $s .= "<link href=\"https://mesonet.agron.iastate.edu/sites/locate.php\" />\n";
    $s .= "<updated>" . gmdate('Y-m-d\\TH:i:s\\Z') . "</updated>\n";
    $s .= "<id>https://mesonet.agron.iastate.edu/sites/locate.php</id>\n";
    $s .= "<author><name>daryl herzmann</name><email>akrherz@iastate.edu</email></author>\n";

    for ($i = 0; $row = pg_fetch_array($rs); $i++) {
        $cbody = "<pre>\n";
        $cbody .= "ID     : " . $row["id"] . "\n";
        $cbody .= "Name   : " . $row["name"] . "\n";
        $cbody .= "Lat    : " . $row["lat"] . "\n";
        $cbody .= "Lon    : " . $row["lon"] . "\n";
        $cbody .= "Ele [m]: " . $row["elevation"] . "\n";
        $cbody .= "Network: " . $row["netname"] . " (" . $row["network"] . ")\n";
        $cbody .= "</pre>\n";
        $cbody = str_replace("&", "&amp;", $cbody);
        $cbody = str_replace(">", "&gt;", $cbody);
        $cbody = str_replace("<", "&lt;", $cbody);
        $s .= "<entry>\n";
        $s .= "<title>" . $row["name"] . " [" . $row["id"] . "]</title>\n";
        $s .= "<author><name>Daryl Herzmann</name><email>akrherz@iastate.edu</email></author>\n";
        $s .= "<link href=\"https://mesonet.agron.iastate.edu/sites/site.php?station=" . $row["id"] . "&amp;network=" . $row["network"] . "\" />\n";
        $s .= "<content type=\"html\">{$cbody}</content>\n";
        $s .= "<id>https://mesonet.agron.iastate.edu/sites/site.php?station=" . $row["id"] . "&amp;network=" . $row["network"] . "</id>\n";
        $s .= "<updated>" . gmdate('Y-m-d\\TH:i:s\\Z', strtotime($row["modified"])) . "</updated>\n";
        $s .= "<georss:point>" . $row["lat"] . " " . $row["lon"] . "</georss:point>\n";
        $s .= "</entry>\n";
    }
    $s .= "</feed>\n";
    return $s;
});

header("Content-type: text/xml");
echo $cached_rss();
