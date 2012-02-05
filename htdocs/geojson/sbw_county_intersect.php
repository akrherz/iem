<?php
/* Sucks to render a KML */
require_once 'Zend/Json.php';
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connect = iemdb("postgis");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";

$rs = pg_prepare($connect, "SELECT", "select ST_asGeoJson(setsrid(a,4326)) as geojson,
      length(transform(a,2163)) as sz
      from (
select 
   intersection(
      buffer(exteriorring(geometryn(multi(ST_union(n.geom)),1)),0.02),
      exteriorring(geometryn(multi(ST_union(w.geom)),1))
   ) as a
   from warnings_$year w, nws_ugc n WHERE gtype = 'P' and w.wfo = '$wfo'
   and phenomena = '$phenomena' and eventid = $eventid 
   and significance = '$significance'
   and n.polygon_class = 'C' and ST_OverLaps(n.geom, w.geom)
   and n.ugc IN (
          SELECT ugc from warnings_$year WHERE
          gtype = 'C' and wfo = '$wfo' 
          and phenomena = '$phenomena' and eventid = $eventid 
          and significance = '$significance'
       )
   and isvalid(w.geom) and isvalid(n.geom)
) as foo 
      WHERE not isempty(a)");

$rs = pg_execute($connect, "SELECT", 
                     Array() );

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
  
  $reps[] = "\"REPLACEME$i\"";
  $subs[] = $row["geojson"];

  $z = Array("type"=>"Feature", "id"=>$i, 
             "properties"=>Array(
                "sz" => $row["sz"]
              ),
             "geometry"=> "REPLACEME$i");
                         
  $ar["features"][] = $z;
}
echo str_replace($reps, $subs, Zend_Json::encode($ar));
?>
