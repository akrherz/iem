<?php 
include("../../config/settings.inc.php");
include('switchtv.php');
$THISPAGE = 'networks-schoolnet';
  $TITLE = "IEM | School Network";
include("$rootpath/include/header.php"); 
?>

<div class="text">
<table><tr><td style="width: 620px;" valign="top">
<p>As the name implies, these automated weather stations are
located at schools throughout the state.  Currently, 
<a href="http://www.kcci.com/">KCCI-TV</a> (Des Moines, IA),
<a href="http://www.keloland.com">KELO-TV</a> (Sioux Falls, SD), and <a href="http://www.kimt.com">KIMT-TV</a> (Mason City, IA) have 
graciously provided
the IEM with the ability to process data from their observing networks.  
</p></td><td>

<div class="ninfo">
<b><u>School Network</u></b>
<br>Sampled: 3x / hour
<br>Reports: Continuously
<br>Stations: 72 (KCCI)
<br>Stations: 39 (KELO)
<br />Stations: 15 (KIMT)
<br><a href="<?php echo $rooturl; ?>/sites/locate.php?network=KCCI">KCCI Locations</a>
<br><a href="<?php echo $rooturl; ?>/sites/locate.php?network=KELO">KELO Locations</a>
<br><a href="<?php echo $rooturl; ?>/sites/locate.php?network=KIMT">KIMT Locations</a>
</div></td></tr></table>

<!-- Begin TV tabs -->

<?php include('switchbar.php'); ?>

<?php
  $link = "index.php";
  if ($tv == 'KCCI'){
    include('KCCI.php');
  }
  else if ($tv == 'KELO'){
    include('KELO.php');
  }
  else if ($tv == 'KIMT'){
    include('KIMT.php');
  }
?>
</td></tr></table>
</td></tr></table>
</td></tr></table>

<p>Many of the school net stations are not located in good
meteorological locations.  While the stations may be accurate, their data
may not be representative of the area in general.
Often, they are placed on top of buildings and may
have obstructions which could skew wind and temperature readings.  The
stations are placed at schools for educational purposes and to get students
interested in the weather.</p></div>


<?php include("$rootpath/include/footer.php"); ?>
