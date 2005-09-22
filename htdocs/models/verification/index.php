<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd"> 
<HTML>
<HEAD>
	<TITLE>IEM | Model Verification</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/main.css">
</HEAD>

<?php 
	$title = "IEM | Model Verification";
	include("../../include/header.php");
 ?>

<TR>

<?php include("../../include/side.html"); ?>

<TD width="450" valign="top">

Back to IEM <a href="/models">Models</a> Homepage.

<P>
<h4>Introduction:</h4>

<P>The IEM provides a rich source of current surface data.  Numerical Models provide 
surface data forecasts.  Often, what is predicted (models) and what actually happens (obs)
are not compared in a timely fashion.   Operational weather forecasters often adjust what
numerical models are predicting, rather than explicitly making the forecasts.

<P>If a forecaster has the tools to compare current model forecasts to current observations,
insight into the remainder of the forecast can be realized.  The comparision process is not
easy.  3+ dimensional forecast models predict conditions for points/regions inside their own 
domain, while surface obs are valid for a particular point and time.

<P>This page contains products that compare model output to observational data.


<h4>ISU MM5</h4>
<form method="GET" action="/plotting/modelvf/temps.php">
<input type="hidden" name="model" value="mm5">

<TABLE>
<TR>
  <TD>
    <SELECT name="modelrun">
	<option value="00">00 UTC
	<option value="12">12 UTC
    </SELECT>
  </TD>
  <TD>
    <SELECT name="modelday">
        <option value="TODAY">TODAY
        <option value="YESTERDAY">YESTERDAY
    </SELECT>
  </TD>
  <TD>
    <SELECT name="station">
	<option value="AMW">Ames, Ia
	<option value="SUX">Sioux City, Ia
    </SELECT>
  </TD>
  <TD>
     <input type="SUBMIT" value="Create Comparison">
  </TD>
</TR>
</TABLE>
</form>


<h4>ISU workstation Eta</h4>
<form method="GET" action="/plotting/modelvf/temps.php">
<input type="hidden" name="model" value="wseta">

<TABLE>
<TR>
  <TD>
    <SELECT name="modelrun">
        <option value="00">00 UTC
    </SELECT>
  </TD>
  <TD>
    <SELECT name="modelday">
        <option value="TODAY">TODAY
        <option value="YESTERDAY">YESTERDAY
    </SELECT>
  </TD>
  <TD>
    <SELECT name="station">
        <option value="AMW">Ames, Ia
        <option value="SUX">Sioux City, Ia
    </SELECT>
  </TD>
  <TD>
     <input type="SUBMIT" value="Create Comparison">
  </TD>
</TR>
</TABLE>
</form>




</TD></TR>

<?php include("../../include/footer.html"); ?>
