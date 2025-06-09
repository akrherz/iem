<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/database.inc.php";

$t = new MyView();
$t->iemss = True;
define("IEM_APPID", 165);

$t->title = "USCRN Data Download";

$ys1 = yearSelect(2001, date("Y"), "year1");
$ms1 = monthSelect("1", "month1");
$ds1 = daySelect("1", "day1");
$hs1 = gmtHourSelect("0", "hour1");
$ys2 = yearSelect(2001, date("Y"), "year2");
$ms2 = monthSelect(date("m"), "month2");
$ds2 = daySelect(date("d"), "day2");
$hs2 = gmtHourSelect("0", "hour2");

$t->content = <<<EOM
<ol class="breadcrumb">
 <li><a href="/uscrn/">USCRN Mainpage</a></li>
 <li class="active">USCRN Download</li>
</ol>
<h3>USCRN Data Download</h3>

<p><a class="btn btn-default" href="/cgi-bin/request/uscrn.py?help"><i class="fa fa-file-text"></i> Backend Documentation</a> exists for those that
wish to script against this service.</p>

<form target="_blank" method="GET" action="/cgi-bin/request/uscrn.py" name="iemss">
<input type='hidden' name='network' value="USCRN" />

<div class="row">
<div class="col-sm-7">

<h3>1. Select Station(s):</h3>

<div id="iemss" data-network="USCRN"></div>

</div>
<div class="col-sm-5">

<h3>2. Select Start/End Time:</h3>

<table class="table table-condensed">
  <tr>
    <td></td>
    <th>Year</th><th>Month</th><th>Day</th>
    <th>Hour</th>
  </tr>

  <tr>
    <th>Start:</th>
    <td>{$ys1}</td>
    <td>{$ms1}</td>
    <td>{$ds1}</td>
    <td>{$hs1}
    <input type="hidden" name="minute1" value="0"></td>
    </td>
  </tr>

  <tr>
    <th>End:</th>
    <td>{$ys2}</td>
    <td>{$ms2}</td>
    <td>{$ds2}</td>
    <td>{$hs2}
    <input type="hidden" name="minute2" value="0">
    </td>
  </tr>
</table>

<h3>3. How to download/view?</h3>

<select name="what">
  <option value="txt">Download as Delimited Text File</option>
  <option value="excel">Download as Excel</option>
  <option value="html">View as HTML webpage</option>
</select>

<h3>3a. Data Delimitation:</h3>

<p>If you selected 'Delimited Text File' above, how do you want the values
separated in the downloaded file?</p>

<select name="delim">
    <option value="comma">Comma</option>
    <option value="space">Space</option>
    <option value="tab">Tab</option>
</select>

<h3>6. Submit Form:</h3>

<input type="submit" value="Process Data Request">
<input type="reset">

</div>
</div>

<h3>Returned data columns:</h3>
<pre>
utc_valid - Observation timestamp in UTC
station - Station identifier
tmpc - Air Temperature [C]
precip_mm - Precipitation [mm]
srad - Solar Radiation [Wm2]
srad_flag - Flag
skinc
skinc_flag
skinc_type
rh
rh_flag
vsm5
soilc5
wetness
wetness_flag
wind_mps
wind_mps_flag
</pre>

<h3>Frequently Asked Questions:</h3>

</form>
EOM;
$t->render('single.phtml');
