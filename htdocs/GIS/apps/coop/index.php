<?php
include("../../../../config/settings.inc.php");

$plot = isset($_GET["plot"]) ? $_GET["plot"]: "high";
$area = isset($_GET["area"]) ? $_GET["area"]: "all";
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");

$TITLE = "IEM | NWS COOP | GIS Plotting";
include("$rootpath/include/header.php");
?>

<?php
dl($mapscript);
include("$rootpath/include/all_locs.php");
include("$rootpath/include/mlib.php");

$height = 350;
$width = 350;

$map = ms_newMapObj("sites.map");
$map->setProjection("proj=lcc,lat_1=42.0666,lat_2=43.2666,lat_0=41.5,lon_0=-93.5,x_0=1500000,y_0=1000000");

$lx = 1220000;
$ux = 1797000;
$ly =  885000;
$uy = 1227000;
$dx = $ux - $lx;
$dy = $uy - $ly;

$ex = Array(
  "all" => Array($lx,          $ly,           $ux,           $uy),
  "ne" => Array($lx + ($dx/2), $ly + ($dy/2), $ux,           $uy),
  "se" => Array($lx + ($dx/2), $ly,           $ux          , $uy - ($dy/2) ),
  "sw" => Array($lx,           $ly,           $ux - ($dx/2), $uy - ($dy/2) ),
  "nw" => Array($lx,           $ly + ($dy/2), $ux - ($dx/2), $uy) );


$map->setextent($ex[$area][0], $ex[$area][1], $ex[$area][2], $ex[$area][3]);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);
$counties->setProjection("proj=latlong");

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);
$stlayer->setProjection("proj=latlong");

$dot = $map->getlayerbyname("dot");
$dot->set("status", MS_ON);
$dot->setProjection("proj=latlong");

$site = $map->getlayerbyname("site");
$site->set("status", MS_ON);
$site->setProjection("proj=latlong");

$coop = $map->getlayerbyname("coop");
$coop->set("status", MS_OFF);
$coop->setProjection("proj=latlong");

$datal = $map->getlayerbyname("datal");
$datal->set("status", MS_ON);
$datal->setProjection("proj=latlong");

$ttt = $map->getlayerbyname("ttt");
$ttt->set("status", MS_ON);
$ttt->setProjection("proj=latlong");

$img = $map->prepareImage();

$tpos = Array(
  "all" => Array(-95.4, 40.2),
  "ne" => Array(-92.9, 43.7),
  "se" => Array(-92.9, 40.3),
  "sw" => Array(-96.4, 40.4),
  "nw" => Array(-96.7, 43.65) );

$ts = mktime(0,0,0, $month, $day, 2000 );
$plotDate = strftime('%b %d', $ts );

$var = Array("max_precip" => "Record Daily Precip [in]",
  "precip" => "Average Precipitation [in]",
  "low" => "Average Low Temp [F]",
  "max_low" => "Record Max Low Temp [F]",
  "max_high" => "Record Max High Temp [F]",
  "min_low" => "Record Min Low Temp [F]",
  "min_high" => "Record Min High Temp [F]",
  "high" => "Average High Temp [F]");

$pt = ms_newPointObj();
$pt->setXY($tpos[$area][0], $tpos[$area][1], 0);
$pt->draw($map, $ttt, $img, 0, $plotDate ." ". $var[$plot] );
$pt->free();



$dbdate = "2000-". $month ."-". $day;

if (strcmp($area, 'all') != 0){

$dbarray = Array("high" => "round(data.high::numeric, 0)::int",
    "low" => "round(data.low::numeric, 0)::int",
    "max_low" => "round(data.max_low::numeric, 0)::int ||'W'|| max_low_yr ",
    "max_high" => "round(data.max_high::numeric, 0)::int ||'W'|| max_high_yr ",
    "min_high" => "round(data.min_high::numeric, 0)::int ||'W'|| min_high_yr ",
    "min_low" => "round(data.min_low::numeric, 0)::int ||'W'|| min_low_yr ",
 "max_precip" => "to_char(data.max_precip, '99.99') ||'W'|| max_precip_yr ",
    "precip" => "to_char(data.precip, '99.99')");

} else {
$dbarray = Array("high" => "round(data.high::numeric, 0)::int",
    "low" => "round(data.low::numeric, 0)::int",
    "max_low" => "round(data.max_low::numeric, 0)::int",
    "max_high" => "round(data.max_high::numeric, 0)::int",
    "min_high" => "round(data.min_high::numeric, 0)::int",
    "min_low" => "round(data.min_low::numeric, 0)::int",
     "max_precip" => "to_char(data.max_precip, '99.99') ",
    "precip" => "to_char(data.precip, '99.99')");
}

