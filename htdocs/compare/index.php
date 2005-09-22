<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
	<TITLE>IEM | Comparisons</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>

<?php 
	$page = "compare";
	include("../include/header2.php"); 
?>

<TD><TR>

<p class="intro">This page contains plots of qualitative comparisons between
observing networks and an operation weather prediction model.  The 
initialization data for the RUC2 model is used for comparison.</p>

<TABLE cellpadding=0 border=0 cellspacing=0>
<TR>
        <TD><b>Temperatures:</b></TD>
</TR>

<TR>
        <TD>  
                &nbsp; &nbsp; [RWIS vs ASOS/AWOS]  -- <a href="/data/temps.gif">Plot</a> | 
                <a href="/data/temps_contour.gif">Contour</a>
                <BR>&nbsp; &nbsp; [Mesonet vs RUC2 Model]  -- <a href="/wx/data/models/ruc2_iem_T.gif">Plot</a> 
        </TD>
</TR>

<TR>
        <TD><b>Dew Points:</b></TD>
</TR>

<TR>
        <TD> 
                &nbsp; &nbsp; [RWIS vs ASOS/AWOS]  -- <a href="/data/dewps.gif">Plot</a> | 
                <a href="/data/dewps_contour.gif">Contour</a>
		<BR>&nbsp; &nbsp; [Mesonet vs RUC2 Model]  -- <a href="/wx/data/models/ruc2_iem_Td.gif">Plot</a>
        </TD>
</TR>

<TR>
	<TD><b>4 inch Soil Temperatures:</b></TD>
</TR>

<TR>
	<TD>
		&nbsp; &nbsp; [ISU AG vs NWS]  -- <a href="/data/5pm_soil.gif">5 PM yesterday</a>
			<a href="/help/imageHelp.php?iod=8"> <img alt="info" src="/icons/ihelp.png" border="0"></a>
	</TD>
</TR>

<TR>
        <TD><b>Winds:</b></TD>
</TR>

<TR>
        <TD>
                &nbsp; &nbsp; [RWIS vs ASOS/AWOS]  --<a href="/data/winds.gif">Plot</a>
			<a href="/help/imageHelp.php?iod=4"> <img alt="info" src="/icons/ihelp.png" border="0"></a>
		<BR>&nbsp; &nbsp; [Mesonet vs RUC2 Model]  -- <a href="/wx/data/models/ruc2_iem_V.gif">Plot</a>
        </TD>
</TR>



</TABLE>

<P><B>Text Products:</B>
<UL>
	<LI><a href="/data/report.txt">Current Mesonet statistics</a></LI>
</UL>

<P>You can interactively generate comparisons by using the <a href="/plotting/index.php">Interactive Plotter</a>.

<BR><BR><BR>


<?php include("../include/footer2.php"); ?>
