<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

   $current="neighbors";
   $TITLE = "IEM | Current Data";
   include("$rootpath/include/header.php");  
   include("$rootpath/include/nav_site.php");

   $elevation=$row["elevation"];

   function elev_check($elevation){

     if ($elevation=="341"){
       $elevation="Unknown";
     }

     return $elevation;

   }

   function neighbors($stations,$lat,$lon){
     $con = iemdb("mesosite");
     $sqlStr = "SELECT * from stations WHERE point_inside_circle(geom, ".$lon.", ".$lat.", 0.25) and id != '$stations'";
     $result = pg_exec($con, $sqlStr);
     pg_close($con);
 
     for( $i=0; $row = @pg_fetch_array($result,$i); $i++) {
        if ($stations!=$row["id"]){
          echo '<a class="llink" href="/sites/site.php?id='.$row["id"].'">'
                .$row["name"].' - '.$row["network"].'</a><br />';
        }
     }
   }

  $interval = 0.25;
  $lat0 = $row["latitude"] - $interval;
  $lat1 = $row["latitude"] + $interval;
  $lon0 = $row["longitude"] - $interval;
  $lon1 = $row["longitude"] + $interval;
  $imgbase = "/cgi-bin/mapserv/mapserv?imgbox=-1+-1+-1+-1&imgxy=99.5+99.5&imgext=".$lon0."+".$lat0."+".$lon1."+".$lat1."&map=$rootpath/htdocs%2FGIS%2Fapps%2Fsmap0%2Fstations.map&zoom=1&layer=". $row["network"];
  $imgref = $imgbase ."&mode=map";
  $refref = $imgbase ."&mode=reference";


/**
 id        | character varying(6)  | 
 synop     | integer               | 
 name      | character varying(40) |  
 state     | character(2)          |  IA
 country   | character(2)          | 
 latitude  | real                  | 
 longitude | real                  | 
 elevation | real                  |  341 is unknown
 network   | character varying(20) | 
 online    | boolean               | 
 lat_dms   | character varying(10) | 
 lon_dms   | character varying(10) | 
**/

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
           <?php neighbors($station,$row["latitude"],$row["longitude"]); ?></TD></TR>
         </TABLE>
       </TD>
</TR>
</TABLE>
</div>
<?php include("$rootpath/include/footer.php"); ?>
