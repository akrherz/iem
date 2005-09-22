<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd"> 
<HTML>
<HEAD>
	<TITLE>IEM | 24 Hour Difference Plots</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>

<?php 
	$title = "IEM | 24h Difference Plots";
	include("../../include/header2.php"); 
	include("../../include/imagemaps.php");
?>

<P>Back to <a href="/plotting/index.php">Interactive Plotting</a>.

<blockquote> This program will create a difference plot between two stations.
The variable for station2 will be substracted from station1. So a positive value
means that station1's value is higher.</blockquote>

<CENTER>
<TABLE border="0">
<TR>
	<TH bgcolor="#EEEEEE">Select Locations Either:</TH>
	<TD><a href="2diff.php">Graphically</a></TD>
	<TD> or <a href="2diff.php?graph=text">Textual</a></TD>
</TR></TABLE>
</CENTER>


<?php
if ( strlen($graph) > 0 ) { ?>

<H3>Textual Selection:</H3>

<FORM METHOD="GET" action="2diff.php">
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
// We have a good Request
} elseif (strlen($station1) > 0 && strlen($station2) > 0 && strlen($data) > 0) {
?>

<ul>
        <li>First Station: <?= $station1 ?> &nbsp; <a href="2diff.php?station1=<?= $station2 ?>">Change</a></li>
        <li>Second Station: <?= $station2 ?> &nbsp; <a href="2diff.php?station1=<?= $station1 ?>">Change</a></li>
</ul>

<P><a href="2diff.php">Start Over</a>
<P>
<BR><BR>

<img src="2diff_plot.php?station1=<?= $station1 ?>&station2=<?= $station2 ?>&data=<?= $data ?>" ALT="Time Series">
</CENTER>

<BR>
 
<P>Data only valid within the past 24 hours is displayed on this chart.
 
<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has
missing data. 
 
<BR><BR> 


<?php
} elseif (strlen($station1) > 0 && strlen($station2) > 0 && strlen($data) == 0) {

?>

<FORM METHOD="GET" action="2diff.php">
<P>Enter station 1: <INPUT TYPE="TEXT" NAME="station1" value="<?= $station1 ?>">
<P>Enter station 2: <INPUT TYPE="TEXT" NAME="station2" value="<?= $station2 ?>">

<P>Data Plotted: <SELECT name="data">
<option value="tmpf">Temperature
<option value="dwpf">Dewpoint
<option value="sknt">Wind Speed (knots)
</SELECT>

<P><INPUT TYPE="SUBMIT" VALUE="Make Map">



<?php
} elseif ( strlen($station1) > 0 && strlen($station2) == 0 ) {
?>
<ul>
	<li>First Station: <?= $station1 ?> &nbsp; <a href="2diff.php">Change</a></li>
</ul>

<P>Please select second station
<BR>

	<?php  if ($rwis == "yes") {
		?> <P>Switch to <a href="2diff.php?station1=<?= $station1 ?>">ASOS</a><BR> <?php
		echo print_rwis("2diff.php?station1=". $station1 ."&station2");

	} else {

		?> <P>Switch to <a href="2diff.php?station1=<?= $station1 ?>&rwis=yes">RWIS</a><BR> <?php
		echo print_asos("2diff.php?station1=". $station1 ."&station2");
	}

} else {
?>

 <?php  if ($rwis == "yes") {
                ?> <P>Switch to <a href="2diff.php">ASOS</a><BR> <?php
                echo print_rwis("2diff.php?station1");
 
        } else {

                ?> <P>Switch to <a href="2diff.php?rwis=yes">RWIS</a><BR> <?php
                echo print_asos("2diff.php?station1");
        }
}
?>



<?php include("../../include/footer2.php"); ?>
