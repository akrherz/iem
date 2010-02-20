<?php
/* Giveme JSON data listing products */
require_once 'Zend/Json.php';
require_once '../..//config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";

$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'GMT'");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";


 $sql = "select round(sum(area(transform(geom,2163)) / 1000000.0)::numeric,0) as area, sumtxt( n.name || ' ['||n.state||'], ') as locations, eventid,
         min(issue) as issued, max(expire) as expired from
        (select distinct ugc, eventid, issue, expire from warnings_$year
         WHERE wfo = '$wfo' and gtype = 'C' and
         significance = '$significance' and phenomena = '$phenomena' and eventid is not null) as foo,
         nws_ugc n WHERE n.ugc = foo.ugc GROUP by eventid ORDER by eventid ASC";
if (($phenomena == "SV" || $phenomena == "TO" || $phenomena == "FF" || $phenomena == "MA") && $significance == "W"){

 $sql = "SELECT round(area::numeric,0) as area, locations, foo2.eventid, issued, expired FROM 
    (select sumtxt( n.name || ' ['||n.state||'], ') as locations, eventid,
     min(issue) as issued, max(expire) as expired from
      (select distinct ugc, eventid, issue, expire from warnings_$year
       WHERE wfo = '$wfo' and gtype = 'C' and
       significance = '$significance' and phenomena = '$phenomena' and eventid is not null) as foo,
   nws_ugc n WHERE n.ugc = foo.ugc GROUP by eventid ORDER by eventid ASC) as foo2, 

(select area(transform(geom,2163)) / 1000000.0 as area, eventid 
        from warnings_$year WHERE wfo = '$wfo' and gtype = 'P' and
       significance = '$significance' and phenomena = '$phenomena' and eventid is not null) as foo3  WHERE foo3.eventid = foo2.eventid";

}


$result = pg_exec($connect, $sql);

$ar = Array("products" => Array() );
for( $i=0; $z = @pg_fetch_array($result,$i); $i++)
{
  $z["id"] = $i +1;
  $z["phenomena"] = $phenomena;
  $z["significance"] = $significance;
  $z["wfo"] = $wfo;
  $z["year"] = $year;
  $z["issued"] = substr($z["issued"],0,16);
  $z["expired"] = substr($z["expired"],0,16);
  $ar["products"][] = $z;
}

echo Zend_Json::encode($ar);

?>
