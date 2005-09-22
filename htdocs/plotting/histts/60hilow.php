<?php 
	$TITLE = "IEM | Last 60 days High Low";
include("/mesonet/php/include/header.php"); 
?>

<?php include("../../include/imagemaps.php"); ?>

<div class="text">
<P>Back to <a href="/plotting/index.php">Interactive Plotting</a>.


<?php
if (strlen($station) > 0 ) {

?>


<CENTER>
<BR><BR>
<P><a href="60hilow.php">Different ASOS/AWOS Location</a>
<P><a href="60hilow.php?rwis=yes">Different RWIS Location</a
<P>
<BR><BR>

<img src="60hilow_plot.php?station=<?php echo $station; ?>" ALT="Time Series">

</CENTER>

<BR>

<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has 
missing data.

<BR><BR>
<?php
} elseif ( strlen($rwis) > 0) {
?>

<P><a href="60hilow.php">Different ASOS/AWOS Location</a>

<?php
	echo print_rwis("60hilow.php?station");

}else {
?>

<P>Switch to<a href="60hilow.php?rwis=yes">RWIS</a> stations.


<?php 
	echo print_asos("60hilow.php?station");

	}
?>
</div>

<?php include("/mesonet/php/include/footer.php"); ?>
