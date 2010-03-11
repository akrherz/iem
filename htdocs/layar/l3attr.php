<?php
/* Generate JSON of l3 nexrad attributes! */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
require_once 'Zend/Json.php';
$postgis = iemdb("postgis");


/* Figure out what was requested */
$center_lat = isset($_GET["lat"]) ? $_GET["lat"]: 58.1;
$center_lng = isset($_GET["lon"]) ? $_GET["lon"]: -97.0;
$radius = isset($_GET["radius"]) ? floatval($_GET["radius"]): 2000.0; # in meters

$rs = pg_prepare($postgis, "SELECT", "SELECT x(geom) as lon, y(geom) as lat,
     distance(transform(geom,2163), 
       transform(
        GeomFromEWKT('SRID=4326;POINT($center_lng $center_lat)'),2163)) as dist,
      * from nexrad_attributes WHERE distance(transform(geom,2163), 
       transform(
        GeomFromEWKT('SRID=4326;POINT($center_lng $center_lat)'),2163)) < $radius");

header('Content-type: application/json');
$rs = pg_execute($postgis, "SELECT", Array());
if (pg_num_rows($rs) == 0){
  $json = array("hotspots"=> Array(), "layer"=>"nexradl3attr", "errorString"=>"Sorry, no attributes close to you right now!", "morePages"=>false, "errorCode"=>21, "nextPageKey"=>null);
  echo  Zend_Json::encode($json);
  exit; // 

}
/*
 nexrad         | character(3)             | 
 storm_id       | character(2)             | 
 geom           | geometry                 | 
 azimuth        | smallint                 | 
 range          | smallint                 | 
 tvs            | character varying(10)    | 
 meso           | character varying(10)    | 
 posh           | smallint                 | 
 poh            | smallint                 | 
 max_size       | real                     | 
 vil            | smallint                 | 
 max_dbz        | smallint                 | 
 max_dbz_height | real                     | 
 top            | real                     | 
 drct           | smallint                 | 
 sknt           | smallint                 | 
 valid          | timestamp with time zone | 
*/
$json = Array("layer"=>"nexradl3attr", 
        "errorString"=>"ok", "morePages"=>false, "errorCode"=>0, 
        "nextPageKey"=>null);

for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $lat = sprintf("%.6f", $row["lat"]);
  $lon = sprintf("%.6f", $row["lon"]);
  $json["hotspots"][] = array(
    "actions" => array(),
    "attribution" => "NWS ". $row["nexrad"] ." NEXRAD",
    "distance" => intval($row["dist"]), // km back to meter!
    "id" => $i,
    "imageURL" => null,
    "lat" => (int) str_replace(".", "", $lat),
    "lon" => (int) str_replace(".", "", $lon), 
    "line2" => null,
    "line3" => null,
    "line4" => null,
    "title" => sprintf("%s %s %s", $row['storm_id'], $row["azimuth"], $row["range"]),
    "type" => 0);
}


echo  Zend_Json::encode($json);
?>
