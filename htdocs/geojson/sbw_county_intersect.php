<?php
header("Content-type: application/vnd.geo+json");
include_once "../../config/settings.inc.php";
include_once "../../include/database.inc.php";
$connect = iemdb("postgis");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? $_GET["wfo"] : "MPX";
if (strlen($wfo) > 3){
    $wfo = substr($wfo, 1, 3);
}
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";

$sql = <<<EOF
	WITH stormbased as (SELECT geom from sbw_$year where wfo = '$wfo'
		and eventid = $eventid and significance = '$significance'
		and phenomena = '$phenomena' and status = 'NEW'),
	countybased as (SELECT ST_Union(u.geom) as geom from
		warnings_$year w JOIN ugcs u on (u.gid = w.gid)
		WHERE w.wfo = '$wfo' and eventid = $eventid and
		significance = '$significance' and phenomena = '$phenomena')

	SELECT ST_asgeojson(geo) as geojson, ST_Length(ST_transform(geo,2163)) as sz from
		(SELECT ST_SetSRID(ST_intersection(
	      ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(c.geom),1)),0.02),
	      ST_exteriorring(ST_geometryn(ST_multi(s.geom),1))
	   	 ), 4326) as geo
	from stormbased s, countybased c) as foo
EOF;
$rs = pg_exec($connect, $sql);


$ar = Array(
  "type"=>"FeatureCollection",
  "features" => Array()
);
$reps = Array();
$subs = Array();

for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++)
{
  
  $reps[] = "\"REPLACEME$i\"";
  $subs[] = $row["geojson"];

  $z = Array("type"=>"Feature", "id"=>$i, 
             "properties"=>Array(
                "sz" => $row["sz"]
              ),
             "geometry"=> "REPLACEME$i");
                         
  $ar["features"][] = $z;
}
echo str_replace($reps, $subs, json_encode($ar));
?>