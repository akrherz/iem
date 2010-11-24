<?php
// How simple can it get!
// Daryl Herzmann

$oid = intval($id);

if ( strlen($img_x) > 0){  // Augh, they clicked!!

  $extents = Array("DMX" => Array(1270178, 863000, 1755341, 1276783),
   "FSD" => Array(540178, -34000, 800341, 450783),
   "ARX" => Array(760178, -30000, 900341, 450783),
   "DVN" => Array(450000, 350000, 800341, 800783),
   "OAX" => Array(220000, -42000, 630000, 400000),
   "EAX" => Array(650000, 174000, 850000, 590000),
   "MPX" => Array(640178, 50000, 900341, 500783)  );

  $projs = Array("DMX" => "proj=lcc,lat_1=42.0666,lat_2=43.2666,lat_0=41.5,lon_0=-93.5,x_0=1500000,y_0=1000000",
  "FSD" => "proj=lcc,lat_1=43.78,lat_2=45.21,lat_0=43,lon_0=-96,x_0=800000,y_0=100000",
  "ARX" => "proj=lcc,lat_1=43.78,lat_2=45.21,lat_0=43,lon_0=-92,x_0=800000,y_0=100000",
  "OAX" => "proj=lcc,lat_1=40.61,lat_2=41.78,lat_0=40,lon_0=-95.5,x_0=500000,y_0=0",
  "DVN" => "proj=tmerc,lat_0=36.666,lon_0=-90.16,k=0.9999,x_0=700000,y_0=0",
  "EAX" => "proj=tmerc,lat_0=36.166,lon_0=-94.5,k=0.9999,x_0=850000,y_0=0",
  "MPX" => "proj=lcc,lat_1=43.78,lat_2=45.21,lat_0=43,lon_0=-94,x_0=800000,y_0=100000"  );

  $projInObj = ms_newprojectionobj("proj=latlong");
  $projOutObj = ms_newprojectionobj( $projs[$site] );

  $widthPix = 450;
  $widthGeo = $lon_ur - $lon_ll;
  $pixToGeo = $widthGeo / $widthPix;
  //echo "<br>". ($img_x );
  $xM = $lon_ll + $pixToGeo * $img_x ; 

  $heightPix = 450;
  $heightGeo = $lat_ur - $lat_ll;
  $pixToGeo = $heightGeo / $heightPix;
  //echo "<br>". ($img_y );
  $yM = $lat_ur - $pixToGeo * $img_y ;


  $point = ms_newpointobj();
  $point->setXY($xM, $yM);
  $point = $point->project($projOutObj, $projInObj);

  $query = "SELECT * from warnings WHERE 
   GeometryFromText('POINT(". $point->x ." ". $point->y .")', -1) && geom_new
   and issue < CURRENT_TIMESTAMP and expire > CURRENT_TIMESTAMP LIMIT 1";

} else {
  $query = "SELECT * from warnings WHERE oid = $oid ";
}

$connect = pg_connect("host=mesonet dbname=postgis user=mesonet");


$result = pg_exec($connect, $query);

$row = pg_fetch_array($result, 0);

echo "<pre>". $row["report"] ."</pre>";

?>
