<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd"> 
<HTML>
<HEAD>
	<TITLE>IEM | 24 Hour Plotting</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/main.css">
</HEAD>

<?php 
	$title = "IEM | 24h Time Series";
	include("../../include/header.php"); 
?>

<TR>

<?php include("../../include/side.html"); ?>

<TD width="450" valign="top">
<P>Back to <a href="/plotting/index.php">Interactive Plotting</a>.


<?php
if (strlen($station1) > 0 && strlen($station2) > 0 ) {

?>


<CENTER>
<BR><BR>

<ul>
	<li>First Station: <?= $station1 ?> &nbsp; <a href="2station.php?$station1=<?= $station2 ?>">Change</a></li>
	<li>Second Station: <?= $station2 ?> &nbsp; <a href="2station.php?$station1=<?= $station1 ?>">Change</a></li>
</ul>

<P><a href="2station.php">Start Over</a>
<P>
<BR><BR>

<img src="2temps.php?station1=<?= $station1 ?>&station2=<?= $station2 ?>&data=<?= $data ?>" ALT="Time Series">
</CENTER>

<BR>

<P>Data only valid within the past 24 hours is displayed on this chart.

<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has 
missing data.

<BR><BR>



<?php
} else {
?>

<P>I am still working on the graphical selection interface for this.  Enter the IDs if you know them...

<FORM METHOD="GET" action="2station.php">
<P>Enter station 1: <INPUT TYPE="TEXT" NAME="station1" value="<?= $station1 ?>">
<P>Enter station 2: <INPUT TYPE="TEXT" NAME="station2" value="<?= $station2 ?>">

<P>Data Plotted: <SELECT name="data">
<option value="tmpf">Temperature
<option value="dwpf">Dewpoint
<option value="sknt">Wind Speed (knots)
</SELECT>

<P><INPUT TYPE="SUBMIT" VALUE="Make Map">

</FORM>

<?php	
	}
?>



</TD></TR>

<?php include("../../include/footer.html"); ?>
