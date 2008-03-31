<?php 
 include("../../../config/settings.inc.php");
 include('../../schoolnet/switchtv.php'); 
 include("$rootpath/include/selectWidget.php");
 include("$rootpath/include/forms.php");

$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");

 $sw = new selectWidget("$rooturl/plotting/snet/1station_1min.php", "$rooturl/plotting/snet/1station_1min.php?tv=$tv", strtoupper($tv) );
 $sw->setformvars( Array("tv" => $tv) );
 $sw->logic($_GET);
 $station = isset($_GET['station']) ? $_GET["station"]: "";

 include("$rootpath/include/imagemaps.php"); 
?>

<?php 
	$TITLE = "IEM | 1 Minute Time Series";
$THISPAGE = "networks-schoolnet"; include("$rootpath/include/header.php"); 
?>

<p>You can plot 1 minute data for a school net location of your
choice.  Note that the archive begins 12 Feb 2002.</p>


<form method="GET" action="1station_1min.php">
<input type="hidden" name="ntv" value="<?php echo $tv; ?>"> 
  <?php
    echo " <a href=\"1station_1min.php\">Select Visually</a><br> \n";
    echo "Make plot selections: ";
    echo networkSelect($tv, $station); 

  ?>
   <?php yearSelect2(2002, $year, "year"); ?>
 <?php echo monthSelect($month); ?>
 <?php daySelect($day); ?>

  <input type="submit" value="Make Plot"></form>

<?php
if (strlen($station) > 0 ) {

?>

<p>

<?php include("1minute.php"); ?>

<p><b>Note:</b> The wind speeds are indicated every minute by the red line. 
The blue dots represent wind direction and are shown every 10 minutes.</p>


<?php
} else {
?>

<p>or select from this map...<p>

<?php 
 $link = '1station_1min.php';
 include('../../schoolnet/switchbar.php'); ?>

<?php 
    echo $sw->printInterface();
}
?>


<?php include("$rootpath/include/footer.php"); ?>
