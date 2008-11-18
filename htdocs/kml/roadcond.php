<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$conn = iemdb("postgis");

$sql = "SELECT askml(simple_geom) as kml,
      * from roads_current r, roads_base b, roads_conditions c WHERE
  r.segid = b.segid and r.cond_code = c.code";

$rs = pg_query($conn, $sql);

header("Content-Type:", "application/vnd.google-earth.kml+xml");
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
    <Style id=\"iemstyle\">
      <LineStyle>
        <width>3</width>
        <color>ffffffff</color>
      </LineStyle>
    </Style>";

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  echo "<Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Polygon Size:</i></font>
  <br /><font color=\"red\"><i>Status:</i></font> 
   </p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <name>Test</name>\n";
  echo $row["kml"];
  echo "</Placemark>";
}
echo "</Document>
</kml>";


?>
