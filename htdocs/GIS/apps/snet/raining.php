<?php
define("IEM_APPID", 159);
 include("../../../../config/settings.inc.php");
 include("../../../../include/myview.php");
 $t = new MyView();
 
include_once "../../../../include/iemmap.php";
require_once "../../../../include/mlib.php";
require_once "../../../../include/forms.php";
include("../../../../include/network.php");

$projs = Array("KCC" => "init=epsg:26915",
		"DMX" => "init=epsg:4326",
		"FSD" => "init=epsg:4326",
		"ARX" => "init=epsg:4326",
		"OAX" => "init=epsg:4326",
		"ABR" => "init=epsg:4326",
		"DVN" => "init=epsg:4326",
		"EAX" => "init=epsg:4326",
		"MPX" => "init=epsg:4326",
		"UDX" => "init=epsg:4326"
);

$extents = Array("KCCI" => Array(176500, 4450000, 710900, 4850000),
		"KCCIA" => Array(276500, 4650000, 610900, 4850000),
		"KCCIB" => Array(276500, 4550000, 610900, 4750000),
		"KCCIC" => Array(276500, 4450000, 610900, 4650000),
		"DMX" => Array(-96.72, 38.72, -90.72, 44.72),
		"DMXA" => Array(-95.0, 41.0, -92.0, 44.0),
		"DMXB" => Array(-95.0, 40.5, -92.0, 43),
		"DMXC" => Array(-95.0, 40, -92.0, 42.5),
		"ARX" => Array(-94.18, 40.82, -88.18, 46.82),
		"DVN" => Array(-93.57, 38.60, -87.57, 44.60),
		"OAX" => Array(-99.37, 38.32, -93.37, 44.32),
		"EAX" => Array(-97.25, 35.80, -91.25, 41.80),
		"MPX" => Array(-96.55, 41.83, -90.55, 47.83),
		"FSD" => Array(-99.72, 40.58, -93.72, 46.58),
		"ABR" => Array(-101.40, 42.45, -95.40, 48.45),
		"UDX" => Array(-105.82, 41.12, -99.82, 47.12)
);

$wfos = Array("DMX" => "Des Moines",
		"DVN" => "Davenport",
		"ARX" => "LaCrosse",
		"MPX" => "Minneapolis",
		"FSD" => "Sioux Falls",
		"OAX" => "Omaha",
		"EAX" => "Pleasant Hill",
		"ABR" => "Aberdeen",
		"UDX" => "Rapid City");

$pgconn = iemdb("access");
 $rad = isset($_GET['rad']) ? xssafe($_GET['rad']) : 'DMX';
 $tv = isset($_GET['rad']) ? strtoupper(substr($_GET['tv'],0,4)) : 'KCCI';
 $station = isset($_GET['station']) ? xssafe($_GET['station']) : '';
 $sortcol = isset($_GET['sortcol']) ? xssafe($_GET['sortcol']) : 'p15m';

