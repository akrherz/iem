<?php 
require_once "../../../config/settings.inc.php";

require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/imagemaps.php";
require_once "../../../include/forms.php";

$t = new MyView();

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

<ol class="breadcrumb">
 <li><a href="/projects/talltowers/">IEM Tall Towers Homepage</a></li>
 <li class="active">Analog Download</li>
</ol>

<p>The dataset being made available is very large and difficult to serve out
on demand.  Also there is a need to track and report usage of this dataset.
Therefore, this interface requires your email address and affiliation
to download the file.  You'll be sent an email when the requested data is
generated (usually within 1-2 minutes.</p>

<form method="GET" action="/cgi-bin/request/talltowers.py" name="iemss">

<h4>1) Select Tower(s):</h4>

<select name="station" size="2" MULTIPLE>
  <option value="ETTI4">ETTI4 - Hamilton County - Tall Towers</option>
  <option value="MCAI4">MCAI4 - Story County - Tall Towers</option>
</select>

<h4>2) Specific Date Range:</h4>

<table class="table table-condensed">
<tr><th>Start Date:</th><td>{$y1select} {$m1select} {$d1select} {$h1select}</td></tr>
<tr><th>End Date:</th><td>{$y2select} {$m2select} {$d2select} {$h2select}</td></tr>
</table>
		
<h4>3) Download Options:</h4>
		
<p><strong>Data Format:</strong> 
<select name="format">
	<option value="comma">Comma Delimited</option>
	<option value="excel">Excel (.xlsx)</option>
	<option value="tdf">Tab Delimited</option>
</select></p>

<h4>4) Email and Affiliation</h4>

<p><strong>Your Email:</strong><input type="text" name="email">		
<p><strong>Your Affiliation:</strong><input type="text" name="affiliation">		

<h4>5) Finally, process request</h4>

  <input type="submit" value="Get Data">
  <input type="reset">

 </form>

<p><strong>Download Variable Description</strong>

<dl class="dl-horizontal">
<dt>station:</dt>
<dd>three or four character site identifier</dd>
</dl>

EOF;
$t->render('single.phtml');
?>
