<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
	<TITLE>IEM | Current Data</TITLE>
	<META NAME="AUTHOR" CONTENT="Dave Flory">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>

<?php 
        $current="facts";
	include("../include/header2.php"); 
        include("../include/header_site.php");
        include("../include/dbase_sites.php");

?>
<TABLE class="sites">
<TR>
        <TD class="spacer">&nbsp</TD>
        <TD><font class="bluet"><?php echo $row["name"]; ?><br /></font></TD>
</TR>
<TR>
        <TD class="spacer">&nbsp</TD> 
        <TD valign="top">Station ID<br /><br />Network<br /><br />County
        <br /><br />Variables Reported<br /><br />Interval<br /><br />Latitude, Longitude
        <br /><br />Archive Status<br /><br />Current Conditions</TD>
        <TD valign="top">ID<br /><br />Network<br /><br />County<br /><br />Variables
        <br /><br />Interval<br /><br />Lat,Lon<br /><br />Archive<br /><br />Temp</TD>
</TR>
</TABLE>
&nbsp;&nbsp;

<?php include("../include/footer2.php"); ?>
