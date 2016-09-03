<?php
header('Content-type: application/json');
/* Giveme JSON data listing products */
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";

$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'GMT'");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : die();
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : die();
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : die();
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : die();
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : die();

$query1 = "SELECT ST_xmax(u.geom) as x1, ST_xmin(u.geom) as x0, 
                  ST_ymin(u.geom) as y0, ST_ymax(u.geom) as y1, issue, expire
                  from warnings_$year w JOIN ugcs u on (u.gid = w.gid)
                  WHERE w.wfo = '$wfo' and 
                  phenomena = '$phenomena' and eventid = $eventid 
                  and significance = '$significance' LIMIT 1";
$result = pg_exec($connect, "SET TIME ZONE 'GMT'");
$result = pg_exec($connect, $query1);

$ar = Array("meta" => Array() );
for( $i=0; $z = @pg_fetch_assoc($result,$i); $i++)
{
  $z["id"] = $i +1;
  $z["issue"] = substr($z["issue"],0,16);
  $issue = strtotime($z["issue"]);
  if (date('i',$issue) % 5 != 0){
    $z["radarstart"] = date('Y-m-d H:i', $issue + ((5 - (date('i',$issue) % 5)) * 60));
  } else {
    $z["radarstart"] = date('Y-m-d H:i', $issue );
  }
  $z["expire"] = substr($z["expire"],0,16);
  $expire = strtotime($z["expire"]);
  if (date('i',$expire) % 5 != 0){
    $z["radarend"] = date('Y-m-d H:i', $expire - (((date('i',$expire) % 5)) * 60));
  } else {
    $z["radarend"] = date('Y-m-d H:i', $expire );
  }
  $ar["meta"][] = $z;
}

echo json_encode($ar);

?>
