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
	    <TR><TD>
<?php


$map = ms_newMapObj("../../data/gis/base26915.map");
$ll = $map->getlayerbyname("wmsback");
$ll->set("connection", "http://cairo.gis.iastate.edu/cgi-bin/server.cgi?format=jpeg&wmtver=1.0.0&request=map&servicename=GetMap&layers=".$type );
//$ll->set('connection', 'http://komodo.gis.iastate.edu/server.cgi?format=jpeg&wmtver=1.0.0&request=map&servicename=GetMap&layers='.$type);
$ll->set("status", MS_ON);

$site = $map->getlayerbyname("dot");
$site->set("status", MS_ON);

$rect = $map->getlayerbyname("rect");
$rect->set("status", MS_ON);

include("$rootpath/include/dbloc.php");
$loc = dbloc26915(iemdb("mesosite"), $station);


$incr = 500;
$ll_x = $loc["x"] - (100+($zoom*$incr));
$ll_y = $loc["y"] - (100+($zoom*$incr));
$ur_x = $loc["x"] + (100+($zoom*$incr));
$ur_y = $loc["y"] + (100+($zoom*$incr));

$map->setextent($ll_x, $ll_y, $ur_x, $ur_y);
$img = $map->prepareImage();

$ll->draw($img);

$pt = ms_newPointObj();
$pt->setXY($loc["x"], $loc["y"], 0);
$pt->draw($map, $site, $img, 0, "  ");
$pt->free();

/**
$rt = ms_newRectObj();
$rt->setextent($r0->x, $r0->y, $r1->x, $r1->y);
$rt->draw($map, $rect, $img, 0, " ");
$rt->free();
*/

//$counties->draw($img);
//$site->draw($img);

$img2 = $map->drawScaleBar();
$map->drawLabelCache($img);

$url = $img->saveWebImage();
$url2 = $img2->saveWebImage();
?>
<img src="<?php echo $url; ?>" border="1">
<img src="<?php echo $url2; ?>" border="1">
</TD></TR>
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