$rs = pg_prepare($pgconn, "SELECT", "SELECT * from events WHERE network = $1
	and valid > (now() - '15 minutes'::interval)");

$t->refresh = "<meta http-equiv=\"refresh\" content=\"60\">";
$t->title = "SchoolNet - Where's it raining?";
$t->thispage = "networks-schoolnet";

$ar = Array("KCCI" => "KCCI-TV Des Moines",
	"KELO" => "KELO-TV Sioux Falls",
	"KIMT" => "KIMT-TV Mason City");
$tvselect = make_select("tv", $tv, $ar);

$ar = Array("ABR" => "[ABR] Aberdeen, SD",
  "ARX" => "[ARX] LaCrosse, WI",
  "DMX" => "[DMX] Des Moines, IA",
  "DMXA" => "[DMX] Des Moines, IA (North)",
  "DMXB" => "[DMX] Des Moines, IA (Central)",
  "DMXC" => "[DMX] Des Moines, IA (South)",
  "DVN" => "[DVN] Davenport, IA",
  "EAX" => "[EAX] Pleasant Hill, MO",
  "FSD" => "[FSD] Sioux Falls, SD",
  "MPX" => "[MPX] Minneapolis, MN",
  "OAX" => "[OAX] Omaha, NE",
  "UDX" => "[UDX] Rapid City, SD");
$radselect = make_select("rad", $rad, $ar);

$nt = new NetworkTable($tv);
$stbl = $nt->table;

$jdata = file_get_contents("http://iem.local/api/1/currents.json?network=$tv");
$jobj = json_decode($jdata, $assoc=TRUE);

$data = Array();
while (list($bogus, $iemob) = each($jobj["data"]) ){
    $key = $iemob["station"];
    $data[$key] = $iemob;
	$data[$key]["p15m"] = 0;
}

$rs = pg_execute($pgconn, "SELECT", Array($tv));
for($i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
	$data[ $row["station"] ]["p15m"] = $row["magnitude"];
}

function mktitle($map, $imgObj, $titlet) {
	$layer = $map->getLayerByName("credits");

	// point feature with text for location
	$point = ms_newpointobj();
	$point->setXY(0, 470);

	$point->draw($map, $layer, $imgObj, 0,
			$titlet);
}



$map = ms_newMapObj("../../../../data/gis/base4326.map");
$map->setsize(640,480);

$pad = 1;
$lpad = 0.4;
$map->setProjection( $projs[substr($rad,0,3)] );
$map->setextent($extents[$rad][0],$extents[$rad][1],$extents[$rad][2],$extents[$rad][3] );
if (strlen($station) > 0)
{
	$a = $stbl[$station];
	$map->setextent($a["lon"] - 0.5, $a["lat"] - 0.5, $a["lon"] + 0.5, $a["lat"] + 0.5);
}

$counties = $map->getlayerbyname("uscounties");
$counties->set("status", MS_ON);

$namer = $map->getLayerByName("namerica");
$namer->set("status", MS_ON);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$dot = $map->getlayerbyname("pointonly");
$dot->set("status", MS_ON);
$dot->setProjection("init=epsg:4326");

$site = $map->getlayerbyname("site");
$site->set("status", MS_ON);

$radar = $map->getlayerbyname( substr($rad,0,3) );
$radar->set("status", MS_ON);
//$radar->setProjection($projs[substr($rad,0,3)]);

$st_cl = ms_newclassobj($stlayer);
//$st_cl->set("outlinecolor", $green);
$st_cl->set("status", MS_ON);

$img = $map->prepareImage();

$namer->draw($img);
$counties->draw($img);
$stlayer->draw( $img);
$radar->draw($img);

$precip = Array();

$now = time();
foreach($stbl as $key => $value){
	if (! array_key_exists($key, $data)){ continue; }
	
	$pt = ms_newPointObj();
	$pt->setXY($stbl[$key]["lon"], $stbl[$key]["lat"], 0);
	/** Data is old */
	if ($now - strtotime($data[$key]["local_valid"]) > 1800){
		$pt->draw($map, $site, $img, 0);
	} else {
		if (floatval($data[$key]["tmpf"]) < 32.1) {
			$pt->draw($map, $site, $img, 2);
		} else {
			$pt->draw($map, $site, $img, 1 );
		}
	}

	if (strlen($station) > 0)
	{
		$pt = ms_newPointObj();
		$pt->setXY($stbl[$key]["lon"], $stbl[$key]["lat"], 0);
		$pt->draw($map, $dot, $img, 1, $data[$key]["sname"] );
		 
	}
}


$obcount = 0;
$now = time();
reset($data);
foreach($data as $key => $value){
	if ($data[$key]['p15m'] > 0) {
		$obcount += 1;
		$pt = ms_newPointObj();
		$pt->setXY($stbl[$key]["lon"], $stbl[$key]["lat"], 0);
		$pt->draw($map, $dot, $img, 0, $key ." (". $data[$key]['p15m'] .")" );
		 
	}
}


$ts = strftime("%d %b %I:%M %p");

$map->drawLabelCache($img);

$radTimes = Array();
$rad2 = $rad;
if ($rad == "DMXA" || $rad == "DMXB" ||$rad == "DMXC" ) { $rad2 = "DMX"; }
$radTS = filemtime("/home/ldm/data/gis/images/4326/ridge/$rad2/N0Q_0.png");
$r = date("m/d h:i a", $radTS);

$map->drawLabelCache($img);
iemmap_title($map, $img, "SNET 15min rain ending: ". $ts , "NEXRAD valid: $r");

$url = $img->saveWebImage();

$u = sprintf("<a href=\"raining.php?rad=%s&tv=%s&sortcol=", $rad, $tv);

$finalA = Array();
$finalA = aSortBySecondIndex($data, $sortcol);

$now = time();
$table = "";
foreach($finalA as $key => $value){
	$pDay = round($data[$key]["pday"], 2);
	if ( ($now - strtotime($data[$key]["local_valid"]) < 1000) ){
		$table .= "<tr><th><a href=\"raining.php?sortcol=$sortcol&tv=$tv&rad=$rad&station=$key\">". $key ."</a></th><td>". $stbl[$key]["name"] ."</td>
     <td>". $data[$key]["p15m"] ."</td><td>". $data[$key]["phour"] ."</td><td>". $data[$key]["pday"] ."</td></tr>\n";
	}
	}

$t->content = <<<EOF
<h3>SchoolNet 'Where is it raining?'</h3>

<form method="GET" action="raining.php" name="former">
<table>
<tr>
 <td>Select Network:</td>
 <td>Select NEXRAD source:</td>
 <td></td></tr>

<tr>
<td>{$tvselect}
</td>
<td>{$radselect}
</td>
<td>
<input type="submit" value="Switch NEXRAD">
</td></tr></table>
</form>

<table><tr><td valign="TOP">
<p><h3>Rainfall totals today.</h3><br>

$u">Zoom out</a>
<table border=1>
 <tr><th>${u}station">SID</a></th><th>${u}sname">Site</a></th>
 <th>${u}p15m">15min</a></th><th>${u}phour">1hour</a></th><th>${u}pday">Day</a></th>
 </tr>


{$table}
</table>

</td><td valign="top">

<p><b>{$obcount}</b> sites currently reporting precip.
<br>Map of <a href="/sites/locate.php?network=KCCI" target="_new">KCCI sites</a> 
or <a href="/sites/locate.php?network=KELO" target="_new">KELO sites</a> or 
<a href="/sites/locate.php?network=KIMT" target="_new">KIMT sites</a>
<p><img src="$url" border=1>

<p>SchoolNet sites use a non-heated tipping bucket to measure rainfall,
which means no rainfall is recorded when the temperature is below freezing.</p>

<h3 class="subtitle">Map Legend:</h3>
<ul>
 <li>Red X's are sites that are currently offline.</li>
 <li>Yellow triangles are sites currently below freezing and not reporting rainfall.</li>
 <li>White dots are sites above freezing, but not reporting precip.</li>
 <li>Black dots are sites reporting precip.</li>
</ul>

<p>This application shows you visually where it should be raining (NEXRAD) and which
schoolNet sites are actually reporting rainfall.  If a dot is black, the site has received 
<b>measurable</b> (> 0.01) rainfall in the previous 15 minutes.<br>
This page will automatically reload every 3 minutes.</p>
</td></tr></table>
</div>
EOF;
$t->render('single.phtml');
?>