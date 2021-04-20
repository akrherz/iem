<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "setup.php";
require_once "../../include/myview.php";

$t = new MyView();
$t->title = "Site Neighbors";
$t->sites_current="neighbors"; 

function neighbors($station,$lat,$lon){
   $con = iemdb("mesosite");
   $rs = pg_prepare($con, "_SELECT", "SELECT *,
         ST_distance(ST_transform(geom,3857), 
                     ST_transform(ST_GeomFromEWKT('SRID=4326;POINT(".$lon." ".$lat.")'), 3857)) /1000.0 as dist from stations 
         WHERE ST_PointInsideCircle(geom, ".$lon.", ".$lat.", 0.25) 
         and id != $1 ORDER by dist ASC");
   $result = pg_execute($con, "_SELECT", Array($station) );
 
   $s = "<table class=\"table table-striped\">
   <thead><tr><th>Distance [km]</th><th>Network</th><th>Station Name</th></tr></thead>";
   for( $i=0; $row = pg_fetch_assoc($result); $i++) {
      $s .= sprintf("<tr><td>%.3f</td><td><a href=\"locate.php?network=%s\">%s</a></td><td><a href=\"site.php?station=%s&network=%s\">%s</a></td></tr>", 
      $row["dist"], $row["network"], $row["network"], $row["id"],  $row["network"], $row["name"]);
     }
   $s .= "</table>";
	return $s;
}

$n = neighbors($station,$metadata["lat"],$metadata["lon"]);
$t->content = <<<EOF
<h3>Neighboring Stations</h3>
<p>The following is a list of IEM tracked stations within roughly a 0.25 degree
radius circle from the station location. Click on the site name for more information.</p>

{$n}
EOF;
$t->render('sites.phtml');
?>
