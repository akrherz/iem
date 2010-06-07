<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

$THISPAGE="iem-sites";
   $TITLE = "IEM | Site Neighbors";
   include("$rootpath/include/header.php");  
   $current="neighbors"; include('sidebar.php');


function neighbors($station,$lat,$lon){
   $con = iemdb("mesosite");
   $rs = pg_prepare($con, "_SELECT", "SELECT *,
         ST_distance(ST_transform(geom,2163), 
                     ST_transform(GeomFromText('SRID=4326;POINT(".$lon." ".$lat.")'), 2163)) /1000.0 as dist from stations 
         WHERE point_inside_circle(geom, ".$lon.", ".$lat.", 0.25) 
         and id != $1 ORDER by dist ASC");
   $result = pg_execute($con, "_SELECT", Array($station) );
 
   echo "<table cellpadding=\"3\" cellspacing=\"0\"><thead><tr><th>Distance [km]</th><th>Network</th><th>Station Name</th></tr></thead>";
   for( $i=0; $row = @pg_fetch_array($result,$i); $i++) {
      echo sprintf("<tr><td>%.3f</td><td>%s</td><td><a href=\"site.php?station=%s&network=%s\">%s</a></td></tr>", 
      $row["dist"], $row["network"], $row["id"], $row["network"], $row["name"]);
     }
   echo "</table>";
   }

?>
<h3 class="subtitle">Neighboring Stations</h3>
<p>The following is a list of IEM tracked stations within roughly 25 kilometers
from the site.</p>

<?php neighbors($station,$metadata["lat"],$metadata["lon"]); ?>
<?php include("$rootpath/include/footer.php"); ?>
