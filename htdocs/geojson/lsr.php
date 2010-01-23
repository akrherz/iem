<?php
/* 
 * Generate GeoJSON LSR information for a period of choice
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
      x(geom) as lon, y(geom) as lat 
      FROM lsrs WHERE
      valid BETWEEN $1 and $2 and wfo in ('$wfoList')
      LIMIT 500");

$rs = pg_execute($postgis, "SELECT", Array(date("Y-m-d H:i", $sts), 
                                           date("Y-m-d H:i", $ets) ) );


$ar = Array("type"=>"FeatureCollection",
      "crs" => Array("type"=>"EPSG", 
                     "properties" => Array("code"=>4326,
                                  "coordinate_order" => Array(1,0))),
      "features" => Array()
);

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $lon = $row["lon"];
  $lat = $row["lat"];
  $wfo = $row["wfo"];
  $products = "N/A";
  if (isset($_GET["inc_ap"]) && $_GET["inc_ap"] == "yes")
  {
     /* Lets go looking for warnings for this particular LSR, fast please */
     $sql = sprintf("SELECT distinct phenomena, significance, eventid 
        from warnings_%s
        WHERE wfo = '%s' and issue <= '%s' 
        and issue > '%s'::timestamp - '7 days'::interval and expire > '%s'
        and GeometryFromText('SRID=4326;POINT(%s %s)') && geom
        and contains(geom, GeometryFromText('SRID=4326;POINT(%s %s)') )", 
        substr($row["valid"],0,4), $wfo, $row["valid"], $row['valid'], 
        $row["valid"], $lon, $lat, $lon, $lat );
     $rs2 = pg_query($postgis, $sql);
     $products = "";
     for ($j=0;$row2 = @pg_fetch_array($rs2,$j); $j++)
     {
      $vtecurl = sprintf("%s/vtec/#%s-O-NEW-K%s-%s-%s-%04d", $rooturl, 
      substr($row["valid"],0,4),
      $wfo, $row2["phenomena"], $row2["significance"], $row2["eventid"] );
      $products .= sprintf("<a href='%s'>%s %s %s</a><br />",
         $vtecurl, $vtec_phenomena[$row2["phenomena"]],
         $vtec_significance[$row2["significance"]], $row2["eventid"]);
     }
     if ($products == ""){ $products = "None"; }
  }

  $z = Array("type"=>"Feature", "id"=>$i, 
             "properties"=>Array(
                "magnitude" => $row["magnitude"],
                "wfo"       => $row["wfo"],
                "valid"     => substr($row["valid"],0,16),
                "type"      => $row["type"],
                "county"    => $row["county"],
                "typetext"  => $row["typetext"],
                "remark"    => $row["remark"],
                "city"      => $row["city"],
                "prodlinks" => $products,
              ),
             "geometry"=>Array("type"=>"Point",
                         "coordinates"=>Array($lon,$lat)));
  $ar["features"][] = $z;
}

echo Zend_Json::encode($ar);
?>
