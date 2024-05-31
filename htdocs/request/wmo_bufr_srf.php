<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/imagemaps.php";
require_once "../../include/forms.php";
require_once "../../include/database.inc.php";

$t = new MyView();
$t->iemss = True;
define("IEM_APPID", 162);

$t->title = "WMO BUFR Surface Station Data Download";

$ys1 = yearSelect2(2024, date("Y"), "year1");
$ms1 = monthSelect("1", "month1");
$ds1 = daySelect2("1", "day1");
$hs1 = gmtHourSelect("0", "hour1");
$ys2 = yearSelect2(2024, date("Y"), "year2");
$ms2 = monthSelect(date("m"), "month2");
$ds2 = daySelect2(date("d"), "day2");
$hs2 = gmtHourSelect("0", "hour2");

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/other/">Other Mainpage</a></li>
 <li class="active">WMO BUFR Surface Download</li>
</ol>
<h3>WMO BUFR Surface Data Download</h3>

<p><a class="btn btn-default" href="/cgi-bin/request/wmo_bufr_srf.py?help"><i class="fa fa-file-text"></i> Backend Documentation</a> exists for those that
wish to script against this service.</p>

<form target="_blank" method="GET" action="/cgi-bin/request/wmo_bufr_srf.py" name="iemss">
<input type='hidden' name='network' value="WMO_BUFR_SRF" />

<div class="row">
<div class="col-sm-7">

<h3>1. Select Station(s):</h3>

<div id="iemss" data-network="WMO_BUFR_SRF"></div>

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
    <option value="comma">Comma
    <option value="space">Space
    <option value="tab">Tab
</select>

<h3>6. Submit Form:</h3>

<input type="submit" value="Process Data Request">
<input type="reset">

</div>
</div>

<h3>Returned data columns:</h3>
<pre>
utc_valid - Observation timestamp in UTC
station - Often WIGOS or guessed WIGOS identifier
tmpf - Air temperature in F
dwpf - Dew Point Temperature in F
drct - Wind Direction (degrees North)
sknt - Wind Speed (knots)
gust - Wind Gust (knots)
relh - Relative Humidity (%)
alti - Pressure Altimeter (inch)
pcpncnt - Precipitation Counter (inch)
pday - Precip for Day (inch)
pmonth - Precip for Month (inch)
srad - Solar Radiation (W/m^2)
tsoil_4in_f - Approx Four inch depth Soil Temp (F)
tsoil_8in_f - Approx Eight inch depth Soil Temp (F)
tsoil_16in_f - Approx Sixteen inch depth Soil Temp (F)
tsoil_20in_f - Approx Twenty inch depth Soil Temp (F)
tsoil_32in_f - Approx Thirty-Two inch depth Soil Temp (F)
tsoil_40in_f - Approx Forty inch depth Soil Temp (F)
tsoil_64in_f - Approx Sixty-Four inch depth Soil Temp (F)
tsoil_128in_f - Approx One Hundred Twenty-Eight inch depth Soil Temp (F)
skyc1 - Sky Cover 1
skyc2 - Sky Cover 2
skyc3 - Sky Cover 3
skyc4 - Sky Cover 4
skyl1 - Sky Level 1 (ft)
skyl2 - Sky Level 2 (ft)
skyl3 - Sky Level 3 (ft)
skyl4 - Sky Level 4 (ft)
srad_1h_j - Solar Radiation 1 hour sum (J/m^2)
</pre>

<h3>Frequently Asked Questions:</h3>


</form>
EOF;
$t->render('single.phtml');
