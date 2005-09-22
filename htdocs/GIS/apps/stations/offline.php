<?php
dl("php_mapscript_442.so");
include('../../../include/mlib.php');
include('/mesonet/php/include/all_locs.php');
include('/mesonet/www/html/include/iemaccess.php');
$iemaccess = new IEMAccess();

$network = isset($_GET['network']) ? $_GET['network'] : die('No Network Set.');

$myStations = Array();

$lats = Array();
$lons = Array();
$height = 350;
$width = 450;

$rs = pg_query($iemaccess->dbconn, "SELECT * from offline WHERE network = '$network'");

for ($i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $station = $row["station"];
  $lats[$station] = $cities[$station]["lat"];
  $lons[$station] = $cities[$station]["lon"];
  $myStations[] = $station;
}

if (sizeof($myStations) == 0)
{

  die("All Sites online!");
}

$lat0 = min($lats);
$lat1 = max($lats);
$lon0 = min($lons);
$lon1 = max($lons);


$map = ms_newMapObj("offline.map");

$pad = 1;
$lpad = 0.8;

//$map->setextent(-83760, -2587, 478797, 433934);
$map->setextent($lon0 - $lpad, $lat0 - $pad, $lon1 + $lpad, $lat1 + $pad);


$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$dot = $map->getlayerbyname("dot");
$dot->set("status", MS_ON);

$st_cl = ms_newclassobj($stlayer);
//$st_cl->set("outlinecolor", $green);
$st_cl->set("status", MS_ON);

$img = $map->prepareImage();

$counties->draw($img);
$stlayer->draw( $img);

$now = time();
foreach($myStations as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 0, $cities[$value]['city'] );
   $pt->free();
}

  $ts = strftime("%d %b %I%p");

$map->drawLabelCache($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

//   $white, $Font, "Sites Offline ". $ts );
?>

<?php include("/mesonet/php/include/header.php"); ?>

<?php echo "<img src=\"$url\">"; ?>

<?php include("/mesonet/php/include/footer.php"); ?>
