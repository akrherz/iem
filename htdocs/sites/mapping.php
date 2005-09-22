<?php 
include("setup.php");

        $current="maps";
	$TITLE = "IEM | Site Location";
	include("/mesonet/php/include/header.php"); 
        include("../include/nav_site.php");
        include("../include/getcurrent.php");
        include("../include/mlib.php");

        if (strlen($station) > 6 || strlen($station) == 0){
           $station = 'DSM';
	}

        if (strlen($type) == 0) $type= "doqqs";
        if (strlen($zoom) == 0) $zoom = 3;
        if ($zoom < 0) $zoom = 0;
        if ($zoom > 5) $zoom = 5; 

        $network=$row["network"];
        $URL='http://mesonet.agron.iastate.edu/GIS/apps/ortho/site.php?station='.$station.'&zoom='.$zoom.'&type='.$type;
        $URL_BASE='http://mesonet.agron.iastate.edu/sites/mapping.php?station='.$station.'&type='.$type;
?>
<?php
          echo '<form method="POST" action="mapping.php">
            <input type="hidden" name="station" value="'.$station.'">
            <input type="hidden" name="zoom" value="'.$zoom.'">
            <input type="hidden" name="type" value="'.$type.'">';
?>
<div class="text">
          <TABLE>
            <TR><TD colspan="2" align="left" class="subtitle"><b>Map Type:</b>
               <select name="type">
                 <option value="doqqs"<?php if ($type=="doqqs") echo " SELECTED"?>>Digital Ortho Quads 
                 <option value="drg100"<?php if ($type=="drg100") echo " SELECTED"?>>1:100,000 Topographic
                 <option value="cir"<?php if ($type=="cir") echo " SELECTED"?>>Color IR
               <option value="ortho_bw_2002"<?php if ($type=="ortho_bw_2002") echo " SELECTED"?>>Color IR (Grayscale)
               </select>
               <input type="submit" value="Change Image"></font>
            </TD></TR>
	    <TR><TD><h3 class="subtitle"><b><?php include($URL); ?></b></h3><br></TD></TR>
            <TR><TD colspan="2"><font class="subtitle"><b>Zoom
	    Level: (near)</b></font>
<?php
        for ($i = 0; $i <= 5; $i++) {
          if ($i == $zoom){
           echo '<font class="subtitle"><b>&nbsp;&nbsp;'.($i+1).'&nbsp;&nbsp;</b></font>';
          }
          else{
           echo '<font class="subtitle"><b>&nbsp;&nbsp;<a
	   href="'.$URL_BASE.'&zoom='.$i.'">'.($i+1).'</a>&nbsp;&nbsp;</b></font>';
          }
        }

?>
         <font class="subtitle"><b> (far)</b></font><p>
         </TD></TR>
         <TR><TD colspan="2"><br><b>Note:</b> While the white 
          dot marks the location of our latitude and longitude measurements, the actual 
          station location could be anywhere within the limits set by the white box. 
          Depending on the accuracy of the location measurements, it is feasible that 
          the actual station location is outside the box.<p>
         </TD></TR>
         <TR><TD colspan="2">Image Generation provided by
             <a href="http://ortho.gis.iastate.edu">Iowa State GIS lab</a></TD></TR>
         </TABLE></form>
        </TD>
</TR>
</TABLE></div>
<?php include("/mesonet/php/include/footer.php"); ?>
