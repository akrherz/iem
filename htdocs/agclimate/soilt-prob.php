<?php
/* Create a table of soil temperature probabilities based on obs? */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 88);
include_once "../../include/myview.php";
$t = new MyView();
require_once "../../include/database.inc.php";
$t->thispage = "networks-agclimate";
require_once "../../include/imagemaps.php";
require_once "../../include/forms.php";

$station = isset($_GET["station"]) ? xssafe($_GET['station']): "A130209";
$tstr = isset($_GET["tstr"]) ? xssafe($_GET['tstr']): "50,45,40,35,32,28,23";

$conn = iemdb("isuag");
$rs = pg_prepare($conn, "spring", "SELECT extract(year from valid) as yr,
      max(extract(doy from valid)) as v from daily WHERE station = $1 and c30 < $2 and 
      extract(month from valid) < 7 and c30_f != 'e' GROUP by yr");
$rs = pg_prepare($conn, "fall", "SELECT extract(year from valid) as yr,
      min(extract(doy from valid)) as v from daily WHERE station = $1 and c30 < $2 and
      extract(month from valid) > 6 and c30_f != 'e' GROUP by yr");

$thresholds = explode(",",$tstr);
$tblrows = Array();

$row1 = "<tr><th>Date:</th>";
while (list($k,$thres) = each($thresholds))
{
  $row1 .= "<th>$thres</th>";
  $rs = pg_execute($conn, "spring", Array($station,$thres));
  $cnts = Array();
  $yrs = pg_num_rows($rs);
  for ($i=0;$row=pg_fetch_array($rs);$i++)
  {
    @$cnts[ $row["v"] ] += 1;
  }
  $probs = Array();
  $running = $yrs;
  for ($i=0;$i<182;$i++) {
    if (array_key_exists($i,$cnts)){ $running -= $cnts[$i]; }
    $probs[$i] = $running;
  }
  /* Day Sampler */
  for ($i=0;$i<182;$i=$i+5) {
    $ts = mktime(0,0,0,1,1,2000) + ($i * 86400);
    @$tblrows[$i] .= sprintf("<td>%.0f</td>", $probs[$i]/$yrs*100);
  }
}
$spring = "<table class=\"table table-condensed table-striped table-bordered\">$row1</tr>";
/* Print webpage */
for ($i=0;$i<182;$i=$i+5) {
  $ts = mktime(0,0,0,1,1,2000) + ($i * 86400);
  $spring .= sprintf("<tr><th>%s</th>%s</tr>", date("M d", $ts), $tblrows[$i]);
}
$spring .= "</table>";

/* ________________________FALL ______________ */
$tblrows = Array();
reset($thresholds);
while (list($k,$thres) = each($thresholds))
{
  $rs = pg_execute($conn, "fall", Array($station,$thres));
  $cnts = Array();
  $yrs = pg_num_rows($rs);
  for ($i=0;$row=pg_fetch_array($rs);$i++)
  {
    @$cnts[ $row["v"] ] += 1;
  }
  $probs = Array();
  $running = 0;
  for ($i=182;$i<366;$i++) {
    if (array_key_exists($i,$cnts)){ $running += $cnts[$i]; }
    $probs[$i] = $running;
  }
  /* Day Sampler */
  for ($i=182;$i<366;$i=$i+5) {
    $ts = mktime(0,0,0,1,1,2000) + ($i * 86400);
    @$tblrows[$i] .= sprintf("<td>%.0f</td>", $probs[$i]/$yrs*100);
  }
}
$fall = "<table class=\"table table-condensed table-striped table-bordered\">$row1</tr>";
/* Print webpage */
for ($i=182;$i<366;$i=$i+5) {
  $ts = mktime(0,0,0,1,1,2000) + ($i * 86400);
  $fall .= sprintf("<tr><th>%s</th>%s</tr>", date("M d", $ts), $tblrows[$i]);
}
$fall .= "</table>";

$sselect = isuagSelect($station);

$t->title = "ISUSM - Soil Temperature Probabilities";
$t->content = <<<EOF
<ol class="breadcrumb">
		<li><a href="/agclimate/">ISU Soil Moisture Network</a></li>
		<li class="active">Soil Temperature Probabilities</li>
</ol>

<h3>4 inch Soil Temperature Probabilities</h3>

<p>This application computes soil temperature exceedance based on the
observation record of a ISU Ag Climate site.  The average daily 4 inch
soil temperature is used in this calculation.
<ul>
 <li>Spring: The values represent the percentage of years that a temperature
below the given threshold was observed <strong>after</strong> a given date.</li>
 <li>Fall: The values represent the percentage of years that a temperature
below the given threshold was observed <strong>before</strong> a given date.</li>
</ul>

<div class="alert alert-info">This application uses the legacy ISU Ag Climate 
network for its computations.  Data from the newer ISU Soil Moisture Network
is not considered.</div>

<form method="GET" name='soil'>
<p><b>Select Station:</b>{$sselect}
<p><b>Thresholds:</b>
<input type="text" value="{$tstr}" name="tstr"> <i>Comma Seperated</i>
<br />
<input type="submit" value="Request">
</form>

<div class="row"><div class="col-md-6">

 <h3>Spring Probabilities<br />Given date to July 1rst</h3>
 {$spring}

 </div><div class="col-md-6">

 <h3>Fall Probabilities<br />July 1rst to given date</h3>
 {$fall}

 </div></div>
EOF;
$t->render('single.phtml');
 ?>
