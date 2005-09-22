<?php
include("/mesonet/php/include/forms.php");

$TITLE = "IEM | NSTL Flux Sites";
include("/mesonet/php/include/header.php"); ?>

<TR><TD>

<h3 class="heading">National Soil Tilth Lab Flux Sites</h3>

<p>The IEM is pleased to host the data from a set of observing platforms operated by the National Soil Tilth Lab.  These sites measure
<ul>
 <li>Net Radiation,</li>
 <li>Soil Heat Flux,</li>
 <li>Latent Heat Flux,</li>
 <li>Sensible Heat Flux,</li>
 <li>and C02 Flux</li>
</ul>
 at 30 minute intervals.  Data from these sites is updated daily with the most recent complete record being 2 days ago.

<h3>Site Information:</h3>

<table>
<thead><tr><th>ID</th><th>Name</th><th>Lat</th><th>Lon</th><th>First Observation</th><th>Last Observation</th></tr></thead>

<tbody>
<tr><td>corn</td><td>Over Corn Residue</td><td>41.97482</td><td>-94.69367</td><td>1 Apr 2005</td><td>Ongoing</td></tr>
<tr><td>sbean</td><td>Over Soybean Residue</td><td>41.9749</td><td>-93.6914</td><td>1 Jan 2005</td><td>8 Apr 2005</td></tr>
<tr><td>nspr</td><td>Over Prairie</td><td>41.55865</td><td>-93.29286</td><td>21 Mar 2005</td><td>Ongoing</td></tr>
</tr>
</tbody>
</table>

<h3>Data Tools:</h3>
<ul>
 <li><a href="plots.phtml">Generate comparison plots</a></li>
</ul>


<h3>Download Data:</h3>

<table cellpadding=3 border=1 >
<tr><td>
<b>Request Date:</b>
<form method="GET" action="dl.phtml" name="single">
<br />Year: 2005 <input type="hidden" value="2005" name="year">
<br /><b>Month:</b><?php echo monthSelect($month, "month"); ?>
<br /><b>Day:</b><?php echo daySelect($day, "day"); ?>
<br /><input type="submit" value="Download Date">
</form>
</td><td>
<b>Request Everything!</b>
<form method="GET" action="dl.phtml" name="all">
<br /><input type="hidden" name="all" value="all">
<input type="submit" value="Download Everything!">
</form>
</td></tr></table>

<?php include("/mesonet/php/include/footer.php"); ?>
