<?php
/* 
 * Generate GeoJSON SBW information for a period of choice
 */
require_once 'Zend/Json.php';
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");
$postgis = iemdb("postgis");

function toTime($s){
  return mktime( intval(substr($s,8,2)), 
               intval(substr($s,10,2)), 
               intval(substr($s,12,2)), 
               intval(substr($s,4,2)), 
               intval(substr($s,6,2)), 
               intval(substr($s,0,4)) );
}

/* Look for calling values */
$wfos = isset($_REQUEST["wfos"]) ? explode(",", $_REQUEST["wfos"]) : die("wfos not defined");
$sts = isset($_REQUEST["sts"]) ? toTime($_REQUEST["sts"]) : die("sts not defined");
$ets = isset($_REQUEST["ets"]) ? toTime($_REQUEST["ets"]) : die("ets not defined");
$wfoList = implode("','", $wfos);

$rs = pg_query("SET TIME ZONE 'GMT'");
$rs = pg_prepare($postgis, "SELECT", "SELECT *, 
      ST_asGeoJson(geom) as geojson
      FROM warnings WHERE
      issue < $2 and
      expire > $1 and expire < $3 and wfo in ('$wfoList')
      and gtype = 'P'
      LIMIT 500");

$rs = pg_execute($postgis, "SELECT", Array(date("Y-m-d H:i", $sts), 
                                           date("Y-m-d H:i", $ets),
                                           date("Y-m-d H:i", $ets + 86400*10)));


$ar = Array("type"=>"FeatureCollection",
      "crs" => Array("type"=>"EPSG", 
                     "properties" => Array("code"=>4326,
                                  "coordinate_order" => Array(1,0))),
      "features" => Array()
);

$reps = Array();
$subs = Array();

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $wfo = $row["wfo"];
  $reps[] = "\"REPLACEME$i\"";
  $subs[] = $row["geojson"];

  $z = Array("type"=>"Feature", "id"=>$i, 
             "properties"=>Array(
                "phenomena" => $row["phenomena"],
                "wfo"       => $row["wfo"],
                "issue"     => substr($row["issue"],0,16),
                "expire"     => substr($row["expire"],0,16),
              ),
             "geometry"=> "REPLACEME$i");
                         
  $ar["features"][] = $z;
}
echo str_replace($reps, $subs, Zend_Json::encode($ar));
?>
