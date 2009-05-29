<?php
/* Sucks to render a KML */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");
include("$rootpath/include/lsrs.php");
$connect = iemdb("postgis");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";

/* Now we fetch warning and perhaps polygon */
$query2 = "SELECT l.*, askml(l.geom) as kml
           from warnings_$year w, lsrs_$year l
           WHERE w.wfo = '$wfo' and w.phenomena = '$phenomena' and 
           w.eventid = $eventid and w.significance = '$significance'
           and w.geom && l.geom and l.valid BETWEEN w.issue and w.expire
           and w.gtype = 'P'";

$result = pg_exec($connect, $query2);
$row = @pg_fetch_array($result, 0);

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
    </Style>";
for ($i=0;$row=@pg_fetch_array($result,$i);$i++)
{
  $ts = strtotime( $row["valid"] );
  echo "<Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Location:</i></font> ". $row["city"] ." ". $row["county"] ." ". $row["state"] ."
  <br /><font color=\"red\"><i>Time:</i></font> ". gmdate('d M Y H:i', $ts) ." GMT 
  <br /><font color=\"red\"><i>Source:</i></font> ". $row["source"] ." 
  <br /><font color=\"red\"><i>Remark:</i></font> ". $row["remark"] ."
   </p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <name>". $row["magnitude"] ." ". $row["typetext"] ."</name>\n";
echo $row["kml"];
echo "</Placemark>";
}
echo "
 </Document>
</kml>";

?>
