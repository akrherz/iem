<?php 
require_once "../../../config/settings.inc.php";

require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/imagemaps.php";
require_once "../../../include/forms.php";

$t = new MyView();
$t->iemss = True;

$t->title = "Download TallTowers Sonic Data";

$y1select = yearSelect2(2016, date("Y"), "year1"); 
$y2select = yearSelect2(2016, date("Y"), "year2"); 

$m1select = monthSelect2(1, "month1"); 
$m2select = monthSelect2(date("m"), "month2"); 

$d1select = daySelect2(1, "day1"); 
$d2select = daySelect2(date("d"), "day2");

$h1select = gmtHourSelect(0, "hour1");
$h2select = gmtHourSelect(0, "hour2");

$ar = Array(
	"Etc/UTC" => "Coordinated Universal Time (UTC)",
    "America/Chicago" => "America/Chicago (CST/CDT)",
);

$tzselect = make_select("tz", "Etc/UTC", $ar);
		
$t->content = <<<EOF
<style type="text/css">
        #map {
            width: 100%;
            height: 450px;
            border: 2px solid black;
        }
</style>

<ol class="breadcrumb">
 <li><a href="/projects/talltowers/">IEM Tall Towers Homepage</a></li>
 <li class="active">Analog Download</li>
</ol>

<div class="row">
<div class="col-sm-7">

<h4>1) Select Station/Network by clicking on location: </h4>

<form method="GET" action="/cgi-bin/request/talltowers.py" name="iemss">
<div id="iemss" data-network="TALLTOWERS" data-name="station"></div>

</div>
<div class="col-sm-5">

<br><br>
<h4>3) Specific Date Range (If needed):</h4>

<table class="table table-condensed">
<tr><th>Start Date:</th><td>{$y1select} {$m1select} {$d1select} {$h1select}</td></tr>
<tr><th>End Date:</th><td>{$y2select} {$m2select} {$d2select} {$h2select}</td></tr>
</table>
		
<h4>4) Timezone of Observation Times:</h4>
<p><i>The following options are available for how the observation time is 
	presented.</i></p>
{$tzselect}

<h4>5) Download Options:</h4>
		
<p><strong>Data Format:</strong> 
<select name="format">
	<option value="tdf">Tab Delimited
	<option value="comma">Comma Delimited
</select></p>

<p><strong>Include Latitude + Longitude?</strong>
<select name="latlon">
  <option value="no">No
  <option value="yes">Yes
</select></p>

<p>
<select name="direct">
  <option value="no">View result data in web browser</option>
  <option value="yes">Save result data to file on computer</option>
</select></p>
		

<h4>7) Finally, get Data:</h4>

  <input type="submit" value="Get Data">
  <input type="reset">

 		</div>
 		</div>
 		
</form>

<p><strong>Download Variable Description</strong>

<dl class="dl-horizontal">
<dt>station:</dt>
<dd>three or four character site identifier</dd>
</dl>

EOF;
$t->render('single.phtml');
?>
