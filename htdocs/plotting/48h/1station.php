<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd"> 
<HTML>
<HEAD>
	<TITLE>IEM | 48 Hour Plotting</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/main.css">
</HEAD>

<?php 
	$title = "IEM | 48h Time Series";
	include("../../include/header.php"); 
?>

<TR>

<?php include("../../include/side.html"); ?>
<?php include("../../include/imagemaps.php"); ?>

<TD width="450" valign="top">
<P>Back to <a href="/plotting/index.php">Interactive Plotting</a>.


<?php
if (strlen($station) > 0 ) {

?>


<CENTER>
<P><a href="1station.php">Different ASOS/AWOS Location</a>
<P><a href="1station.php?rwis=yes">Different RWIS Location</a
<P>

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
} elseif ( strlen($rwis) > 0) {
?>
<P><a href="1station.php">Different ASOS/AWOS Location</a>
<BR><BR>

<?php
	echo print_rwis("1station.php?station");

}else {
?>

<P>Switch to<a href="1station.php?rwis=yes">RWIS</a> stations.



<?php 
 print_asos("1station.php?station");
}
?>



</TD></TR>

<?php include("../../include/footer.html"); ?>
