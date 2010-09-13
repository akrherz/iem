<?php
include("../../config/settings.inc.php");
$TITLE = "IEM | Agricultural Weather/Climate Information";
$THISPAGE = "iem-info";
include("$rootpath/include/header.php"); ?>

<h3 class="heading">IEM Ag Weather/Climate Information</h3><p>

<div class="warning">Please <a href="<?php echo $rooturl; ?>/info/contacts.php">suggest</a> features for this page.  We are looking to collect all relevant
Iowa Ag Weather information in a one-stop location.</div>

<p>

<table cellspacing="0" border="1" cellpadding="7">
<tr>
 <th></th>
 <th>Current</th>
 <th>Growing Season</th>
</tr>



<tr>
  <th>Growing Degree Days</th>
  <td></td>
  <td><a href="../GIS/apps/coop/gsplot.phtml?var=gdd50&year=2010">Map of Totals</a>
  <br /><a href="../plotting/coop/acc.phtml">Single Site Graphs</a></td>
</tr>

<tr>
  <th>Precipitation</th>
  <td><a href="../data/summary/today_prec.png">Today's total</a></td>
  <td><a href="../plotting/coop/acc.phtml">Single Site Graphs</a></td>
</tr>


<tr>
 <th>Soil Moisture</th>
 <td><a href="http://wepp.mesonet.agron.iastate.edu/GIS/sm.phtml?pvar=vsm">Modelled Estimates</a></td>
 <td></td>
</tr>

<tr>
 <th>Soil Temperatures</th>
 <td><a href="../agclimate/soilt.php">County Estimates</a></td>
 <td></td>
</tr>

<tr>
  <th>Stress Degree Days</th>
  <td></td>
  <td><a href="../GIS/apps/coop/gsplot.phtml?var=sdd50&year=2010">Map of Totals</a>
  <br /><a href="../plotting/coop/acc.phtml">Single Site Graphs</a></td>
</tr>

</table>

<h4>External Links</h4>
<ul>
 <li><a href="http://www.iowaagriculture.gov/climatology.asp">State of Iowa Climatologist</a></li>
 <li><a href="http://www.nass.usda.gov/Charts_and_Maps/Crop_Progress_&_Condition/index.asp">USDA Charts &amp; Maps of Crop Progress</a></li>
 <li><a href="http://www.nass.usda.gov/Publications/State_Crop_Progress_and_Condition/index.asp">USDA State Crop Progress &amp; Condition</a></li>
</ul>

<?php include("$rootpath/include/footer.php"); ?>
