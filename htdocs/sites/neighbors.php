<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

$THISPAGE="iem-sites";
   $TITLE = "IEM | Site Neighbors";
   include("$rootpath/include/header.php");  
   $current="neighbors"; include('sidebar.php');


   function neighbors($stations,$lat,$lon){
     $con = iemdb("mesosite");
     $sqlStr = "SELECT * from stations WHERE point_inside_circle(geom, ".$lon.", ".$lat.", 0.25) and id != '$stations'";
     $result = pg_exec($con, $sqlStr);
     pg_close($con);
 
     for( $i=0; $row = @pg_fetch_array($result,$i); $i++) {
        if ($stations!=$row["id"]){
          echo '<a class="llink" href="site.php?station='.$row["id"].'&network='.$row["network"].'">'
                .$row["name"].'</a> ('.$row["network"].' )<br />';
        }
     }
   }

  $interval = 0.25;
  $lat0 = $metadata["lat"] - $interval;
  $lat1 = $metadata["lat"] + $interval;
  $lon0 = $metadata["lon"] - $interval;
  $lon1 = $metadata["lon"] + $interval;
  $imgbase = $rootcgi."/mapserv/mapserv?imgbox=-1+-1+-1+-1&imgxy=99.5+99.5&imgext=".$lon0."+".$lat0."+".$lon1."+".$lat1."&map=$rootpath/htdocs%2FGIS%2Fapps%2Fsmap0%2Fstations.map&zoom=1&layer=". $network;
  $imgref = $imgbase ."&mode=map";
  $refref = $imgbase ."&mode=reference";

?><div class="text">
<TABLE>
<TR>
       <TD><img border="2" src="<?php echo $imgref; ?>" 
           ALT="County Map">
           <br /></TD>
       <TD valign="top" width="600px">
         <TABLE width="100%">
           <TR><TD>
           <h3 class="subtitle">Neighboring Stations</h3><br>
           <?php neighbors($station,$metadata["lat"],$metadata["lon"]); ?></TD></TR>
         </TABLE>
       </TD>
</TR>
</TABLE>
</div>
<?php include("$rootpath/include/footer.php"); ?>
