<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

   $current="sites";
   $TITLE = "IEM | Current Data";
   include("$rootpath/include/header.php");
   include("$rootpath/include/nav_site.php");

   $elevation=$row["elevation"];

   function getcounty($station){
     $con = iemdb("mesosite");
     $sqlStr = "SELECT county as countyname from stations
               WHERE id = '".$station."' ";
     $result = pg_exec($con, $sqlStr);
     pg_close($con);
     $row = @pg_fetch_array($result,0);

     return $row["countyname"];

   }


   function eval_network($network){
 
     if ($network == "KCCI")
      {
       $new_network = "KCCI SchoolNet";
      }
     else $new_network = $network;

     return $new_network;

   }

   function elev_check($elevation){

     if ($elevation=="341"){
       $elevation="Unknown";
     }

     return $elevation;

   }

   function neighbors($stations,$lat,$lon){
     $con =  iemdb("mesosite");
     $sqlStr = "SELECT * from sites WHERE 
               point_inside_circle(geom, ".$lon.", ".$lat.", 0.25)";
     $result = pg_exec($con, $sqlStr);
     pg_close($con);
 
     for( $i=0; $row = @pg_fetch_array($result,$i); $i++) {
        if ($stations!=$row["id"]){
          echo '<a class="llink" href="/sites/site.php?station='.$row["id"].'">'
                .$row["name"].' - '.$row["network"].'</a><br />';
        }
     }
   }

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

  $interval = 0.25;
  $lat0 = $row["latitude"] - $interval;
  $lat1 = $row["latitude"] + $interval;
  $lon0 = $row["longitude"] - $interval;
  $lon1 = $row["longitude"] + $interval;
  $imgbase = "$rootcgi/cgi-bin/mapserv/mapserv?imgbox=-1+-1+-1+-1&imgxy=99.5+99.5&imgext=".$lon0."+".$lat0."+".$lon1."+".$lat1."&map=$rootpath/htdocs/GIS%2Fapps%2Fsmap0%2Fstations.map&zoom=1&layer=". $row["network"];
  $imgref = $imgbase ."&mode=map";
  $refref = $imgbase ."&mode=reference";

?>
<br>
         <TABLE border="0">
           <TR><TD valign="top">
            <img border="2" src="<?php echo $imgref; ?>" ALT="County Map"></TD>
            <TD>
	    </td></tr>
               <TR><TD class="subtitle"><b>Station ID</b></TD><TD><?php echo $station ?></TD></TR>
               <TR><TD class="subtitle"><b>Network</b></TD><TD>
                   <a href="http://www.mesonet.agron.iastate.edu/<?php echo $row["network"]; ?>/"><?php echo eval_network($row["network"]); ?></a></TD></TR>
               <TR><TD class="subtitle"><b>County</b></TD><TD><?php echo getcounty($row["id"]);?></TD></TR>
               <TR><TD class="subtitle"><b>Lat, Lon</b></TD><TD><?php echo round( $row["latitude"], 4) ." , ". round($row["longitude"], 4) ; ?></TD></TR>
               <TR><TD class="subtitle"><b>Elevation [m]</b></TD><TD><?php echo elev_check($elevation);?>
            </TD></TR>
         </TABLE>

<?php include("$rootpath/include/footer.php"); ?>
