<?php 
include("../../../config/settings.inc.php");
include("$rootpath/include/selectWidget.php");
$station = isset($_GET["station"]) ? $_GET["station"] : "";
$network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";

$sw = new selectWidget("60hilow.php?", "60hilow.php?network=$network&", $network );
$sw->set_networks("ALL");
$sw->logic($_GET);


$TITLE = "IEM | Last 60 days High Low";
include("$rootpath/include/header.php");
?>


<P>Back to <a href="/plotting/index.php">Interactive Plotting</a>.


<?php
if (strlen($station) > 0 ) {

?>
<CENTER>
<BR><BR>
<P><a href="60hilow.php">Different Location</a>
<P>
<BR><BR>

<img src="60hilow_plot.php?station=<?php echo $station; ?>" ALT="Time Series">

</CENTER>

<BR>

<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has 
missing data.

<BR><BR>
<?php
} else {
 echo $sw->printInterface(); 
}
?>

<?php include("$rootpath/include/footer.php"); ?>
