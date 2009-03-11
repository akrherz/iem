<?php
/* Sucks to render a KML */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connect = iemdb("postgis");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";

$rs = pg_prepare($connect, "SELECT", "select askml(a) as kml
      from (select intersection(w.geom, n.geom) as a 
            from warnings_$year w, nws_ugc n WHERe gtype = 'P' 
            and w.wfo = $1 and n.wfo = w.wfo and phenomena = $2
            and eventid = $3 and significance = $4) as foo 
      WHERE not isempty(a)");

$result = pg_execute($connect, "SELECT", 
                     Array($wfo, $phenomena, $eventid, $significance) );

header("Content-Type:", "application/vnd.google-earth.kml+xml");

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
    <Style id=\"iemstyle\">
      <LineStyle>
        <width>4</width>
        <color>ffffff00</color>
      </LineStyle>
    </Style>
";

for($i=0;$row=@pg_fetch_array($result, $i);$i++){
  echo "<Placemark>
    <styleUrl>#iemstyle</styleUrl>
    <name>Intersection</name>";
  echo $row["kml"];
  echo "</Placemark>";
}
echo " </Document>
</kml>";
?>
