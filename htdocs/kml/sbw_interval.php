<?php
/* Sucks to render a KML */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");
$connect = iemdb("postgis");

$ts = isset($_GET["ts"]) ? strtotime($_GET["ts"]) : die("APIFAIL");
$ts2 = isset($_GET["ts2"]) ? strtotime($_GET["ts2"]) : die("APIFAIL");

$tsSQL = date("Y-m-d H:i:00+00", $ts);
$tsSQL2 = date("Y-m-d H:i:00+00", $ts2);

$year = date("Y", $ts);
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";

$rs = pg_prepare($connect, "SELECT", "SELECT *, astext(geom) as t, 
           askml(geom) as kml,
           round(area(transform(geom,2163)) / 1000000.0) as psize,
           length(CASE WHEN svs IS NULL THEN '' ELSE svs END) as sz 
           from warnings_$year 
           WHERE wfo = $1 and issue >= $2 and issue <= $3
           and gtype = 'P' ORDER by sz DESC, updated DESC, gtype ASC");

$result = pg_execute($connect, "SELECT", 
                     Array($wfo, $tsSQL, $tsSQL2) );

header("Content-Type:", "application/vnd.google-earth.kml+xml");
// abgr
$color = "7dff0000";
$ca = Array("TO" => "7d0000ff", "SV" => "7d00ffff", "FF" => "7d00ff00",
             "MA" => "7d00ff00");

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
    <Style id=\"TOstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d0000ff</color></PolyStyle>
    </Style>
    <Style id=\"MAstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d00ff00</color></PolyStyle>
    </Style>
    <Style id=\"SVstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d00ffff</color></PolyStyle>
    </Style>
    <Style id=\"FFstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d00ff00</color></PolyStyle>
    </Style>";
for ($i=0;$row=@pg_fetch_array($result,$i);$i++){
  echo "<Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Polygon Size:</i></font> ". $row["psize"] ." km^2
  <br /><font color=\"red\"><i>Status:</i></font> ". $vtec_status[$row["status"]] ."
   </p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <name>". $vtec_phenomena[$row["phenomena"]] ." ". $vtec_significance[$row["significance"]]  ."</name>\n";
  echo $row["kml"];
  echo "</Placemark>";
}
echo "</Document>
</kml>";

?>
