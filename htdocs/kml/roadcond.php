<?php
/*
 * Generate KML of the road conditions
 */
include("../../config/settings.inc.php");
$linewidth = isset($_REQUEST['linewidth']) ? intval($_REQUEST["linewidth"]): 3;

header("Content-Type: application/vnd.google-earth.kml+xml");

// Try to get it from memcached
$memcache = new Memcache;
$memcache->connect('iem-memcached', 11211);
$val = $memcache->get("/kml/roadcond.php|$linewidth");
if ($val){
	die($val);
}
// Need to buffer the output so that we can save it to memcached later
ob_start();

include("../../include/database.inc.php");
$conn = iemdb("postgis");

$linewidth2 = $linewidth + 2;
$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($conn, $sql);
$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);
$ts = strtotime($valid);
$valid = strftime("%I:%M %p on %d %b %Y", $ts);


$tbl = "roads_current";
if (isset($_GET["test"])){ $tbl = "roads_current_test"; }

$sql = "SELECT ST_askml(ST_Simplify(simple_geom,100)) as kml,
      * from $tbl r, roads_base b, roads_conditions c WHERE
  r.segid = b.segid and r.cond_code = c.code";

$rs = pg_query($conn, $sql);

// holy cow, colors are ABGR ! :(

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://www.opengis.net/kml/2.2\">
 <Document>

<Style id=\"code0\">
  <LineStyle><color>ff000000</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code1\">
  <LineStyle><color>ff00CC00</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code3\">
  <LineStyle><color>ff00f0f0</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code7\">
  <LineStyle><color>ff00f0f0</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code11\">
  <LineStyle><color>ff00f0f0</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code15\">
  <LineStyle><color>ffc5c5ff</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code19\">
  <LineStyle><color>ff9932fe</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code23\">
  <LineStyle><color>ffb500b5</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code27\">
  <LineStyle><color>ffc5c5ff</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code31\">
  <LineStyle><color>ff9933fe</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code35\">
  <LineStyle><color>ffb500b5</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code39\">
  <LineStyle><color>ffffffdc</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code43\">
  <LineStyle><color>fffe9900</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code47\">
  <LineStyle><color>ff9E0000</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code51\">
  <LineStyle><color>ff015ffe</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code56\">
  <LineStyle><color>ffc5c5ff</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code60\">
  <LineStyle><color>ff9933fe</color><width>${linewidth}</width></LineStyle>
</Style>
<Style id=\"code86\">
  <LineStyle><color>ff0000ff</color><width>${linewidth}</width></LineStyle>
</Style>
 <ScreenOverlay id=\"legend_bar\">
   <visibility>1</visibility>
   <Icon>
       <href>http://mesonet.agron.iastate.edu/kml/timestamp.php?label=Roads:%20". urlencode($valid) ."</href>
   </Icon>
   <overlayXY x=\".3\" y=\"0.99\" xunits=\"fraction\" yunits=\"fraction\"/>
   <screenXY x=\".3\" y=\"0.99\" xunits=\"fraction\" yunits=\"fraction\"/>
   <size x=\"0\" y=\"0\" xunits=\"pixels\" yunits=\"pixels\"/>
  </ScreenOverlay>
";

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $minor = $row["minor"];
  $major = $row["major"];


  echo "<Placemark>
<name>$major $minor</name>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Road:</i> $major :: $minor</font>
  <br /><font color=\"red\"><i>Status:</i> ". $row["raw"] ."</font> 
   </p>
        ]]>
    </description>
    <styleUrl>#code".$row["cond_code"] ."</styleUrl>";
  echo $row["kml"];
  echo "</Placemark>";
}
echo "</Document>
</kml>";

$memcache->set("/kml/roadcond.php|$linewidth", ob_get_contents(), false, 300);
ob_end_flush();
?>