<?php 
include("../../../config/settings.inc.php");
include("../../../include/myview.php");
$t = new MyView();

$station = isset($_GET["station"]) ? $_GET["station"] : "";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");

$t->thispage = "networks-awos";
$t->title = "AWOS 1 Minute Time Series";

include("../../../include/imagemaps.php"); 
include("../../../include/forms.php"); 

$nselect = networkSelect("AWOS", $station);
$yselect = yearSelect(1995,2011, $year);
$mselect = monthSelect($month);
$dselect = daySelect($day);
$content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/AWOS/">AWOS Network</a></li>
 <li class="active">One minute time series</li>
</ol>

<p><b>Note:</b>The archive currently contains data from 1 Jan 1995 
till the end of the previous month.  Fort Dodge and Clinton were converted to ~ASOS, 
but are available for some times earlier in the archive.<p>

  <form method="GET" action="1station_1min.php">
Make plot selections: <br>
    {$nselect} 
 
   {$yselect}
   {$mselect}
   {$dselect}
   
  <input type="submit" value="Make Plot">
  </form>
EOF;
if (strlen($station) > 0 ) {

$content .= <<<EOF

<br />
<img class="image-responsive" src="1min.php?year={$year}&month={$month}&day={$day}&station={$station}" ALT="Time Series">

<BR>
<img class="image-responsive" src="1min_V.php?year={$year}&month={$month}&day={$day}&station={$station}" ALT="Time Series">

<br>
<img class="image-responsive" src="1min_P.php?year={$year}&month={$month}&day={$day}&station={$station}" ALT="Time Series">


<p><b>Note:</b> The wind speeds are indicated every minute by the red line. 
The blue dots represent wind direction and are shown every 10 minutes.</p>

EOF;
} 
$content .= <<<EOF

<br><br>
EOF;
$t->content = $content;
$t->render('single.phtml');

?>