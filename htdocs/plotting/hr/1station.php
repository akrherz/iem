<?php
include("../../../config/settings.inc.php");
 include("$rootpath/include/selectWidget.php");
 $network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";
 $hours = isset($_GET["hours"]) ? $_GET["hours"] : 24;

 $sw = new selectWidget("$rooturl/plotting/hr/1station.php", "$rooturl/plotting/hr/1station.php?network=$network&", $network);
 $sw->set_networks( Array("IA_ASOS","AWOS","IA_RWIS") );
 $sw->logic($_GET);
 $sw->setformvars( Array("network" => $network) );
 $swinterface = $sw->printInterface();


 $station = isset($_GET['station']) ? strtoupper( $_GET['station'] ): "";
?>

<?php 
	$TITLE = "IEM | Time Series";
include("$rootpath/include/header.php"); 
?>
<?php include("$rootpath/include/imagemaps.php"); ?>

<br><br>
<div class="text">
<table width="100%">
<tr><td>

<?php
if (strlen($station) > 0 ) {

?>

  <form method="GET" action="1station.php">
  <input name="station" value="<?php echo $station; ?>" type="hidden">
  <?php
    echo "<b>Options:</b>";
    echo " <b>|</b> <a href=\"1station.php?network=$network\">Select Visually</a><br> \n";
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
<br />
<img src="pres.php?hours=<?php echo $hours; ?>&station=<?php echo $station; ?>" ALT="Time Series">
</CENTER>

<BR>

<P>Data only valid within the past <?php echo $hours; ?> hours is displayed on this chart.

<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has 
missing data.

<BR><BR>
<?php } else { ?>

<p><?php echo $swinterface; ?>
<?php } ?>

</td></tr></table>

<br><br></div>

<?php include("$rootpath/include/footer.php"); ?>
