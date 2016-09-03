<?php
/* 
 * Generate GeoJSON SBW information for a period of choice
 */
header("Content-type: application/vnd.geo+json");
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("../../include/vtec.php");
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



$rs = pg_query($postgis, "SET TIME ZONE 'UTC'");

if (isset($_REQUEST["phenomena"])){
  $year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
  $wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
  $eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
  $phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
  $significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";
  	
  $rs = pg_prepare($postgis, "SELECT", "SELECT  
  			issue, expire, phenomena, status, w.wfo, eventid, significance,
  		to_char(issue, 'YYYY-MM-DDThh24:MI:SSZ') as iso_issue,
  		to_char(expire, 'YYYY-MM-DDThh24:MI:SSZ') as iso_expire,
  		ST_asGeoJson(geom) as geojson
      FROM sbw_$year w WHERE
      status = 'NEW' and significance = $1 and wfo = $2
      and eventid = $3 and phenomena = $4");
  $rs = pg_execute($postgis, "SELECT", Array($significance, $wfo,
  		$eventid, $phenomena));
  if (pg_num_rows($rs) < 1){
  	$rs = pg_prepare($postgis, "SELECT222", "SELECT 
  			issue, expire, phenomena, status, w.wfo, eventid, significance,
  		to_char(issue, 'YYYY-MM-DDThh24:MI:SSZ') as iso_issue,
  		to_char(expire, 'YYYY-MM-DDThh24:MI:SSZ') as iso_expire,
  			ST_asGeoJson(u.geom) as geojson
  			FROM warnings_$year w JOIN ugcs u on (u.gid = w.gid) WHERE
  			significance = $1 and w.wfo = $2
  			and eventid = $3 and phenomena = $4");
  	$rs = pg_execute($postgis, "SELECT222", Array($significance, $wfo,
  		$eventid, $phenomena));
  }
  
} else {
	$wfos = isset($_REQUEST["wfos"]) ? explode(",", $_REQUEST["wfos"]) : Array();
	$sts = isset($_REQUEST["sts"]) ? toTime($_REQUEST["sts"]) : die("sts not defined");
	$ets = isset($_REQUEST["ets"]) ? toTime($_REQUEST["ets"]) : die("ets not defined");
	$wfoList = implode("','", $wfos);
	$str_wfo_list = "and wfo in ('$wfoList')";
	if ($wfoList == ""){  $str_wfo_list = ""; }
	
	$rs = pg_prepare($postgis, "SELECT", "SELECT 
  			issue, expire, phenomena, status, w.wfo, eventid, significance,
  		to_char(issue, 'YYYY-MM-DDThh24:MI:SSZ') as iso_issue,
  		to_char(expire, 'YYYY-MM-DDThh24:MI:SSZ') as iso_expire,
			ST_asGeoJson(geom) as geojson
      FROM sbw w WHERE
      issue < $2 and
      expire > $1 and expire < $3 $str_wfo_list
      and status = 'NEW' and significance is not null
      LIMIT 500");
  $rs = pg_execute($postgis, "SELECT", Array(date("Y-m-d H:i", $sts), 
                                           date("Y-m-d H:i", $ets),
                                           date("Y-m-d H:i", $ets + 86400*10)));
}

$ar = Array("type"=>"FeatureCollection",
      "crs" => Array("type"=>"EPSG", 
                     "properties" => Array("code"=>4326,
                                  "coordinate_order" => Array(1,0))),
      "features" => Array()
);

$reps = Array();
$subs = Array();

for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++)
{
  $wfo = $row["wfo"];
  $reps[] = "\"REPLACEME$i\"";
  $subs[] = $row["geojson"];
  $vtecurl = sprintf("%s/vtec/#%s-O-NEW-K%s-%s-%s-%04d", ROOTURL, 
      substr($row["issue"],0,4),
      $wfo, $row["phenomena"], $row["significance"], $row["eventid"] );

  $z = Array("type"=>"Feature", "id"=>$i, 
             "properties"=>Array(
                "phenomena" => $row["phenomena"],
                "significance" => $row["significance"],
                "wfo"       => $row["wfo"],
                "eventid"   => $row["eventid"],
                "issue"     => $row["iso_issue"],
                "expire"     => $row["iso_expire"],
                "link"         => sprintf("<a href='%s'>%s %s %s</a> &nbsp; ",
         $vtecurl, $vtec_phenomena[$row["phenomena"]],
         $vtec_significance[$row["significance"]], $row["eventid"]),
              ),
             "geometry"=> "REPLACEME$i");
                         
  $ar["features"][] = $z;
}
echo str_replace($reps, $subs, json_encode($ar));
?>
