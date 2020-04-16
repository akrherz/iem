<?php 
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
$t = new MyView();
$t->title = "School Network Parameters";

$t->content = <<<EOF
<h3>SchoolNet Data Explanation</h3>

<div class="text">
<p><h3>Observation Time</h3>
<p>This is the local valid time for which the observation was taken.
There may be some ambiguity around the times when Iowa changes from CDT->CST and
vice-versa.</p>

<p><h3>Air Temperature [tmpf]</h3>
<p>This value is simply the temperature of the air.  Values are in units
of degrees Fahrenhit.</p>

<p><h3>Wind Direction [drct]</h3>
<p>Wind Direction can sometimes be a hard concept to interpret.  The 
values are in integer degrees for where the wind is blowing from.  0&deg; 
is a wind from the North.  90&deg; is a wind from the East.  180&deg; in
a wind from the South.  &270&deg; is a wind from the West. 
<br>For example.  If the value is 90, this is an easterly wind.  Meaning,
if you were facing east, the wind would be in your face.</p>

<p><h3>Wind Speed [sknt]</h3>
<p>For the schoolNet sites, this value is an instantenous
measurement of the wind speed.  Values are in knots.</p>

<p><h3>Daily Precip Counter [pday]</h3>
<p>This value is the accumulated amount of precip recorded at
the site for the local day.  Values are in inches.</p>

<p><h3>Monthly Precip Counter [pmonth]</h3>
<p>This value is the accumulated amount of precip recorded at
the site for the current month. Values are in inches.</p>

<p><h3>Solar Radiation [srad]</h3>
<p>Instantaneous values of solar radiation.  Values are in Watts.
</p>

<p><h3>Relative Humidity [relh]</h3>
<p>Relative humidity is expressed as a percentage.  It is a 
measure of the amount of water vapor currently in the air versus the 
capacity of the air.</p>

<p><h3>Altimeter [alti]</h3>
<p>Atmospheric pressure expressed in inches of mercury.</p></div>
EOF;
$t->render('single.phtml');
?>
