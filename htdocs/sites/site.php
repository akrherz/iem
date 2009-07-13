<?php 

include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");
$THISPAGE="iem-sites";
$TITLE = "IEM | Site Information";
include("$rootpath/include/header.php");
?>
<h3 class="heading">IEM Site Information</h3><p>
<?php $current = "base"; include("sidebar.php"); ?>

<div style="float: left;">

<?php include("make_maps.php"); ?>

<table>
<tr><th>Station Identifier:</th><td><?php echo $station; ?></td></tr>
<tr><th>Network:</th><td><?php echo $network; ?></td></tr>
<tr><th>County:</th><td><?php echo $cities[$station]["county"]; ?></td></tr>
<tr><th>Latitude:</th><td><?php echo sprintf("%.5f", $cities[$station]["latitude"]); ?></td></tr>
<tr><th>Longitude:</th><td><?php echo sprintf("%.5f", $cities[$station]["longitude"]); ?></td></tr>
<tr><th>Elevation [m]:</th><td><?php echo $cities[$station]["elevation"]; ?></td></tr>

</table>

</div>

<?php include("$rootpath/include/footer.php"); ?>
