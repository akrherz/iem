<?php
/* Sucks to render a KML */
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
$connect = iemdb("postgis");

$year = get_int404("year", 2006);
$wfo = isset($_GET["wfo"]) ? substr(xssafe($_GET["wfo"]),0,4) : "MPX";
if (strlen($wfo) > 3){
    $wfo = substr($wfo, 1, 3);
}
$eventid = get_int404("eventid", 103);
$phenomena = isset($_GET["phenomena"]) ? substr(xssafe($_GET["phenomena"]),0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr(xssafe($_GET["significance"]),0,1) : "W";

/* Now we fetch warning and perhaps polygon */
$query2 = "SELECT l.*, ST_askml(l.geom) as kml
           from sbw_$year w, lsrs l
           WHERE w.wfo = '$wfo' and w.phenomena = '$phenomena' and 
           w.eventid = $eventid and w.significance = '$significance'
           and w.geom && l.geom and l.valid BETWEEN w.issue and w.expire
           and w.status = 'NEW'";

$result = pg_exec($connect, $query2);
$row = pg_fetch_array($result);

header('Content-disposition: attachment; filename=sbw_lsrs.kml');
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
    </Style>";
for ($i=0;$row=pg_fetch_assoc($result);$i++)
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
