<?php
/* Sucks to render a KML */
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
$connect = iemdb("postgis");

$year = get_int404("year", 2006);
$wfo = isset($_GET["wfo"]) ? substr(xssafe($_GET["wfo"]), 0, 4) : "MPX";
if (strlen($wfo) > 3) {
    $wfo = substr($wfo, 1, 3);
}
$eventid = get_int404("eventid", 103);
$phenomena = isset($_GET["phenomena"]) ? substr(xssafe($_GET["phenomena"]), 0, 2) : "SV";
$significance = isset($_GET["significance"]) ? substr(xssafe($_GET["significance"]), 0, 1) : "W";

$rs = pg_prepare($connect, "SELECT", "SELECT  
           ST_askml(geom) as kml, issue, expire, status,
           round(ST_area(ST_transform(geom,9311)) / 1000000.0) as psize
           from sbw_$year 
           WHERE wfo = $1 and phenomena = $2 and 
           eventid = $3 and significance = $4
           and status = 'NEW'");

$result = pg_execute(
    $connect,
    "SELECT",
    array($wfo, $phenomena, $eventid, $significance)
);

if (pg_num_rows($result) <= 0) {
    $rs = pg_prepare($connect, "SELECT2", "SELECT 
            issue, expire, status,  
           ST_askml(u.geom) as kml,
           round(ST_area(ST_transform(u.geom,9311)) / 1000000.0) as psize
           from warnings_$year w JOIN ugcs u on (u.gid = w.gid)
           WHERE w.wfo = $1 and phenomena = $2 and 
           eventid = $3 and significance = $4 ");

    $result = pg_execute(
        $connect,
        "SELECT2",
        array($wfo, $phenomena, $eventid, $significance)
    );
}

$label = "";
if (pg_num_rows($result) > 0) {
    $row = pg_fetch_array($result, 0);
    $radarts = strtotime($row["issue"]);
    if (strtotime($row["expire"]) > time()) {
        $radarts = time();
    }
    $label = date("d M Y h:i A T", $radarts);
}
header('Content-disposition: attachment; filename=vtec.kml');
header("Content-Type: application/vnd.google-earth.kml+xml");
// abgr
$color = "7dff0000";
$ca = array(
    "TO" => "7d0000ff", "SV" => "7d00ffff", "FF" => "7d00ff00",
    "MA" => "7d00ff00"
);
if (isset($ca[$phenomena])) {
    $color = $ca[$phenomena];
}

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
    <Style id=\"iemstyle\">
      <LineStyle>
        <width>1</width>
        <color>ff000000</color>
      </LineStyle>
      <PolyStyle>
        <color>$color</color>
      </PolyStyle>
    </Style>
";

for ($i = 0; $row = pg_fetch_assoc($result); $i++) {
    echo "<Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Polygon Size:</i></font> " . $row["psize"] . " sq km
  <br /><font color=\"red\"><i>Status:</i></font> " . $vtec_status[$row["status"]] . "
   </p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <name>" . $vtec_phenomena[$phenomena] . " " . $vtec_significance[$significance]  . "</name>\n";
    echo $row["kml"];
    echo "</Placemark>";
}
echo " </Document>
</kml>";
