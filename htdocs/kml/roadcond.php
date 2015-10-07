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
$styles = Array(
		0 => "ff000000",
		1 => "ff00CC00",
		3 => "ff00f0f0",
		7 => "ff00f0f0",
		11 => "ff00f0f0",
		15 => "ffc5c5ff",
		19 => "ff9932fe",
		23 => "ffb500b5",
		27 => "ffc5c5ff",
		31 => "ff9933fe",
		35 => "ffb500b5",
		39 => "ffffffdc",
		43 => "fffe9900",
		47 => "ff9E0000",
		51 => "ff015ffe",
		56 => "ffc5c5ff",
		60 => "ff9933fe",
		76 => "ff000000",
		86 => "ff0000ff",
		);

$uri = urlencode($valid);
echo <<<EOF
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<ScreenOverlay id="legend_bar">
   <visibility>1</visibility>
   <Icon>
       <href>http://mesonet.agron.iastate.edu/kml/timestamp.php?label=Roads:%20{$uri}</href>
   </Icon>
   <overlayXY x=".3" y="0.99" xunits="fraction" yunits="fraction"/>
   <screenXY x=".3" y="0.99" xunits="fraction" yunits="fraction"/>
   <size x="0" y="0" xunits="pixels" yunits="pixels"/>
</ScreenOverlay>
EOF;

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $minor = $row["minor"];
  $major = $row["major"];
	$c = "ff000000";
	if (array_key_exists($row["cond_code"], $styles)){
		$c = $styles[$row["cond_code"]];
	}

  echo "<Placemark>
<name>$major $minor</name>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Road:</i> $major :: $minor</font>
  <br /><font color=\"red\"><i>Status:</i> ". $row["raw"] ."</font> 
   </p>
        ]]>
    </description>
<Style><LineStyle><color>{$c}</color><width>${linewidth}</width></LineStyle></Style>
";
  echo $row["kml"];
  echo "</Placemark>";
}
echo "</Document>
</kml>";

@$memcache->set("/kml/roadcond.php|$linewidth", ob_get_contents(), false, 300);
ob_end_flush();
?>