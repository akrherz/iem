<?php 
	$TITLE = "IEM | 24 Hour Plotting";
include("/mesonet/php/include/header.php"); 
?>

<h3 class="heading">Plot Time Series</h3>

<div class="text">
<?php include("../../include/imagemaps.php"); ?>


<?php
if (strlen($station) > 0 ) {

?>

<CENTER>
<P><a href="1station.php">Different Location</a>
<P>
<BR><BR>

<img src="1temps.php?station=<?php echo $station; ?>" ALT="Time Series">
<BR>
<img src="winds.php?station=<?php echo $station; ?>" ALT="Time Series">
</CENTER>

<BR>

<P>Data only valid within the past 24 hours is displayed on this chart.

<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has 
missing data.

<BR><BR>

<?php

}else {
?>

<br>
<div align="center">
<?php 
	echo print_snet("1station.php?station");

	}
?>
</div>
<br><br>


<?php include("/mesonet/php/include/footer.php"); ?>
