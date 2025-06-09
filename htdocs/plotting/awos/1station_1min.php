<?php 
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";
$t = new MyView();

$station = isset($_GET["station"]) ? xssafe($_GET["station"]): "";
$year = get_int404("year", 2011);
$month = get_int404("month", 1);
$day = get_int404("day", 1);

$t->title = "AWOS 1 Minute Time Series";

$nselect = networkSelect("IA_ASOS", $station);
$yselect = yearSelect(1995, 2011, $year);
$mselect = monthSelect($month);
$dselect = daySelect($day);
$content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
 <li class="breadcrumb-item"><a href="/AWOS/">AWOS Network</a></li>
 <li class="breadcrumb-item active" aria-current="page">One minute time series</li>
</ol>
</nav>

<p><b>Note:</b>The archive currently contains data from 1 Jan 1995 
till <strong>1 April 2011</strong>. 
Fort Dodge and Clinton were converted to ~ASOS, 
but are available for some times earlier in the archive.<p>

  <form method="GET" action="1station_1min.php">
Make plot selections: <br>
    {$nselect} 
 
   {$yselect}
   {$mselect}
   {$dselect}
   
  <input type="submit" value="Make Plot">
  </form>
EOM;
if (strlen($station) > 0 ) {

$content .= <<<EOM

<br />
<img class="img-fluid" src="1min.php?year={$year}&amp;month={$month}&amp;day={$day}&amp;station={$station}" alt="Time Series">

<br />
<img class="img-fluid" src="1min_V.php?year={$year}&amp;month={$month}&amp;day={$day}&amp;station={$station}" alt="Time Series">

<br>
<img class="img-fluid" src="1min_P.php?year={$year}&amp;month={$month}&amp;day={$day}&amp;station={$station}" alt="Time Series">


<p><b>Note:</b> The wind speeds are indicated every minute by the red line. 
The blue dots represent wind direction and are shown every 10 minutes.</p>

EOM;
} 
$content .= <<<EOM

<br><br>
EOM;
$t->content = $content;
$t->render('single.phtml');
