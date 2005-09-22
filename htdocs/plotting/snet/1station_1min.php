<?php 
 include('../../schoolnet/switchtv.php'); 
 include("/mesonet/php/lib/selectWidget.php");

$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");

 $sw = new selectWidget("/plotting/snet/1station_1min.php", "/plotting/snet/1station_1min.php?tv=KCCI", strtoupper($tv) );
 $sw->logic($_GET);

 $station = $_GET['station'];
?>

<?php 
	$TITLE = "IEM | 1 Minute Time Series";
include("/mesonet/php/include/header.php"); 
	include("../../include/forms.php"); 
?>
<?php include("/mesonet/php/include/imagemaps.php"); ?>

<div class="text">
<b>Nav:</b> <a href="/schoolnet/">School Network</a> <b> > </b>
<a href="/plotting/snet/">Interactive Plotting</a> <b> > </b>
One minute time series


<p>You can plot 1 minute data for a school net location of your
choice.  Note that the archive begins 12 Feb 2002.</p>

<div align="center">
<table width="100%">
<tr><td>


<form method="GET" action="1station_1min.php">
<input type="hidden" name="ntv" value="<?php echo $tv; ?>"> 
  <?php
    echo " <a href=\"1station_1min.php\">Select Visually</a><br> \n";
    echo "Make plot selections: ";
    echo networkSelect($tv, $station); 

  ?>
   <?php yearSelect2(2002, $year, "year"); ?>

  <select name="month">
    <option value="01" <?php if ($month == "01") echo "SELECTED"; ?> >January
    <option value="02" <?php if ($month == "02") echo "SELECTED"; ?> >February
    <option value="03" <?php if ($month == "03") echo "SELECTED"; ?> >March
    <option value="04" <?php if ($month == "04") echo "SELECTED"; ?> >April
    <option value="05" <?php if ($month == "05") echo "SELECTED"; ?> >May
    <option value="06" <?php if ($month == "06") echo "SELECTED"; ?> >June
    <option value="07" <?php if ($month == "07") echo "SELECTED"; ?> >July
    <option value="08" <?php if ($month == "08") echo "SELECTED"; ?> >August
    <option value="09" <?php if ($month == "09") echo "SELECTED"; ?> >September
    <option value="10" <?php if ($month == "10") echo "SELECTED"; ?> >October
    <option value="11" <?php if ($month == "11") echo "SELECTED"; ?> >November
    <option value="12" <?php if ($month == "12") echo "SELECTED"; ?> >December
  </select>

  <select name="day">
<?php
  for ($k=1;$k<32;$k++){
   echo "<option value=\"".$k."\" ";
   if ($k == (int)$day){
     echo "SELECTED";
   }
   echo ">".$k."\n";
  }
?>
  </select>

  <input type="submit" value="Make Plot"></form>

<?php
if (strlen($station) > 0 ) {

?>

</td></tr><tr><td>

<a href="download.php?year=<?php echo $year; ?>&month=<?php echo $month; ?>&day=<?php echo $day; ?>&station=<?php echo $station; ?>">Download</a> this data.
<a href="dataformat.php">Explanation</a> of downloaded data format.

<BR><BR>

<?php include("1minute.php"); ?>

<!--
<img src="http://mesonet.agron.iastate.edu/plotting/snet/1min.php?year=<?php echo $year; ?>&month=<?php echo $month; ?>&day=<?php echo $day; ?>&station=<?php echo $station; ?>" ALT="Time Series">
<BR>
<img src="http://mesonet.agron.iastate.edu/plotting/snet/1min_V.php?year=<?php echo $year; ?>&month=<?php echo $month; ?>&day=<?php echo $day; ?>&station=<?php echo $station; ?>" ALT="Time Series">

<br>
<img src="http://mesonet.agron.iastate.edu/plotting/snet/1min_P.php?year=<?php echo $year; ?>&month=<?php echo $month; ?>&day=<?php echo $day; ?>&station=<?php echo $station; ?>" ALT="Time Series">
-->


<p><b>Note:</b> The wind speeds are indicated every minute by the red line. 
The blue dots represent wind direction and are shown every 10 minutes.</p>


<?php
} else {
?>

<p>or select from this map...<p>

<?php 
 $link = '1station_1min.php';
 include('../../schoolnet/switchbar.php'); ?>

<div align="center">

<?php 
    echo $sw->printInterface();
}
?>

</div>

</td></tr></table>
</td></tr></table>
</td></tr></table>
</td></tr></table>
</div>

<br><br></div>

<?php include("/mesonet/php/include/footer.php"); ?>
