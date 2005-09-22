<?php 
include("../../../config/settings.inc.php");
	$TITLE = "IEM | GDD Method";
include("$rootpath/include/header.php"); 
?>

<h3 class="heading">Growing Degree Days</H3>

<div class="text">
<p>This page describes the quality control method used for calculating GDD.

<P><h3 class="subtitle">Plots using this method:</h3>
<BR> &nbsp; &nbsp; GDD since June 1 <a href="/data/summary/gdd_qc.gif">Plot</a> or <a href="/data/summary/gdd_qc_contour.gif">Contour</a>


<P><h3 class="subtitle">Need for QC:</h3>
<BR>For various reasons, all potential reports from automated observing stations are not sent to the IEM server.  This
makes creating a climatology problematic.  In order to calculate Growing Degree Days (GDD), a station's high and low
temperature each day must be known.  Without a complete record, the true high and low is unknown.

<BR><BR>The basic GDD plot on the IEM server just calculates the maximum and minimum temperature recorded for that day
regardless of the completeness of the data.

<P><h3 class="subtitle">Procedure:</h3>
<ol>
	<li>The number of observations saved for each station in Iowa are counted.  Only observations valid at
the top of the hour are included.  The maximum value for each day is considered the best record possible for that 
particular day.</li>

	<li>The state is divided into 9 regions having approximately 5 stations each.  Statewide and regional 
averages are computed from stations meeting the requirement from number step 1.</li>

	<li>If a region does not have a single station reporting enough obs for the day, all of the region's members will be assigned 
the state average for that day.</li> 

	<li>Locations not reporting enough obs are assigned the averages from their respective region.</li>

	<li>GDD are then totaled.</li>
</ol>

<BR><BR>
<P align="right">Revised: 19 Sept 2001
</div>

<?php include("$rootpath/include/footer.php"); ?>
