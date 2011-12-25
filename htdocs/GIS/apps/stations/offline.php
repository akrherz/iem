<?php
include("../../../../config/settings.inc.php");
include_once "$rootpath/include/iemmap.php";
include("$rootpath/include/mlib.php");
include("$rootpath/include/network.php");
include("$rootpath/include/iemaccess.php");
$iemaccess = new IEMAccess();

$network = isset($_GET['network']) ? $_GET['network'] : die('No Network Set.');
$nt = new NetworkTable($network);
$cities = $nt->table;

$myStations = Array();

$lats = Array();
$lons = Array();
$height = 350;
$width = 450;

$rs = pg_prepare($iemaccess->dbconn, "query",
      "SELECT * from offline WHERE network = $1");

$rs = pg_execute($iemaccess->dbconn, "query", array($network));


for ($i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $station = $row["station"];
  if (! isset($cities[$station])) continue;
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


$map = ms_newMapObj("$rootpath/data/gis/base4326.map");

$pad = 1;
$lpad = 0.8;

//$map->setextent(-83760, -2587, 478797, 433934);
$map->setextent($lon0 - $lpad, $lat0 - $pad, $lon1 + $lpad, $lat1 + $pad);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", MS_ON);

$counties = $map->getlayerbyname("uscounties");
$counties->set("status", MS_ON);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$dot = $map->getlayerbyname("pointonly");
$dot->set("status", MS_ON);

$st_cl = ms_newclassobj($stlayer);
//$st_cl->set("outlinecolor", $green);
$st_cl->set("status", MS_ON);

$img = $map->prepareImage();
$namer->draw($img);
$counties->draw($img);
$stlayer->draw( $img);

$now = time();
foreach($myStations as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 0, $cities[$value]['name'] );

}

  $ts = strftime("%d %b %I%p");

$map->drawLabelCache($img);
iemmap_title($map, $img, "$network Sites Offline $ts");

$url = $img->saveWebImage();

//   $white, $Font, "Sites Offline ". $ts );
?>

<?php include("$rootpath/include/header.php"); ?>

<?php echo "<img src=\"$url\">"; ?>

<?php include("$rootpath/include/footer.php"); ?>
