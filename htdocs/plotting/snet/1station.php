<?php 
include("../../../config/settings.inc.php");
	$TITLE = "IEM | 24 Hour Plotting";
include("$rootpath/include/header.php"); 
?>

<h3 class="heading">Resource Moved</h3>

<p>The 20 minute interval plots have been depreciated.  Please use the 
1 minute interval plotter found here:

<p><a href="<?php echo $rooturl; ?>/plotting/snet/1station_1min.php"><?php echo $rooturl; ?>/plotting/snet/1station_1min.php</a>

<?php include("$rootpath/include/footer.php"); ?>
