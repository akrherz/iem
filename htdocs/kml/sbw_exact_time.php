<?php
/* Sucks to render a KML */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");
$connect = iemdb("postgis");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";

$rs = pg_prepare($connect, "SELECT", "SELECT *, astext(geom) as t, 
           askml(geom) as kml,
           round(area(transform(geom,2163)) / 1000000.0) as psize,
           length(CASE WHEN svs IS NULL THEN '' ELSE svs END) as sz 
           from warnings_$year 
           WHERE wfo = $1 and phenomena = $2 and 
           eventid = $3 and significance = $4
           and gtype = 'P' ORDER by sz DESC, updated DESC, gtype ASC");

$result = pg_execute($connect, "SELECT", 
                     Array($wfo, $phenomena, $eventid, $significance) );
$row = pg_fetch_array($result, 0);
$radarts = strtotime( $row["issue"] );
if (strtotime( $row["expire"] ) > time()){
  $radarts = time();
}

header("Content-Type:", "application/vnd.google-earth.kml+xml");
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
       <href>http://mesonet.agron.iastate.edu/kml/timestamp.php?label=". strftime("%d%%20%B%%20%Y%%20%-I:%M%%20%p%%20%Z", $radarts) ."</href>
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
