<?php
/* Generate a plot based on a request from gsplot.phtml, no more tmp 
 * files please
 */
require_once "../../../../config/settings.inc.php";
require_once "../../../../include/database.inc.php";
$coopdb = iemdb("coop");
require_once "../../../../include/forms.php";
require_once "../../../../include/network.php";
/** Need to use external date lib 
 * http://php.weblogs.com/adodb_date_time_library
 */
require_once "../../../../include/adodb-time.inc.php";

$var = isset($_GET["var"]) ? xssafe($_GET["var"]) : "gdd50";
$year = get_int404("year", date("Y"));
$smonth = get_int404("smonth", 5);
$sday = get_int404("sday", 1);
$emonth = get_int404("emonth", date("m"));
$eday = get_int404("eday", date("d"));
$network = isset($_REQUEST["network"]) ? xssafe($_REQUEST["network"]) : "IACLIMATE";

$nt = new NetworkTable($network);
$cities = $nt->table;


$sts = adodb_mktime(0, 0, 0, $smonth, $sday, $year);
$ets = adodb_mktime(0, 0, 0, $emonth, $eday, $year);

if ($sts > $ets) {
    $sts = $ets - 86400;
}


function mktitlelocal($map, $imgObj, $titlet)
{

    $layer = $map->getLayerByName("credits");

    // point feature with text for location
    $point = new pointobj();
    $point->setXY(0, 10);
    $point->draw($map, $layer, $imgObj, 0, $titlet);
}

function plotNoData($map, $img)
{
    $layer = $map->getLayerByName("credits");

    $point = new pointobj();
    $point->setXY(100, 200);
    $point->draw(
        $map,
        $layer,
        $img,
        1,
        "  No data found for this date! "
    );
}

$varDef = array(
    "gdd32" => "Growing Degree Days (base=32)",
    "gdd41" => "Growing Degree Days (base=41)",
    "gdd46" => "Growing Degree Days (base=46)",
    "gdd48" => "Growing Degree Days (base=48)",
    "gdd50" => "Growing Degree Days (base=50)",
    "gdd51" => "Growing Degree Days (base=51)",
    "gdd52" => "Growing Degree Days (base=52)",
    "cdd65" => "Cooling Degree Days (base=65)",
    "hdd65" => "Heating Degree Days (base=65)",
    "et" => "Potential Evapotranspiration",
    "prec" => "Precipitation",
    "sgdd50" => "Soil Growing Degree Days (base=50)",
    "sdd86" => "Stress Degree Days (base=86)",
    "mintemp" => "Minimum Temperature [F]",
    "maxtemp" => "Maximum Temperature [F]",
);

$rnd = array(
    "gdd32" => 0,
    "gdd41" => 0,
    "gdd46" => 0,
    "gdd48" => 0,
    "gdd50" => 0,
    "gdd51" => 0,
    "gdd52" => 0,
    "et" => 2,
    "prec" => 2,
    "sgdd50" => 0,
    "sdd86" => 0,
    "cdd65" => 0,
    "hdd65" => 0,
    "mintemp" => 0,
    "maxtemp" => 0
);
$myStations = $cities;
$height = 480;
$width = 640;

$proj = "init=epsg:26915";

$map = new MapObj("../../../../data/gis/base26915.map");
$map->setProjection($proj);

$state = substr($network, 0, 2);
$dbconn = iemdb("postgis");
$rs = pg_query($dbconn, "SELECT ST_xmin(g), ST_xmax(g), ST_ymin(g), ST_ymax(g) from (
        select ST_Extent(ST_Transform(the_geom,26915)) as g from states 
        where state_abbr = '${state}'
        ) as foo");
$row = pg_fetch_array($rs, 0);
$buf = 35000; // 35km
$xsz = $row[1] - $row[0];
$ysz = $row[3] - $row[2];
if (($ysz + 100000) > $xsz) {
    $map->setsize(768, 1024);
} else {
    $map->setsize(1024, 768);
}
$map->setextent(
    $row[0] - $buf,
    $row[2] - $buf,
    $row[1] + $buf,
    $row[3] + $buf
);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$bar640t = $map->getlayerbyname("bar640t");
$bar640t->set("status", MS_ON);

$snet = $map->getlayerbyname("snet");
$snet->set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->set("status", 1);

$ponly = $map->getlayerbyname("pointonly");
$ponly->set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($img);
$states->draw($img);
$iards->draw($img);
$bar640t->draw($img);

$rs = pg_prepare($coopdb, "SELECT", "SELECT station, 
    sum(precip) as s_prec,
  sum(gddxx(32, 86, high, low)) as s_gdd32,
    sum(gddxx(41, 86, high, low)) as s_gdd41,
    sum(gddxx(46, 86, high, low)) as s_gdd46,
    sum(gddxx(48, 86, high, low)) as s_gdd48,
    sum(gddxx(50, 86, high, low)) as s_gdd50,
  sum(gddxx(51, 86, high, low)) as s_gdd51,
    sum(gddxx(52, 86, high, low)) as s_gdd52,
  sum(cdd(high, low, 65)) as s_cdd65,
  sum(hdd(high, low, 65)) as s_hdd65,
    sum(sdd86(high,low)) as s_sdd86, min(low) as s_mintemp,
    max(high) as s_maxtemp from alldata 
    WHERE day >= $1 and day <= $2
  and substr(station, 3, 4) != '0000' and substr(station, 3, 1) != 'C'
  GROUP by station 
    ORDER by station ASC");
$rs = pg_execute($coopdb, "SELECT", array(
    adodb_date("Y-m-d", $sts),
    adodb_date("Y-m-d", $ets)
));

for ($i = 0; $row = pg_fetch_array($rs); $i++) {

    $ukey = $row["station"];
    if (!isset($cities[$ukey])) continue;
    // Red Dot...  
    $pt = new PointObj();
    $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
    $pt->draw($map, $ponly, $img, 0);

    // City Name
    $pt = new PointObj();
    $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
    $pt->draw($map, $snet, $img, 3, substr($ukey, 2, 4));

    // Value UL
    $pt = new PointObj();
    $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
    $pt->draw(
        $map,
        $snet,
        $img,
        0,
        round($row["s_" . $var], $rnd[$var])
    );
}
if ($i == 0)
    plotNoData($map, $img);

$title = sprintf(
    "%s (%s through %s)",
    $varDef[$var],
    adodb_date("Y-m-d", $sts),
    adodb_date("Y-m-d", $ets)
);

mktitlelocal($map, $img, $title);
$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
