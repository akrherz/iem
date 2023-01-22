<?php
require_once "/usr/lib64/php/modules/mapscript.php";

require_once "../../../../config/settings.inc.php";
define("IEM_APPID", 52);
require_once "../../../../include/myview.php";
$t = new MyView();
$t->title = "NWS COOP Plotting";

require_once "../../../../include/database.inc.php";
require_once "../../../../include/iemmap.php";
require_once "../../../../include/network.php";
require_once "../../../../include/mlib.php";
require_once "../../../../include/forms.php";
require_once "../rview/lib.php";

$coopdb = iemdb("coop");
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;

$plot = isset($_GET["plot"]) ? xssafe($_GET["plot"]) : "high";
$area = isset($_GET["area"]) ? xssafe($_GET["area"]) : "all";
$month = isset($_GET["month"]) ? intval($_GET["month"]) : date("m");
$day = isset($_GET["day"]) ? intval($_GET["day"]) : date("d");

$height = 350;
$width = 350;

$map = new mapObj("../../../../data/gis/base4326.map");
$map->setProjection("init=epsg:26915");

$lx =  200000;
$ux =  710000;
$ly = 4400000;
$uy = 4900000;
$dx = $ux - $lx;
$dy = $uy - $ly;

$ex = array(
    "all" => array($lx,          $ly,           $ux,           $uy),
    "ne" => array($lx + ($dx / 2), $ly + ($dy / 2), $ux,           $uy),
    "se" => array($lx + ($dx / 2), $ly,           $ux, $uy - ($dy / 2)),
    "sw" => array($lx,           $ly,           $ux - ($dx / 2), $uy - ($dy / 2)),
    "nw" => array($lx,           $ly + ($dy / 2), $ux - ($dx / 2), $uy)
);


$map->setextent($ex[$area][0], $ex[$area][1], $ex[$area][2], $ex[$area][3]);

$namer = $map->getLayerByName("namerica");
$namer->__set("status", MS_ON);

$counties = $map->getLayerByName("uscounties");
$counties->__set("status", MS_ON);

$stlayer = $map->getLayerByName("states");
$stlayer->__set("status", 1);

$dot = $map->getLayerByName("pointonly");
$dot->__set("status", MS_ON);

$datal = new layerObj($map);
$datal->__set("name", "q");
$datal->__set("status", MS_ON);
$datal->__set("type", MS_LAYER_POINT);
$datal->setProjection("init=epsg:4326");

$datalc0 = new classObj($datal);
$datalc0->addLabel(new labelObj());
$datalc0->getLabel(0)->color->setrgb(255, 255, 0);
$datalc0->getLabel(0)->__set("font", "liberation");
$datalc0->getLabel(0)->__set("size", 12);
$datalc0->getLabel(0)->__set("force", MS_TRUE);
$datalc0->getLabel(0)->__set("partials", MS_TRUE);
//$datalc0->getLabel(0)->__set("antialias", MS_TRUE);
$datalc0->getLabel(0)->__set("position", MS_UR);
$datalc0->getLabel(0)->__set("angle", 0);
$datalc0->getLabel(0)->__set("wrap", 0x57);

$datalc0s0 = new styleObj($datalc0);
$datalc0s0->color->setrgb(0, 0, 0);
$datalc0s0->__set("symbolname", "circle");
$datalc0s0->__set("size", 3);

$datalc1 = new classObj($datal, $datalc0);
$datalc1->setExpression("([yrs] < 80)");
$datalc1s0 = new styleObj($datalc1);
$datalc1s0->color->setrgb(255, 0, 0);
$datalc1s0->__set("symbolname", "circle");
$datalc1s0->__set("size", 3);

$img = $map->prepareImage();

$tpos = array(
    "all" => array(-95.4, 40.2),
    "ne" => array(-92.9, 43.7),
    "se" => array(-92.9, 40.3),
    "sw" => array(-96.4, 40.4),
    "nw" => array(-96.7, 43.65)
);

$ts = mktime(0, 0, 0, $month, $day, 2000);
$plotDate = date('M d', $ts);

$var = array(
    "max_precip" => "Record Daily Precip [in]",
    "precip" => "Average Precipitation [in]",
    "low" => "Average Low Temp [F]",
    "max_low" => "Record Max Low Temp [F]",
    "max_high" => "Record Max High Temp [F]",
    "min_low" => "Record Min Low Temp [F]",
    "min_high" => "Record Min High Temp [F]",
    "high" => "Average High Temp [F]"
);

$dbdate = "2000-" . $month . "-" . $day;

