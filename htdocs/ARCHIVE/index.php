<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd">
<HTML>
<HEAD>
	<TITLE>Iowa Environmental Mesonet</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<link rel="stylesheet" type="text/css" href="css/main.css">
        <META HTTP-EQUIV="Pragma" CONTENT="no-cache">
	<meta HTTP-EQUIV="Cache-Control" content="no-cache">
</HEAD>

<?php 
	$title = "Iowa Environmental Mesonet";
	include("include/header.php"); ?>

<?php include("include/main_side.html"); ?>


<TD width="500" bgcolor="WHITE" valign="TOP">


<CENTER>
	<a href="http://www.dot.state.ia.us"><img src="/icons/doticon.gif" ALT="DOT" BORDER="0"></a>
	&nbsp; &nbsp; 
	<a href="http://www.iastate.edu"><img src="/icons/isuicon.gif" ALT="ISU" BORDER="0"></a>
	&nbsp; &nbsp; 
	<a href="http://www.crh.noaa.gov/dmx/"><img src="/icons/nws.gif" ALT="NWS" BORDER="0" height="40"></a>
</CENTER>

<P>Welcome to the Iowa Environmental Mesonet (IEM).  The IEM collects data from weather observing networks in Iowa
and makes the data available at this site. 


<!-- Begin Table for Products -->
<TABLE>
<TR>
	<TD>
	<img src="/images/thumb_current.gif" alt="Current Data" border="1" width="50">
	</TD>
	
	<TD valign="TOP">
	<B><a href="/current/">Current Data</a></B>
	<blockquote>Current data and plots from the mesonet.</blockquote>
	</TD>

	<TD>
	<img src="/images/thumb_climate.gif" alt="Climate" border="1" width="50">
	</TD>
	<TD valign="TOP">
	<B><a href="/climate/">Climatology</a></B>
	<blockquote>Recent and historical climate information from the mesonet.</blockquote>
	</TD>
</TR>

<TR>
	<TD>
	<img src="/images/thumb_plotting.gif" alt="Interactive Plotting" border="1" width="50">
	</TD>
	<TD valign="TOP">
	<B><a href="/plotting/">Interactive Plotting</a></B>
        <blockquote>User-generated plots.</blockquote>
        </TD>

        <TD>
	<img src="/images/thumb_compare.gif" alt="Comparisons" border="1" width="50">
        </TD>

	<TD valign="TOP">
	<B><a href="/compare/">Comparisons</a></B>
        <blockquote>Plots and statistics on how the components of the combined mesonet compare.</blockquote>
        </TD>
</TR>

<TR>
	<TD>
	<img src="/images/thumb_qc.gif" alt="Quality Control" border="1" width="50">
	</TD>
        <TD valign="TOP">
        <B><a href="/QC/">Quality Control</a></B>
        <blockquote>Quality Control information about data from the mesonet.</blockquote>
        </TD>

	<TD>
	<img src="/images/thumb_info.gif" alt="Information" border="1" width="50">
	</TD>
        <TD valign="TOP">
        <B><a href="/info.php">Information</a></B>
        <blockquote>Information about the mesonet.</blockquote> 
        </TD> 
</TR> 

</TABLE>
<!-- End Table for Products -->


<!-- Table for Popular Products -->
<CENTER>
<TABLE cellpadding="2" cellspacing="0" border="0" width="100%">

<TR>
	<TD align="CENTER" colspan="2"><font class="bluet"><B>Popular Products:</B></font></TD>
</TR>

<TR>
        <TD><a href="/current/conditions.php">Current Conditions</a> for mesonet sites.</TD>
	<TD><a href="data/mesonet.gif">Combined Mesonet Plot</a></TD>
</TR>

<TR>
 <!---
       <TD><a href="data/wceq.gif">Wind Chill Index</a></TD>
-->
        <TD colspan="2"><a href="/data/summary/today_prec.gif">Today's Precipitation</a></TD>
</TR>

</TABLE>
</CENTER>
<!-- End Table for Popular Products -->

<H3>Disclaimer:</H3>
<P class="info">While we use care to provide accurate weather/climatic information,
errors may occur because of equipment or other failure. We therefore provide this
information without any warranty of accuracy. Users of this weather/climate data
do so at their own risk, and are advised to use independent judgement as to 
whether to verify the data presented.



</TD></TR>

<?php include("include/main_footer.html"); ?>
