<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/forms.php");
include("setup.php");
$THISPAGE="iem-sites";
 $TITLE = "IEM | Sites";
 include("$rootpath/include/header.php");

 $current="meteo"; include("sidebar.php"); 
?>
 <br /><img src="<?php echo sprintf("meteo_temps.php?network=%s&station=%s",   $network, $station); ?>">
</div>
<?php include("$rootpath/include/footer.php"); ?>
