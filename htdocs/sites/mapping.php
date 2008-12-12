<?php 
include("setup.php");
$THISPAGE="iem-sites";
 $TITLE = "IEM | Site Location";
 include("../../config/settings.inc.php");
 include("$rootpath/include/header.php"); 
 include("$rootpath/include/mlib.php");
?>
<?php $current = "loc"; include("sidebar.php"); ?>
<?php
 $type = isset($_GET["type"]) ? $_GET["type"] : "doqqs";
 $zoom = isset($_GET["zoom"]) ? $_GET["zoom"] : 3;
 if ($zoom < 0) $zoom = 0;
 if ($zoom > 5) $zoom = 5; 

 $URL= "$rooturl/GIS/apps/ortho/site.php?station=${station}&zoom=${zoom}&type=${type}";
        $URL_BASE=$rooturl.'/sites/mapping.php?station='.$station.'&type='.$type;
echo '<form method="GET" action="mapping.php">
  <input type="hidden" name="station" value="'.$station.'">
  <input type="hidden" name="network" value="'.$network.'">
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
<?php include("$rootpath/include/footer.php"); ?>
