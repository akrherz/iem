<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
// Figure out feature just clicked
// $imgx, $imgy, $site, $fips

//select linkitem, name from nws_counties WHERE GeometryFromText('POINT(-95  42)', -1) && the_geom;

$projInObj = ms_newprojectionobj("init=epsg:4326");
$projOutObj = ms_newprojectionobj( $projs[$site] );

//echo "<p>UPPER RIGHT X: ". $lon_ur;
//echo "<p>UPPER RIGHT Y: ". $lat_ur;
//echo "<p>LOWER LEFT X: ". $lon_ll;
//echo "<p>LOWER LEFT Y: ". $lat_ll;

$widthPix = 200;
$widthGeo = $lon_ur - $lon_ll;
$pixToGeo = $widthGeo / $widthPix;
//echo "<br>". ($img_x );
$xM = $lon_ll + $pixToGeo * $img_x ; 

$heightPix = 200;
$heightGeo = $lat_ur - $lat_ll;
$pixToGeo = $heightGeo / $heightPix;
//echo "<br>". ($img_y );
$yM = $lat_ur - $pixToGeo * $img_y ;

//echo "<br>". $xM ." = ". $yM;

$point = ms_newpointobj();
$point->setXY($xM, $yM);
$point = $point->project($projOutObj, $projInObj);

//echo "<br>". $point->x ." = ". $point->y ;

$query = "SELECT linkitem, name from nws_counties WHERE 
  GeometryFromText('POINT(". $point->x ." ". $point->y .")', -1) && the_geom";

$connection = iemdb("postgis");


$result = pg_exec($connection, $query);

pg_close($connection);

$row = @pg_fetch_array($result,0);

//echo "<br>". $row["name"];

$fips = $row["linkitem"];
$site = $row["cwa"];

?>
