<?php
die();
include("../../../../config/settings.inc.php");

$TITLE = "IEM | Archived Precipitation Comparison";
include("$rootpath/include/header.php");
include("$rootpath/include/database.inc.php");

$area = isset($_GET["area"]) ? $_GET["area"] : "";
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");
$hour = isset($_GET["hour"]) ? $_GET["hour"]: date("h");
$plot = isset($_GET["plot"]) ? $_GET["plot"]: "";

?>
<div class="text">
<b>Nav:</b> <a href="/QC/">Quality Control</a> &nbsp; > &nbsp; 
  NEXRAD Estimates versus ASOS/AWOS observations
<?php
dl($mapscript);
include("$rootpath/include/mlib.php");

$height = 350;
$width = 350;

$map = ms_newMapObj("pcs.map");
//$map->setProjection("proj=lcc,lat_1=42.0666,lat_2=43.2666,lat_0=41.5,lon_0=-93.5,x_0=1500000,y_0=1000000");
$map->setProjection("proj=latlong");

if (strlen($plot) == 0){
  $plot = 'high';
}
if (strlen($area) == 0){
 $area = "all";
}
if (strlen($month) == 0){
  $month = date('m');
}
if (strlen($day) == 0){
  $day = date('d');
}
#$lx = -98; $ux = -89; $ly = 39.25; $uy = 44.75;
$lx = -97;
$ux = -90;
$ly = 40.0;
$uy = 44.0;
$dx = $ux - $lx;
$dy = $uy - $ly;

$ex = Array(
  "all" => Array($lx,          $ly,           $ux,           $uy),
  "ne" => Array($lx + ($dx/2), $ly + ($dy/2), $ux,           $uy),
  "se" => Array($lx + ($dx/2), $ly,           $ux          , $uy - ($dy/2) ),
  "sw" => Array($lx,           $ly,           $ux - ($dx/2), $uy - ($dy/2) ),
  "nw" => Array($lx,           $ly + ($dy/2), $ux - ($dx/2), $uy) );


$map->setextent($ex[$area][0], $ex[$area][1], $ex[$area][2], $ex[$area][3]);

if (isset($county)){
 if (strlen($county) > 10){
   $t = split(" ", $county);
   $map->setextent($t[0], $t[1], $t[2], $t[3]);
 }
}


$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);
$counties->setProjection("proj=latlong");

$datal = $map->getlayerbyname("datal");
$datal->set("status", MS_ON);
$datal->setProjection("proj=latlong");

$datal->set("data", "geom from (SELECT map.oid,
      round(data.p01i::numeric,2)::float::text as p01i, data.station,
      setsrid(map.geom, -1) as geom
      from stations map, hp_2002 data
      WHERE data.station = map.id and
      data.valid = '2002-".$month."-".$day." ".$hour.":00:00+0000') as foo using srid=-1");

$n1p = $map->getlayerbyname("n1p");
$n1p->set("status", MS_ON);
$n1p->set("data", "/mesonet/www/html/archive/data/2002/".$month."/".$day."/GIS/n1p_".$hour."00.png");
$n1p->setProjection("proj=latlong");


$img = $map->prepareImage();

$tpos = Array(
  "all" => Array(-95.4, 40.2),
  "ne" => Array(-92.9, 43.7),
  "se" => Array(-92.9, 40.3),
  "sw" => Array(-96.4, 40.4),
  "nw" => Array(-96.7, 43.65) );

$ts = mktime($hour,0,0, $month, $day, 2002 );
$imghref = strftime('%Y/%m/%d/GIS/n1p_%H00', $ts);
$cgi = strftime('year=%Y&month=%m&day=%d&hour=%H', $ts);
$plotDate = strftime('%b %d', $ts );

$counties->draw($img);
$n1p->draw($img);
$datal->draw($img);

$map->drawLabelCache($img);

$url = $img->saveWebImage();


echo "<table border=0>
 <tr>
  <td valign=\"top\"><img src=\"$url\" border=\"1\">"; ?>
   <br><i>You can right-click on the image to save it.</i>
   <img src="n1p_bar.gif" alt=\"Legend\">
 </td>
  <td rowspan="2" valign="top">
    <form method="GET" action="index.php">

<table width="100%">
<tr>
  <td colspan=3 class="subtitle"><b>Display Area:</b>
  </td></tr>

