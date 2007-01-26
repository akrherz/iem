<?php
 include("../../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 include("$rootpath/include/selectWidget.php");
 $network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";

 $sw = new selectWidget("$rooturl/sites/locate.php", "$rooturl/sites/site.php?", $network);
 $swf = Array("network" => $network);
 $sw->setformvars($swf);
 $sw->logic($_GET);
 $ar = Array("IA_ASOS", "AWOS", "IA_RWIS", "KELO", "KCCI", "KIMT","SD_ASOS", "MN_ASOS", "WI_ASOS", "IL_ASOS", "MO_ASOS", "KS_ASOS", "NE_ASOS");
 $sw->set_networks($ar);
 $swinterface = $sw->printInterface();
?>
<?php
$TITLE = "IEM | Site Locator";
include("$rootpath/include/header.php"); 
  include("$rootpath/include/imagemaps.php");
    ?>

<h3 class="heading">IEM Site Information</h3><p>
<div class="text">
The IEM site selector allows the user to obtain a details of a given site through selection of the
site visually through maps of the various station types.  Once a site is selected, the user has 
access to a site description, current conditions, parameters measured at the site, site neighbors,
and site photos.<br /><br /></p>


<div align="center">

<?php echo $swinterface; ?>

</div>
<br /><br /></div>

<?php include("$rootpath/include/footer.php"); ?>
