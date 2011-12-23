<?php
// nexlib.php
//  NEXRAD functions!!!
//

// DMX is Iowa North!
// FSD is Minnesota South! +2 W
// MPX is Minnesota South!
// ARX is Minnesota South!
// DVN is Illinois West!
// OAX is Iowa South! +2 W
// EAX is Iowa South


//  "FSD" => "proj=lcc,lat_1=43.78,lat_2=45.21,lat_0=43,lon_0=-96,x_0=800000,y_0=100000",
//  "ARX" => "proj=lcc,lat_1=43.78,lat_2=45.21,lat_0=43,lon_0=-92,x_0=800000,y_0=100000",
//  "OAX" => "proj=lcc,lat_1=40.61,lat_2=41.78,lat_0=40,lon_0=-95.5,x_0=500000,y_0=0",
//  "ABR" => "proj=lcc,lat_1=42.83,lat_2=44.4,lat_0=42.33,lon_0=-98.33,x_0=600000,y_0=0",
//  "UDX" => "proj=lcc,lat_1=40,lat_2=43,lat_0=39.83,lon_0=-103,x_0=500000,y_0=0"
//  "EAX" => "proj=tmerc,lat_0=36.166,lon_0=-94.5,k=0.9999,x_0=850000,y_0=0",
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

// "FSD" => Array(600178, -54000, 880341, 380783),
//  "ARX" => Array(760178, -30000, 900341, 450783),
//  "OAX" => Array(220000, -42000, 630000, 400000),
//  "ABR" => Array(300178, 100000, 800341, 600783),
//  "UDX" => Array(320178, 320000, 850341, 620783) 
// "EAX" => Array(650000, 100000, 1100000, 550000)
// "MPX" => Array(640178, 50000, 900341, 500783),
//  "DVN" => Array(450000, 350000, 800341, 800783),
// "DMX" => Array(176500, 4450000, 710900, 4850000),
 // "DMX" => Array(-96.72, 38.72, -90.72, 44.72),
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
?>
