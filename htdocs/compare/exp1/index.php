<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
	<TITLE>IEM | Comparisons</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>

<?php 
	include("../../include/header2.php"); 
?>

<div class="ptitle">Simple ASOS vs RWIS Comparison</div>

<p><font class="intro">The IEM is made up of observing networks with different 
observing equipment.  These differences produce differences in the datasets
and can make comparisons sometimes difficult.  This page attempts a simple 
comparison between data from 3 ASOS sites with 3 RWIS sites nearby.</p>

<p><font class="bluet">Dataset:</font>

<br><br>For this comparison, data from 2002, specifically from 1 Jan till 10 Sep, is
used.  Data from the Ames (AMW), Mason City (MCW) and Spencer (SPW) ASOS sites
is compared against the Ames (RAME), Mason City (RMCW), and Spencer (RSPE) RWIS
sites.  Please refer to the IEM <a href="/ASOS">ASOS</a> and IEM 
<a href="/RWIS/">RWIS</a> homepages for more information.</p>

<p><font class="bluet">Methodology:</font>

<br><br>Data stored in the IEM database was sent to a special database for this 
comparison.  An application was quickly written to build plots based on 
Simple Query Language (SQL) statements of my choice.  Plots were saved and
then presented on this page.
<br><br>Comparisons are done for matching timestamps.  For instance, temperature
differences are based on the difference of temperature at the same 
observation time.  There is some ambiguity in the observation time, but it
is insignificant for this comparision.</p>

<p><font class="bluet">Hypothesis:</font>

<br><br>Since the RWIS stations don't utilize an aspirated thermometer, there
should be a <b>warm</b> temperature bias at low wind speeds.</p>

<p><font class="bluet">Rationale:</font>

<br><br>Aspirated thermometers are used as an attempt to negate the heating 
effects of the instrument and its surroundings.  Allthough, the instruments
are painted white, they are still subspect to exposure errors through
radiational heating and then long wave emissions.  
By aspirating the thermometer, the exchange of environmental air is 
increased limiting exposure errors.

<br><br>The RWIS sites do use a ventilated thermometer, but they are not 
aspirated like the ASOS sites are.  Since the RWIS sites would be suspect
to exposure errors, they should read warmer.  This bias should appear in 
the nighttime hours when the wind speeds are the lightest, since the 
exposure errors would not be compensated by the ambient wind.

<p><font class="bluet">Data & Plots:</font></p>


<p>
<table align="right" width="100"><tr><td>
<img src="temps_simple.png"><br>
<font size="-1"><b>Fig 1</b>  For a given wind speed at the RWIS site, the average
temperature difference is shown.</font>
</td></tr></table>
Lets begin with a simple plot (Fig 1),
shown are average temperature differences for a given RWIS wind speed.  This
plot would seem to validate the hypothesis that the RWIS stations have a warm
bias at low wind speeds.  Another remarkable feature of the plot is the 
consistantcy between the different station comparisons.  Anonymolous behaviour
appears to be occuring when the wind speed is zero knots, but the trend looks
to be the same.
<br><br>Notes about the plot.
<li>Wind speeds above 25 knots were not included, since they are poorly sampled
(not as many observations).</li>
<li>RWIS winds were used to group the observations, since ASOS does not report
non-zero wind speeds below 3 knots.</li>

<br><br>Lets not let (Fig 1) tell the whole story.  During a typical day, the 
surface winds will be a direct result of the boundary layer stability.  So
one would expect light winds in the morning when the stability is the 
highest and then the strongest winds in mid afternoon when the boundary
layer is the deepest.  Well, with our data, we can generate a plot of 
average wind speeds versus hour of the day (Fig 2).

<table align="right" width="100"><tr><td>
<img src="hourly_winds.png"><br>
<font size="-1"><b>Fig 2</b> Average wind speeds per local hour of the day.
temperature difference is shown.</font>
</td></tr></table>

<br><br>Figure 2 produces an extremely interesting plot of the diurnal wind 
cycle.  There are two points on the plot that appear to be discontinuities.
One at about 7 AM and one at about 8 PM.  These are called inflection points
and are well documented.  They are mentioned in this context just to 
illustrate that theory can often be found in real data.
<br><br>The most distribuing aspect of this plot appears to be the ~1 knot 
of difference between the ASOS average and RWIS average.  There are two 
possible reasons for this difference.  Probably the most important is the
difference in height of the wind instruments.  While the ASOS is at 10m, the
RWIS is a bit lower than that.  Assuming a log-wind profile, it would stand
to reason that the RWIS would read lower.
<br><br>The point of Fig 2 is to show the times when the wind speeds appear to 
be the smallest.  Our hypothesis states that the RWIS stations should read 
warmer during light winds and that the lightest winds are during the nighttime,
so it would seem natural to look at average temperatures per hour (Fig 3). 

<table align="right" width="100"><tr><td>
<img src="hourly_temps.png"><br>
<font size="-1"><b>Fig 3</b> Hourly average temperatures for Ames.</font>
</td></tr></table>

<br><br>Figure 3 shows the average hourly temperatures from the RWIS and ASOS 
site.  This figure should seem to support our hypothesis even more.  The RWIS
site appears to have a warm bias during the evening hours, when Fig 2 would
indicate that the winds are the lightest.  Before going much further, we 
should probably backtrack a little bit.  Up until this point, we have been 
assuming that the Ames ASOS site is reading correctly under all conditions 
and we have been witch-hunting the RWIS site.  Lets generate a similar 
plot as Fig 3, but for a different location.  Fig 4 is similar to Fig 3, but
for Mason City.

<table align="right" width="100"><tr><td>
<img src="hourly_temps_MCW.png"><br>
<font size="-1"><b>Fig 3</b> Hourly average temperatures for Mason City.</font>
</td></tr></table>

<br><br>Fig 4 closely agrees with Fig 3.  But we are no further to a conclusion.
The ASOS site could be reading cold at night.  Lets think through this logically.  It has been shown that during the main daylight hours, the RWIS and ASOS
sites seem to agree closely.  Now either both sites are incorrect or they 
both are accurate.  Lets assume that they are accurate during the daytime.
Now, what is happening in the late afternoon when the ASOS site starts to 
read cooler?  If we assume that the ASOS site is reading cooler, how does
this physically happen?  I would assert that forced ventilation of the ASOS
site is reducing exposure errors that are appearing in the RWIS site.

<p><font class="bluet">Conclusions:</font>
<br><br>I am not sure if conclusions can be drawn from this limited study, but it
would appear that the RWIS stations have a temperature exposure problem 
for light winds. There were four sets of ASOS vs RWIS comparisons that were
done and they all produced similar results.

<?php include("../../include/footer2.php"); ?>
