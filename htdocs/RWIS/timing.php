<?php 
include("../../config/settings.inc.php");
$TITLE = "IEM | RWIS Timing";
include("$rootpath/include/header.php"); ?>

<h3 class="heading">RWIS Data Timing</h3>

<div class="text">
<p>Unlike the ASOS & AWOS networks, the RWIS data is not 
reported at regular intervals.  This creates a problem when comparisons 
are to be made between the networks.  Traditionally, the ASOS stations 
report at about :53 past the hour and this observation is thus 
reported as being valid for the top of the hour.  For example, the Ames 
ASOS station makes an observation at 4:53 PM.  This observation is then 
considered as the conditions valid at 5:00 PM.  Since this time conversion 
is similar for all ASOS stations, comparisons between ASOS stations is not 
a problem.</p>

<p>The AWOS network in Iowa reports 3 times per hour.  Most 
of the stations report at :05, :25 and :45 minutes after the hour.  
Traditionally, these observations are then grouped into three time bins 
per hour.  These bins are :00, :20 and :40 after.  On the IEM site, you 
may notice plots that are valid for :20 or :40 after.  The obs in the 
:00 bin are then compared with the ASOS obs at :00, eventhough the 
true observational times are seperated by ~12 minutes.</p>

<p>
<table align="right" border=1>
<tr><th>Sample Time</th><th>Ob Valid</th><th>Time Bin</th></tr>
<tr><td>:05 after</td><td>:01 after</td><td>:00</td></tr>
<tr><td>:20 after</td><td>:08 after</td><td>:00</td></tr>
<tr><td>:35 after</td><td>:31 after</td><td>:40</td></tr>
<tr><td>:50 after</td><td>:38 after</td><td>:40</td></tr>
</table>

The RWIS network is sampled every 7 minutes, by the DOT.  The results of
this sampling are saved on the IEM every 15 minutes.  The hopes are to
catch enough observations to fill the 3 time periods per hour.  Sometimes
this does not work.  Consider this situation represented by the table to
the right. The network was sampled 4 times that hour and the station
generated 4 unique reports, but none of the reports would have been
classified valid for :20 after.  This creates a missing value for
comparison with AWOS stations.</p>

<p>The original RWIS observations are saved on the IEM 
server with their none regular timestamps.  It is our hope to generate 
better algorithms to handle these time difficulties.</p>

<p>Return to <a href="/RWIS/">RWIS</a> page.</p>
</div>
<?php include("$rootpath/include/footer.php"); ?>
