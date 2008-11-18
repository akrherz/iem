<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$conn = iemdb("postgis");

$tbl = "roads_current";
if (isset($_GET["test"])){ $tbl = "roads_current_test"; }

$sql = "SELECT askml(simple_geom) as kml,
      * from $tbl r, roads_base b, roads_conditions c WHERE
  r.segid = b.segid and r.cond_code = c.code";

$rs = pg_query($conn, $sql);

header("Content-Type:", "application/vnd.google-earth.kml+xml");
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
<Style id=\"code0\">
  <LineStyle><width>3</width><color>ffffffff</color></LineStyle>
</Style>
<Style id=\"code1\">
  <LineStyle><width>3</width><color>ff00CC00</color></LineStyle>
</Style>
<Style id=\"code3\">
  <LineStyle><width>3</width><color>fff0f000</color></LineStyle>
</Style>
<Style id=\"code7\">
  <LineStyle><width>3</width><color>fff0f000</color></LineStyle>
</Style>
<Style id=\"code11\">
  <LineStyle><width>3</width><color>fff0f000</color></LineStyle>
</Style>
<Style id=\"code15\">
  <LineStyle><width>3</width><color>ffffc5c5</color></LineStyle>
</Style>
<Style id=\"code19\">
  <LineStyle><width>3</width><color>fffe3299</color></LineStyle>
</Style>
<Style id=\"code23\">
  <LineStyle><width>3</width><color>ffb500b5</color></LineStyle>
</Style>
<Style id=\"code27\">
  <LineStyle><width>3</width><color>ffffc5c5</color></LineStyle>
</Style>
<Style id=\"code31\">
  <LineStyle><width>3</width><color>fffe3399</color></LineStyle>
</Style>
<Style id=\"code35\">
  <LineStyle><width>3</width><color>ffb500b5</color></LineStyle>
</Style>
<Style id=\"code39\">
  <LineStyle><width>3</width><color>ffdcdcdc</color></LineStyle>
</Style>
<Style id=\"code43\">
  <LineStyle><width>3</width><color>ff0099fe</color></LineStyle>
</Style>
<Style id=\"code47\">
  <LineStyle><width>3</width><color>ff00009E</color></LineStyle>
</Style>
<Style id=\"code51\">
  <LineStyle><width>3</width><color>ffe85f01</color></LineStyle>
</Style>
<Style id=\"code56\">
  <LineStyle><width>3</width><color>ffffc5c5</color></LineStyle>
</Style>
<Style id=\"code60\">
  <LineStyle><width>3</width><color>fffe3399</color></LineStyle>
</Style>
<Style id=\"code86\">
  <LineStyle><width>5</width><color>ffff0000</color></LineStyle>
</Style>
";

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $minor = $row["minor"];
  $major = $row["major"];


  echo "<Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Road:</i> $major :: $minor</font>
  <br /><font color=\"red\"><i>Status:</i> ". $row["raw"] ."</font> 
   </p>
        ]]>
    </description>
    <styleUrl>#code".$row["cond_code"] ."</styleUrl>
    <name>$major $minor</name>\n";
  echo $row["kml"];
  echo "</Placemark>";
}
echo "</Document>
</kml>";


?>
