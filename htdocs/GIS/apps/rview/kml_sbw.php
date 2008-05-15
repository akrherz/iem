<?php
/* Sucks to render a KML */
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");
$connect = iemdb("postgis");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";

/* Now we fetch warning and perhaps polygon */
$query2 = "SELECT *, astext(geom) as t, askml(geom) as kml,
           round(area(transform(geom,2163)) / 1000000.0) as psize,
           length(CASE WHEN svs IS NULL THEN '' ELSE svs END) as sz 
           from warnings_$year 
           WHERE wfo = '$wfo' and phenomena = '$phenomena' and 
           eventid = $eventid and significance = '$significance'";
if ($significance == "W" && 
   ($phenomena == "SV" or $phenomena == "TO" or $phenomena == "MA" or $phenomena == "FF"))
{
  $query2 .= " and gtype = 'P'";
}
$result = pg_exec($connect, $query2 ." ORDER by sz DESC, updated DESC, gtype ASC");
$row = pg_fetch_array($result, 0);

header("Content-Type:", "application/vnd.google-earth.kml+xml");
// abgr
$color = "7dff0000";
$ca = Array("TO" => "7d0000ff", "SV" => "7dffff00", "FF" => "7d00ff00",
             "MA" => "7d00ff00");
if (isset($ca[$phenomena])) { $color = $ca[$phenomena]; }

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
    <Style id=\"iemstyle\">
      <LineStyle>
        <width>1.5</width>
        <color>$color</color>
      </LineStyle>
      <PolyStyle>
        <color>$color</color>
      </PolyStyle>
    </Style>
  <Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Polygon Size:</i></font> ". $row["psize"] ." km^2
  <br /><font color=\"red\"><i>Status:</i></font> ". $vtec_status[$row["status"]] ."
   </p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <name>". $vtec_phenomena[$phenomena] ." ". $vtec_significance[$significance]  ."</name>\n";
echo $row["kml"];
echo "</Placemark>
 </Document>
</kml>";

?>
