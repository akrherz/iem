<?php
 $TITLE = "IEM | 48 Hour Comparison";
include("/mesonet/php/include/header.php"); 
 include("../../include/imagemaps.php");
?>

<b>Nav:</b> <a href="/plotting/index.php">Interactive Plotting</a>.

<div class="text">
<p>This program will create a side-by-side plot of an atmospheric variable for
two stations.  Please make the necessary selections in order for the plot to work.  If you 
receive a broken image symbol, data is missing for your station locations.

<CENTER>
<TABLE border="0">
<TR>
	<TH bgcolor="#EEEEEE">Select Locations Either:</TH>
	<TD><a href="2compare.php">Graphically</a></TD>
	<TD> or <a href="2compare.php?graph=text">Textual</a></TD>
</TR></TABLE>
</CENTER>


<?php
if ( strlen($graph) > 0 ) { ?>

<H3>Textual Selection:</H3>

<FORM METHOD="GET" action="2compare.php">
<P>Enter station 1: <INPUT TYPE="TEXT" NAME="station1" value="<?= $station1 ?>">
<P>Enter station 2: <INPUT TYPE="TEXT" NAME="station2" value="<?= $station2 ?>">

<P>Data Plotted: <SELECT name="data">
<option value="tmpf">Temperature
<option value="dwpf">Dewpoint
<option value="sknt">Wind Speed (knots)
<option value="drct">Wind Direction
<option value="alti">Altimeter
</SELECT>

<P><INPUT TYPE="SUBMIT" VALUE="Make Map">

</FORM>

<?php
// We have a good Request
} elseif (strlen($station1) > 0 && strlen($station2) > 0 && strlen($data) > 0) {
?>

<FORM METHOD="GET" action="2compare.php" name="compare">
<P>Enter station 1: <INPUT size=5 TYPE="TEXT" NAME="station1" value="<?= $station1 ?>">
<P>Enter station 2: <INPUT size=5 TYPE="TEXT" NAME="station2" value="<?= $station2 ?>">

<P>Data Plotted: <SELECT name="data">
<option value="tmpf" <? if ($data == "tmpf") echo "SELECTED"; ?>>Temperature
<option value="dwpf" <? if ($data == "dwpf") echo "SELECTED"; ?>>Dewpoint
<option value="sknt" <? if ($data == "sknt") echo "SELECTED"; ?>>Wind Speed (knots)
<option value="drct" <? if ($data == "drct") echo "SELECTED"; ?>>Wind Direction
<option value="alti" <? if ($data == "alti") echo "SELECTED"; ?>>Altimeter
</SELECT>

<P><INPUT TYPE="SUBMIT" VALUE="Build Comparison">

</form>

<br><img src="2temps.php?station1=<?= $station1 ?>&station2=<?= $station2 ?>&data=<?= $data ?>" ALT="Time Series">

 
<P>Data only valid within the past 48 hours is displayed on this chart.
 
<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has
missing data. 
 
<BR><BR> 


<?php
} elseif (strlen($station1) > 0 && strlen($station2) > 0 && strlen($data) == 0) {

?>

<FORM METHOD="GET" action="2compare.php">
<P>Enter station 1: <INPUT TYPE="TEXT" NAME="station1" value="<?= $station1 ?>">
<P>Enter station 2: <INPUT TYPE="TEXT" NAME="station2" value="<?= $station2 ?>">

<P>Data Plotted: <SELECT name="data">
<option value="tmpf">Temperature
<option value="dwpf">Dewpoint
<option value="sknt">Wind Speed (knots)
<option value="drct">Wind Direction
<option value="alti">Altimeter
</SELECT>

<P><INPUT TYPE="SUBMIT" VALUE="Make Map">



<?php
} elseif ( strlen($station1) > 0 && strlen($station2) == 0 ) {
?>
<ul>
	<li>First Station: <?= $station1 ?> &nbsp; <a href="2compare.php">Change</a></li>
</ul>

<P>Please select second station
<BR>

	<?php  if ($rwis == "yes") {
		?> <P>Switch to <a href="2compare.php?station1=<?= $station1 ?>">ASOS</a><BR> <?php
		echo print_rwis("2compare.php?station1=". $station1 ."&station2");

	} else {

		?> <P>Switch to <a href="2compare.php?station1=<?= $station1 ?>&rwis=yes">RWIS</a><BR> <?php
		echo print_asos("2compare.php?station1=". $station1 ."&station2");
	}

} else {
?>

 <?php  if ($rwis == "yes") {
                ?> <P>Switch to <a href="2compare.php">ASOS</a><BR> <?php
                echo print_rwis("2compare.php?station1");
 
        } else {

                ?> <P>Switch to <a href="2compare.php?rwis=yes">RWIS</a><BR> <?php
                echo print_asos("2compare.php?station1");
        }
}
?>
</div>

<?php include("/mesonet/php/include/footer.php"); ?>
