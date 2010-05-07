<?php
 include("../../../../config/settings.inc.php");
include("$rootpath/include/mlib.php");
include("$rootpath/include/network.php");
include("$rootpath/include/nexlib2.php");
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
 $pgconn = iemdb("access");
 $rad = isset($_GET['rad']) ? $_GET['rad'] : 'DMX';
 $tv = isset($_GET['rad']) ? strtoupper(substr($_GET['tv'],0,4)) : 'KCCI';
 $station = isset($_GET['station']) ? $_GET['station'] : '';
 $sortcol = isset($_GET['sortcol']) ? $_GET['sortcol'] : 'p15m';

$rs = pg_prepare($pgconn, "SELECT", "SELECT * from events WHERE network = $1
and valid > (now() - '15 minutes'::interval)");

$REFRESH = "<meta http-equiv=\"refresh\" content=\"60\">";
$TITLE = "IEM | SchoolNet | Where's it raining?";
$THISPAGE = "networks-schoolnet";
include("$rootpath/include/header.php");
?>

<h3 class="heading">SchoolNet 'Where is it raining?'</h3>

<form method="GET" action="raining.php" name="former">
<table>
<tr>
 <td>Select Network:</td>
 <td>Select NEXRAD source:</td>
 <td></td></tr>

<tr>
<td>
<select name="tv">
 <option value="KCCI" <?php if ($tv == 'KCCI') echo 'SELECTED'; ?>>KCCI-TV Des Moines
 <option value="KELO" <?php if ($tv == 'KELO') echo 'SELECTED'; ?>>KELO-TV Sioux Falls
 <option value="KIMT" <?php if ($tv == 'KIMT') echo 'SELECTED'; ?>>KIMT-TV Mason City
</select>
</td>
<td>
<select name="rad">
  <option value="ABR" <?php if ($rad == 'ABR') echo 'SELECTED'; ?>>[ARX] Aberdeen, SD
  <option value="ARX" <?php if ($rad == 'ARX') echo 'SELECTED'; ?>>[ARX] LaCrosse, WI
  <option value="DMX" <?php if ($rad == 'DMX') echo 'SELECTED'; ?>>[DMX] Des Moines, IA
  <option value="DMXA" <?php if ($rad == 'DMXA') echo 'SELECTED'; ?>>[DMX] Des Moines, IA (North)
  <option value="DMXB" <?php if ($rad == 'DMXB') echo 'SELECTED'; ?>>[DMX] Des Moines, IA (Central)
  <option value="DMXC" <?php if ($rad == 'DMXC') echo 'SELECTED'; ?>>[DMX] Des Moines, IA (South)
  <option value="DVN" <?php if ($rad == 'DVN') echo 'SELECTED'; ?>>[DVN] Davenport, IA
  <option value="EAX" <?php if ($rad == 'EAX') echo 'SELECTED'; ?>>[EAX] Pleasant Hill, MO
  <option value="FSD" <?php if ($rad == 'FSD') echo 'SELECTED'; ?>>[FSD] Sioux Falls, SD
  <option value="MPX" <?php if ($rad == 'MPX') echo 'SELECTED'; ?>>[MPX] Minneapolis, MN
  <option value="OAX" <?php if ($rad == 'OAX') echo 'SELECTED'; ?>>[OAX] Omaha, NE
  <option value="UDX" <?php if ($rad == 'UDX') echo 'SELECTED'; ?>>[UDX] Rapid City, SD
</select>
</td>
<td>
<input type="submit" value="Switch NEXRAD">
</td></tr></table>
</form>

<?php
dl($mapscript);
$nt = new NetworkTable($tv);
$stbl = $nt->table;

$iemdb = new IEMAccess();
$iemdata = $iemdb->getNetwork($tv);
$data = Array();
while (list($key, $iemob) = each($iemdata) ){
  $data[$key] = $iemob->db;
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

  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}



$map = ms_newMapObj("raining.map");
$map->set("width", 640);
$map->set("height", 480);

$pad = 1;
$lpad = 0.4;

$map->setProjection( $projs[substr($rad,0,3)] );
$map->setextent($extents[$rad][0],$extents[$rad][1],$extents[$rad][2],$extents[$rad][3] );
if (strlen($station) > 0)
{
  $a = $stbl[$station];
  $map->setextent($a["lon"] - 0.5, $a["lat"] - 0.5, $a["lon"] + 0.5, $a["lat"] + 0.5);
}


$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$dot = $map->getlayerbyname("dot");
$dot->set("status", MS_ON);
$dot->setProjection("init=epsg:4326");

$site = $map->getlayerbyname("site");
$site->set("status", MS_ON);
$site->setProjection("init=epsg:4326");

$radar = $map->getlayerbyname( substr($rad,0,3) );
$radar->set("status", MS_ON);
//$radar->setProjection($projs[substr($rad,0,3)]);

$st_cl = ms_newclassobj($stlayer);
//$st_cl->set("outlinecolor", $green);
$st_cl->set("status", MS_ON);

$img = $map->prepareImage();


$counties->draw($img);
$stlayer->draw( $img);
$radar->draw($img);

$precip = Array();

$now = time();
foreach($stbl as $key => $value){
   if ($key == "S03I4" || $key == "SDNI4" || $key == "SRUM5" || $key == "GETS2") continue;

   $pt = ms_newPointObj();
   $pt->setXY($stbl[$key]["lon"], $stbl[$key]["lat"], 0);
   /** Data is old */
   if ($now - $data[$key]["ts"] > 1800){
       $pt->draw($map, $site, $img, 0, "" );
   } else {
     if (floatval($data[$key]["tmpf"]) < 32.1) {
       $pt->draw($map, $site, $img, 2, "" );
     } else {
       $pt->draw($map, $site, $img, 1, "" );
     }
   }
   $pt->free();

   if (strlen($station) > 0)
   {
     $pt = ms_newPointObj();
     $pt->setXY($stbl[$key]["lon"], $stbl[$key]["lat"], 0);
     $pt->draw($map, $dot, $img, 1, $data[$key]["sname"] );
     $pt->free();
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
     $pt->free();
   }
}


  $ts = strftime("%d %b %I:%M %p");

$map->drawLabelCache($img);

$radTimes = Array();
$rad2 = $rad;
if ($rad == "DMXA" || $rad == "DMXB" ||$rad == "DMXC" ) { $rad2 = "DMX"; }
$radTS = filemtime("/home/ldm/data/gis/images/4326/$rad2/n0r_0.tif");
$r = date("m/d h:i a", $radTS);

mktitle($map, $img, " SNET 15min rain ending: ". $ts ." , NEXRAD valid: $r");
$map->drawLabelCache($img);

$url = $img->saveWebImage();

echo"<table><tr><td valign=\"TOP\">";

echo "<p><h3 class=\"subtitle\">Rainfall totals today.</h3><br>";

$u = sprintf("<a href=\"raining.php?rad=%s&tv=%s&sortcol=", $rad, $tv);

echo $u ."\">Zoom out</a>\n";
echo "<table border=1>
 <tr><th>${u}station\">SID</a></th><th>${u}sname\">Site</a></th><th>${u}p15m\">15min</a></th><th>${u}phour\">1hour</a></th><th>${u}pday\">Day</a></th></tr>";


function aSortBySecondIndex($multiArray, $secondIndex) {
        while (list($firstIndex, ) = each($multiArray))
             $indexMap[$firstIndex] = @$multiArray[$firstIndex][$secondIndex];
        arsort($indexMap);
        while (list($firstIndex, ) = each($indexMap))
                if (is_numeric($firstIndex))
                        $sortedArray[] = $multiArray[$firstIndex];
                else $sortedArray[$firstIndex] = $multiArray[$firstIndex];
        return $sortedArray;
}

$finalA = Array();
$finalA = aSortBySecondIndex($data, $sortcol);

$now = time();
foreach($finalA as $key => $value){
  $pDay = round($data[$key]["pday"], 2);
  if ( ($now - $data[$key]["ts"] < 1000) ){
    echo "<tr><th><a href=\"raining.php?sortcol=$sortcol&tv=$tv&rad=$rad&station=$key\">". $key ."</a></th><td>". $stbl[$key]["name"] ."</td>
     <td>". $data[$key]["p15m"] ."</td><td>". $data[$key]["phour"] ."</td><td>". $data[$key]["pday"] ."</td></tr>\n";
  }
}
echo "</table>\n";

echo "</td><td valign=\"top\">\n";

echo "<p><b>". $obcount ."</b> sites currently reporting precip.\n";
echo "<br>Map of <a href=\"$rooturl/sites/locate.php?network=KCCI\" target=\"_new\">KCCI sites</a> or <a href=\"$rooturl/sites/locate.php?network=KELO\" target=\"_new\">KELO sites</a> or <a href=\"$rooturl/sites/locate.php?network=KIMT\" target=\"_new\">KIMT sites</a> .\n";

echo "<p><img src=\"$url\" border=1>";
?>

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

<?php
echo "</td></tr></table>\n";

?></div>

<?php
include ("$rootpath/include/footer.php");

?>