if (strcmp($area, 'all') != 0) {

    $dbarray = array(
        "high" => "round(high::numeric, 0)::int",
        "low" => "round(low::numeric, 0)::int",
        "max_low" => "round(max_low::numeric, 0)::int ||'W'|| max_low_yr ",
        "max_high" => "round(max_high::numeric, 0)::int ||'W'|| max_high_yr ",
        "min_high" => "round(min_high::numeric, 0)::int ||'W'|| min_high_yr ",
        "min_low" => "round(min_low::numeric, 0)::int ||'W'|| min_low_yr ",
        "max_precip" => "to_char(max_precip, '99.99') ||'W'|| max_precip_yr ",
        "precip" => "round(precip::numeric, 2)"
    );
} else {
    $dbarray = array(
        "high" => "round(high::numeric, 0)::int",
        "low" => "round(low::numeric, 0)::int",
        "max_low" => "round(max_low::numeric, 0)::int",
        "max_high" => "round(max_high::numeric, 0)::int",
        "min_high" => "round(min_high::numeric, 0)::int",
        "min_low" => "round(min_low::numeric, 0)::int",
        "max_precip" => "to_char(max_precip, '99.99') ",
        "precip" => "round(precip::numeric, 2)"
    );
}

$sql = "SELECT station, years as yrs, " . $dbarray[$plot] . " as d 
    from climate WHERE valid = '" . $dbdate . "'
    and substr(station,1,2) = 'IA'";

$rs = pg_query($coopdb, $sql);
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $station = $row["station"];
    if (!array_key_exists($station, $cities)) continue;
    $pt = new pointObj();
    $pt->setXY($cities[$station]['lon'], $cities[$station]['lat'], 0);
    $pt->draw($map, $datal, $img, 0, $row["d"]);
}

$namer->draw($map, $img);
$counties->draw($map, $img);
$stlayer->draw($map, $img);
$datal->draw($map, $img);
iemmap_title($map, $img, $plotDate . " " . $var[$plot]);

$map->drawLabelCache($img);

$url = saveWebImage($img);

$ar = array(
    "all" => "Iowa",
    "ne" => "NE Iowa",
    "se" => "SE Iowa",
    "sw" => "SW Iowa",
    "nw" => "NW Iowa"
);
$aselect = make_select("area", $area, $ar);

$ar = array(
    "high" => "Average High Temperature",
    "low"         => "Average Low Temperature",
    "precip"      => "Average Precip",
    "max_high"      => "Record High Temperature",
    "min_low"      => "Record Low Temperature",
    "max_precip" => "Record Precip",
    "min_high"      => "Record Minimum High Temp",
    "max_low"      => "Record Maximum Low Temp"
);
$pselect = make_select("plot", $plot, $ar);

$mselect = monthSelect($month, "month");
$dselect = daySelect($day);

$t->content = <<<EOF
<h3>COOP Climate Data</h3>

 Using the COOP data archive, daily averages and extremes
  were calculated.  These numbers are <b>not</b> official, but we believe them
  to be accurate.  Please make your form selections on the left hand side and
  then click the 'Generate Plot' button.

  <div class="row">
  <div class="col-md-7">

<img src="{$url}" class="img img-responsive" />
   <br><i>You can right-click on the image to save it.</i>
  <br><li>Only one year with the record value is shown, there may have been 
    more.</li>

   </div><div class="col-md-5">
    
    <form name="f" method="GET" action="index.php">

<table width="100%">
<tr>
  <td colspan=2><b>Display Area:</b>
  </td></tr>

<tr><td colspan=2>
  {$aselect}
   <br><i>If you select a sub-region, the year of a record event will appear 
   as well.</i><br><br>

</td></tr>

<tr>
  <td colspan="2"><b>Select Parameter:</b>
  </td></tr>

<tr><td colspan=2>
  {$pselect}<br><br>

</td></tr>

<tr>
  <td colspan="2"><b>Select Date:</b>
  </td></tr>

<tr>
  <td>

 <b>Month:</b>
  <br>{$mselect}

</td><td>

 <b>Day:</b>
  <br>{$dselect}

<tr>
  <td colspan=2 align="center">
     <input type="submit" value="Generate Plot">
    </form><br><br>
  </td></tr>

<tr>
  <td colspan="2"><b>Download Options:</b>
  </td></tr>

<tr>
  <td colspan="2">
    <a href="request.php?month={$month}&day={$day}">
    <img src="/images/gisready.png" border="0"> shp, dbf, shx</a><br><br>
  </td></tr>


<tr>
  <td colspan="2"><b>Map Information:</b>
  </td></tr>

<tr>
  <td colspan="2">
  The black and red dots signify the climate record for the station.  Sites in 
  black date back till 1893 and sites in red to 1951.

</td></tr>

</table>

</div></div>

EOF;
$t->render('single.phtml');