<tr><td colspan=2>
<b>View a Region of Iowa:</b><br>
  <select name="area">
    <option value="all" <?php if ($area == "all") echo "SELECTED"; ?> >Iowa
    <option value="ne" <?php if ($area == "ne") echo "SELECTED"; ?> >NE Iowa
    <option value="se" <?php if ($area == "se") echo "SELECTED"; ?> >SE Iowa
    <option value="sw" <?php if ($area == "sw") echo "SELECTED"; ?> >SW Iowa
    <option value="nw" <?php if ($area == "nw") echo "SELECTED"; ?> >NW Iowa
   </select>

<br><b>Select a County in Iowa:</b><br>
   <?php include('counties.php'); ?><br><br>

</td></tr>

<tr>
  <td colspan=3 class="subtitle"><b>Select Time (GMT):</b>
  </td></tr>


<tr>
  <td colspan=3>
  <i>Currently, only data between 15 April 2002 and 1 Nov 2002 is 
available in this system</i><br>
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
   printf ("%s%02d%s", '<option value="', $k, '"' );
   if ($k == (int)$day){
     echo " SELECTED";
   }
   echo ">".$k."\n";
  }
  ?>
  </select>
 </td><td>

 <b>Hour:</b>
  <br><select name="hour">
  <?php
  for ($k=0;$k<24;$k++){
   printf ("%s%02d%s", '<option value="', $k, '"' );
   if ($k == (int)$hour){
     echo "SELECTED";
   }
   echo ">".$k."\n";
  }
  ?>
  </select>
 </td>
</tr>
<tr>
  <td colspan=3 align="center">
     <input type="submit" value="Generate Plot">
    </form><br><br>
  </td></tr>

<tr>
  <td colspan=3 class="subtitle"><b>Download Options:</b>
  </td></tr>

<tr>
  <td colspan=3>
    <img src="/images/gisready.png">
    <a href="/archive/data/<?php echo $imghref; ?>.png">Rainfall image</a>  and
    <a href="/archive/data/<?php echo $imghref; ?>.wld">world file</a>
    <i>(This image is in geographic coordinates.)</i>
    <br>A <a href="hourlydata.php?<?php echo $cgi; ?>">shapefile</a> also exists with the 
    precip observations included.<br><br>
  </td></tr>

<tr>
  <td colspan=3 class="subtitle"><b>Scatter Plot:</b>
  </td></tr>

<tr>
  <td colspan=3>
    <img src="/plotting/stats/precScat.php?month=<?php echo $month; ?>&day=<?php echo $day; ?>&hour=<?php echo $hour; ?>">
  </td></tr>

</table></td></tr>

<tr><td>
<font class="subtitle"><b>Raw Precip obs (inches):</b></font>
  <br><b>Key:</b> <font color="#ff3030">Obs Larger</font> 
    <font color="#87cefa">NEX Larger</font> 
  <br><table style="font-size: 10pt" border=0 cellpadding=2 cellspacing=0 width=100%>
  <tr>
    <th align="left">ID:</th>
    <th align="left">Station:</th>
    <th align="left">Ob:</th>
    <th align="left">NEX Est:</th>
    <th align="left">Ob - NEX</th>
  </tr>
<?php
 $c = iemdb("postgis");
 $q = "SELECT n.valid, n.station, round((CASE WHEN n.p01i < 0 
   THEN 0 ELSE n.p01i END)::numeric, 2)
   as n_p01i, round(h.p01i::numeric,2) as h_p01i from nex_2002 n LEFT JOIN hp_2002 h 
   using (valid, station) WHERE n.valid = '2002-".$month."-".$day." ".$hour.":00:00+0000' and (n.p01i > 0 or h.p01i > 0)";
 pg_exec($c, "SET TIME ZONE 'GMT'");
 $rs = pg_exec($c, $q);


 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++){
   $pdiff = ($row["h_p01i"] - $row["n_p01i"]);
   if ($pdiff == 0)  $bgcolor = "#ffffff";
   else if ($pdiff > 0)  $bgcolor = "#ff3030";
   else if ($pdiff < 0)  $bgcolor = "#87cefa";
   echo "<tr bgcolor=\"". $bgcolor ."\"><td>". $row["station"] ."</td>
    <td>". $cities[$row["station"]]['city'] ."</td>
    <td>". $row["h_p01i"] ."</td>
    <td>". $row["n_p01i"] ."</td>
    <td>". $pdiff ."</td>
    </tr>";
 }

 pg_close($c);
?>
 </table>

<?php
  echo "</td></tr>
</table>";
?>
</div>
<?php
include("$rootpath/include/footer.php");

?>