$datal->set('data', "geom from 
    (SELECT data.years as yrs, map.OID, map.geom, ". $dbarray[$plot] ." as d 
    from stations map, climate data
    WHERE data.station = lower(map.id) and 
    data.valid = '". $dbdate ."') as foo");

$st_cl = ms_newclassobj($stlayer);
//$st_cl->set("outlinecolor", $green);
$st_cl->set("status", MS_ON);

$stlayer->draw( $img);
$counties->draw($img);
$ttt->draw($img);
$datal->draw($img);

$map->drawLabelCache($img);

$url = $img->saveWebImage();

$im = @imagecreatefrompng("/var/www/htdocs/". $url );

echo "<h3 class=\"heading\">COOP Climate Data</h3><p>
 <div class=\"text\">Using the COOP data archive, daily averages and extremes
  were calculated.  These numbers are <b>not</b> official, but we believe them
  to be accurate.  Please make your form selections on the left hand side and
  then click the 'Generate Plot' button.
";

echo "<table border=0>
 <tr>
  <td valign=\"top\"><img src=\"$url\" border=\"1\">"; ?>
   <br><i>You can right-click on the image to save it.</i>
  <br><li>Only one year with the record value is shown, there may have been 
    more.</li>
 </td>
  <td>
    <form method="GET" action="index.php">

<table width="100%">
<tr>
  <td colspan=2 class="subtitle"><b>Display Area:</b>
  </td></tr>

<tr><td colspan=2>
  <select name="area">
    <option value="all" <?php if ($area == "all") echo "SELECTED"; ?> >Iowa
    <option value="ne" <?php if ($area == "ne") echo "SELECTED"; ?> >NE Iowa
    <option value="se" <?php if ($area == "se") echo "SELECTED"; ?> >SE Iowa
    <option value="sw" <?php if ($area == "sw") echo "SELECTED"; ?> >SW Iowa
    <option value="nw" <?php if ($area == "nw") echo "SELECTED"; ?> >NW Iowa
   </select>
   <br><i>If you select a sub-region, the year of a record event will appear 
   as well.</i><br><br>

</td></tr>

<tr>
  <td colspan=2 class="subtitle"><b>Select Parameter:</b>
  </td></tr>

<tr><td colspan=2>
  <select name="plot">
    <option value="high" 
      <?php if ($plot == "high") echo "SELECTED"; ?> >Average High Temperature
    <option value="low" 
      <?php if ($plot == "low") echo "SELECTED"; ?> >Average Low Temperature
    <option value="precip" 
      <?php if ($plot == "precip") echo "SELECTED"; ?> >Average Precip
   <option value="max_high" 
    <?php if ($plot == "max_high") echo "SELECTED"; ?> >Record High Temperature
   <option value="min_low" 
     <?php if ($plot == "min_low") echo "SELECTED"; ?> >Record Low Temperature
    <option value="max_precip" 
      <?php if ($plot == "max_precip") echo "SELECTED"; ?> >Record Precip
    <option value="min_high" 
      <?php if ($plot == "min_high") echo "SELECTED"; ?> >Record Minimum High Temp
    <option value="max_low" 
      <?php if ($plot == "max_low") echo "SELECTED"; ?> >Record Maximum Low Temp
  </select><br><br>

</td></tr>

<tr>
  <td colspan=2 class="subtitle"><b>Select Date:</b>
  </td></tr>

<tr>
  <td>

 <b>Month:</b>
  <br><select name="month">
    <option value="01" <?php if ($month == "01") echo "SELECTED"; ?> >January
    <option value="02" <?php if ($month == "02") echo "SELECTED"; ?> >February
    <option value="03" <?php if ($month == "03") echo "SELECTED"; ?> >March
    <option value="04" <?php if ($month == "04") echo "SELECTED"; ?> >April
    <option value="05" <?php if ($month == "05") echo "SELECTED"; ?> >May
    <option value="06" <?php if ($month == "06") echo "SELECTED"; ?> >June
    <option value="07" <?php if ($month == "07") echo "SELECTED"; ?> >July
    <option value="08" <?php if ($month == "08") echo "SELECTED"; ?> >August
    <option value="09" <?php if ($month == "09") echo "SELECTED"; ?> >September
    <option value="10" <?php if ($month == "10") echo "SELECTED"; ?> >October
    <option value="11" <?php if ($month == "11") echo "SELECTED"; ?> >November
    <option value="12" <?php if ($month == "12") echo "SELECTED"; ?> >December
  </select>

</td><td>

 <b>Day:</b>
  <br><select name="day">
  <?php
  for ($k=1;$k<32;$k++){
   echo "<option value=\"".$k."\" ";
   if ($k == (int)$day){
     echo "SELECTED";
   }
   echo ">".$k."\n";
  }
  ?>
  </select>

<tr>
  <td colspan=2 align="center">
     <input type="submit" value="Generate Plot">
    </form><br><br>
  </td></tr>

<tr>
  <td colspan=2 class="subtitle"><b>Download Options:</b>
  </td></tr>

<tr>
  <td colspan=2>
    <a href="request.php?month=<?php echo $month; ?>&day=<?php echo $day;
    ?>"><img src="/images/gisready.png" border=0> shp, dbf, shx</a><br><br>
  </td></tr>


<tr>
  <td colspan=2 class="subtitle"><b>Map Information:</b>
  </td></tr>

<tr>
  <td colspan=2>
  The black and red dots signify the climate record for the station.  Sites in 
  black date back till 1893 and sites in red to 1951.

</td></tr>

</table>

<?php
  echo "</td></tr>
</table></div>";
?>

<?php
include ("$rootpath/include/footer.php");
?>
