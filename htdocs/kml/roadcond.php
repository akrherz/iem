<?php
/*
 * Generate KML of the road conditions
 */
require_once "../../config/settings.inc.php";
$linewidth = isset($_REQUEST['linewidth']) ? intval($_REQUEST["linewidth"]): 3;
$maxtype = isset($_GET["maxtype"]) ? intval($_GET["maxtype"]): 3;

header("Content-Type: application/vnd.google-earth.kml+xml");

if (! isset($_GET["cachebust"])){
// Try to get it from memcached
$memcache = new Memcached();
$memcache->addServer('iem-memcached', 11211);
$val = $memcache->get("/kml/roadcond.php|$linewidth|$maxtype");
if ($val){
	die($val);
}
}
// Need to buffer the output so that we can save it to memcached later
ob_start();

require_once "../../include/database.inc.php";
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

$sql = "SELECT ST_askml(ST_Simplify(simple_geom, 100)) as kml, ".
       "* from $tbl r, roads_base b, roads_conditions c WHERE ".
       "r.segid = b.segid and r.cond_code = c.code and b.type <= $maxtype";

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
$stext = "";
foreach($styles as $key => $value){
	$stext .= sprintf("<Style id=\"style%s\"><LineStyle><color>%s</color><width>${linewidth}</width></LineStyle></Style>\n",
			$key, $value);
}

$uri = urlencode($valid);
/*
<ScreenOverlay id="legend_bar">
   <visibility>1</visibility>
   <Icon>
       <href>https://mesonet.agron.iastate.edu/kml/timestamp.php?label=Roads:%20{$uri}</href>
   </Icon>
   <overlayXY x=".3" y="0.99" xunits="fraction" yunits="fraction"/>
   <screenXY x=".3" y="0.99" xunits="fraction" yunits="fraction"/>
   <size x="0" y="0" xunits="pixels" yunits="pixels"/>
</ScreenOverlay>
 */
echo <<<EOF
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
 <name>Iowa Winter Road Conditions delivered by the IEM</name>
{$stext}
<Folder>
EOF;

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
	if ($row["kml"] ==  "") continue;
  $minor = $row["minor"];
  $major = $row["major"];
	$ccode = intval($row["cond_code"]);
	if (! array_key_exists($ccode, $styles)){
		$ccode = 0;
	}

  echo "<Placemark><name>$major $minor</name>
    <description><![CDATA[
  <p><font color=\"red\"><i>Road:</i> $major :: $minor</font>
  <br /><font color=\"red\"><i>Status:</i> ". $row["raw"] ."</font> 
   </p>
        ]]></description><styleUrl>#style{$ccode}</styleUrl>
";
  echo $row["kml"];
  echo "</Placemark>\n";
}
echo <<<EOF
</Folder>
</Document>
</kml>
EOF;

@$memcache->set("/kml/roadcond.php|$linewidth|$maxtype", ob_get_contents(), 300);
ob_end_flush();
?>
