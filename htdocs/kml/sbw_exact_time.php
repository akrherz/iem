<?php
/* Sucks to render a KML */
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/reference.php";
$vtec_action = $reference["vtec_action"];
$vtec_phenomena = $reference["vtec_phenomena"];
$vtec_significance = $reference["vtec_significance"];
$connect = iemdb("postgis");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";

$rs = pg_prepare($connect, "SELECT", "SELECT issue, expire, status, 
           ST_askml(geom) as kml,
           round(ST_area(ST_transform(geom,9311)) / 1000000.0) as psize
           from sbw_$year 
           WHERE wfo = $1 and phenomena = $2 and 
           eventid = $3 and significance = $4 and status = 'NEW'");

$result = pg_execute($connect, "SELECT", 
                     Array($wfo, $phenomena, $eventid, $significance) );
$row = pg_fetch_array($result, 0);
$radarts = strtotime( $row["issue"] );
if (strtotime( $row["expire"] ) > time()){
  $radarts = time();
}

header("Content-Type: application/vnd.google-earth.kml+xml");
// abgr
$color = "7dff0000";
$ca = Array("TO" => "7d0000ff", "SV" => "7d00ffff", "FF" => "7d00ff00",
             "MA" => "7d00ff00");
if (isset($ca[$phenomena])) { $color = $ca[$phenomena]; }

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
 <ScreenOverlay id=\"legend_bar\">
   <visibility>1</visibility>
   <Icon>
       <href>{$EXTERNAL_BASEURL}/kml/timestamp.php?label=". date("d M Y h:i A T", $radarts) ."</href>
   </Icon>
   <description>WaterWatch Legend</description>
   <overlayXY x=\".3\" y=\"0.99\" xunits=\"fraction\" yunits=\"fraction\"/>
   <screenXY x=\".3\" y=\"0.99\" xunits=\"fraction\" yunits=\"fraction\"/>
   <size x=\"0\" y=\"0\" xunits=\"pixels\" yunits=\"pixels\"/>
  </ScreenOverlay>
  <Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Polygon Size:</i></font> ". $row["psize"] ." sq km
  <br /><font color=\"red\"><i>Status:</i></font> ". $vtec_action[$row["status"]] ."
   </p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <name>". $vtec_phenomena[$phenomena] ." ". $vtec_significance[$significance]  ."</name>\n";
echo $row["kml"];
echo "</Placemark>
 </Document>
</kml>";
