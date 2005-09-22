<?php 
	$TITLE = "IEM | 1 Minute Time Series";
include("/mesonet/php/include/header.php"); 
?>
<?php include("../../include/imagemaps.php"); ?>
<?php include("../../include/forms.php"); ?>

<div class="text">
<b>Nav:</b> <a href="/AWOS/">AWOS Network</a> <b> > </b>
One minute time series

<p><b>Note:</b>The archive currently contains data from 1 Jan 1995 
till 31 August 2004.  Fort Dodge and Clinton were converted to ~ASOS, 
but are available for some times earlier in the archive.<p>

<table width="100%">
<tr><td>


  <form method="GET" action="1station_1min.php">
  <?php

    if (strlen($month) == 0 ){
	$month = date("m");
    }
    if (strlen($day) == 0 ){
        $day = date("d");
    }

  //  echo " <a href=\"1station_1min.php\">Select Visually</a><br> \n";
    echo "Make plot selections: <br>";
    echo awosSelect($station); 
 
   echo yearSelect(1995, $year, "year"); 
  ?>

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

<!--
<a href="download.php?year=<?php echo $year; ?>&month=<?php echo $month; ?>&day=<?php echo $day; ?>&station=<?php echo $station; ?>">Download</a> this data.
<a href="dataformat.php">Explanation</a> of downloaded data format.
-->

<BR><BR>

<img src="1min.php?year=<?php echo $year; ?>&month=<?php echo $month; ?>&day=<?php echo $day; ?>&station=<?php echo $station; ?>" ALT="Time Series">

<BR>
<img src="1min_V.php?year=<?php echo $year; ?>&month=<?php echo $month; ?>&day=<?php echo $day; ?>&station=<?php echo $station; ?>" ALT="Time Series">

<br>
<img src="1min_P.php?year=<?php echo $year; ?>&month=<?php echo $month; ?>&day=<?php echo $day; ?>&station=<?php echo $station; ?>" ALT="Time Series">


<p><b>Note:</b> The wind speeds are indicated every minute by the red line. 
The blue dots represent wind direction and are shown every 10 minutes.</p>


<?php
} else {
?>
<!--
<p>or select from this map...
-->

<?php 
//	echo print_awos("1station_1min.php?station");

}

?>


</td></tr></table>
</div>

<br><br>

<?php include("/mesonet/php/include/footer.php"); ?>
