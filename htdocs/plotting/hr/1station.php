<?php
include("../../../config/settings.inc.php");
 include("$rootpath/include/selectWidget.php");
 $network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";

 $sw = new selectWidget("/plotting/hr/1station.php", "/plotting/hr/1station.php?", $network);
 $swf = Array("network" => $network);
 $sw->setformvars($swf);
 $sw->logic($_GET);
 $swinterface = $sw->printInterface();


 $station = $_GET['station'];
?>

<?php 
	$TITLE = "IEM | Time Series";
include("$rootpath/include/header.php"); 
?>
<?php include("$rootpath/include/imagemaps.php"); ?>
<b>Nav:</b> <a href="/plotting/">Interactive Plotting</a> <b> > </b>
One station time series

<br><br>
<div class="text">
<table width="100%">
<tr><td>

<?php
if (strlen($station) > 0 ) {

?>

  <form method="GET" action="1station.php">
  <?php
  if ( strlen($station) == 4 ) {
    echo "<b>Options:</b><a href=\"1station.php\">Switch to ASOS/AWOS</a> \n";
    echo " <b>|</b> <a href=\"1station.php\">Select Visually</a><br> \n";
    echo rwisSelect($station); 
  } else {
    echo "<b>Options:</b> <a href=\"1station.php?rwis=yes\">Switch to RWIS</a> \n";
    echo " <b>|</b> <a href=\"1station.php\">Select Visually</a><br> \n";
    echo asosSelect($station);
  }
  ?>
  <select name="hours">
    <option value="24" <?php if ($hours == "24") echo "SELECTED"; ?>>24 hours
    <option value="48" <?php if ($hours == "48") echo "SELECTED"; ?>>48 hours
    <option value="72" <?php if ($hours == "72") echo "SELECTED"; ?>>72 hours
    <option value="96" <?php if ($hours == "96") echo "SELECTED"; ?>>96 hours
  </select>
  <input type="submit" value="Make Plot"></form>

</td></tr><tr bgcolor="#b2dfee"><td>

<BR><BR>


<img src="1temps.php?hours=<?php echo $hours; ?>&station=<?php echo $station; ?>" ALT="Time Series">
<BR>
<img src="winds.php?hours=<?php echo $hours; ?>&station=<?php echo $station; ?>" ALT="Time Series">
</CENTER>

<BR>

<P>Data only valid within the past <?php echo $hours; ?> hours is displayed on this chart.

<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has 
missing data.

<BR><BR>
<?php } else { ?>
<b>Switch Network:</b> <a href="1station.php?network=IA_ASOS">Iowa ASOS</a>,
<a href="1station.php?network=AWOS">Iowa AWOS</a>,
<a href="1station.php?network=IA_RWIS">Iowa RWIS</a>.

<p><?php echo $swinterface; ?>
<?php } ?>

</td></tr></table>

<br><br></div>

<?php include("$rootpath/include/footer.php"); ?>
