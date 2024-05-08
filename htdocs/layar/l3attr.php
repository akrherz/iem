<?php
/* Generate JSON of l3 nexrad attributes! */
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
$postgis = iemdb("radar");


/* Figure out what was requested */
$center_lat = isset($_GET["lat"]) ? floatval(xssafe($_GET["lat"])): 58.1;
$center_lng = isset($_GET["lon"]) ? floatval(xssafe($_GET["lon"])): -97.0;
$radius = isset($_GET["radius"]) ? floatval(xssafe($_GET["radius"])): 2000.0; # in meters

$rs = pg_prepare($postgis, "SELECT", "SELECT ST_x(geom) as lon, ST_y(geom) as lat,
     ST_distance(ST_transform(geom,9311), 
       ST_transform(
        ST_Point($center_lng, $center_lat, 4326),9311)) as dist,
      * from nexrad_attributes WHERE ST_distance(ST_transform(geom,9311), 
       ST_transform(
        ST_Point($center_lng, $center_lat, 4326),9311)) < $radius");

//header('Content-type: application/json');
$rs = pg_execute($postgis, "SELECT", Array());
if (pg_num_rows($rs) == 0){
  $json = array("hotspots"=> Array(), "layer"=>"nexradl3attr", "errorString"=>"Sorry, no attributes close to you right now!", "morePages"=>false, "errorCode"=>21, "nextPageKey"=>null);
  echo json_encode($json);
  die();

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

for($i=0;$row=pg_fetch_assoc($rs);$i++)
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
    "line2" => sprintf("Azimuth: %.1f Range: %.1f", $row["azimuth"], $row["range"]),
    "line3" => sprintf("POSH: %.0f", $row["posh"]),
    "line4" => sprintf("VIL: %.1f", $row["vil"]),
    "title" => sprintf("%s %s %s", $row['storm_id'], $row["azimuth"], $row["range"]),
    "type" => 0);
}

echo json_encode($json);
