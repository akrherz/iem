<?php 
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("setup.php");

include("../../include/myview.php");
$t = new MyView();
$t->thispage="iem-sites";
$t->title = "Site Neighbors";
$t->sites_current="neighbors"; 

function neighbors($station,$lat,$lon){
   $con = iemdb("mesosite");
   $rs = pg_prepare($con, "_SELECT", "SELECT *,
         ST_distance(ST_transform(geom,3857), 
                     ST_transform(ST_GeomFromEWKT('SRID=4326;POINT(".$lon." ".$lat.")'), 3857)) /1000.0 as dist from stations 
         WHERE ST_point_inside_circle(geom, ".$lon.", ".$lat.", 0.25) 
         and id != $1 ORDER by dist ASC");
   $result = pg_execute($con, "_SELECT", Array($station) );
 
   $s = "<table class=\"table table-striped\">
   <thead><tr><th>Distance [km]</th><th>Network</th><th>Station Name</th></tr></thead>";
   for( $i=0; $row = @pg_fetch_assoc($result,$i); $i++) {
      $s .= sprintf("<tr><td>%.3f</td><td><a href=\"locate.php?network=%s\">%s</a></td><td><a href=\"site.php?station=%s&network=%s\">%s</a></td></tr>", 
      $row["dist"], $row["network"], $row["network"], $row["id"],  $row["network"], $row["name"]);
     }
   $s .= "</table>";
	return $s;
}

$n = neighbors($station,$metadata["lat"],$metadata["lon"]);
$t->content = <<<EOF
<h3 class="subtitle">Neighboring Stations</h3>
<p>The following is a list of IEM tracked stations within roughly 25 kilometers
from the site. Click on the site name for more information.</p>

{$n}
EOF;
$t->render('sites.phtml');
?>
