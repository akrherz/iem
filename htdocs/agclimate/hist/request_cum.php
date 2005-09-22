<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
	<TITLE>ISU Agclimate Data Cumulative Plotter</TITLE>
	<META name="author" content="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>
<?php 
        include("../../include/header2.php"); 
?>
<b>Nav:</b> <a href="/agclimate">ISU AgClimate</a> <b> > </b> 
  Cumulative Data Plotter


<div class="ptitle">Cumulative Data Plotter:</div>

<p class="intro">The growing season totals are based on accumulations from 
May 1.  This arbitrary date may not be representative in all parts of the 
state of Iowa.  With this form, you can select a time period that best meets 
your needs.</p>

<form method="POST" action="/cgi-bin/agclimate/hist/gen_gs.py">

<div style="background: #cae1ff; padding: 3px; border-color: #cae1ff;">
     <b>Make Plot Selections:</b>
  <div style="background: white; padding: 3px;">

<!--
<option value="SGDD">Soil Growing Degree Days
-->
<b>Select Variable:</b> <SELECT name="type">
	<option value="ET">Evapo-transpiration
	<option value="GDD">Growing Degree Days
	<option value="PREC">Precipitation totals
</SELECT>

<br>
<TABLE>
	<TR>
		<TH></TH>
		<TH>Month:</TH>
		<TH>Day:</TH>
		<TH>Year:</TH>
		</TR>
	<TR>
		<TH>Starting On:</TH>
		<td><SELECT name="start_month">
			<option value="1">January
			<option value="2">Febuary
			<option value="3">March
			<option value="4">April
			<option value="5">May
			<option value="6">June
			<option value="7">July
			<option value="8">August
			<option value="9">September
			<option value="10">October
			<option value="11">November
			<option value="12">December
			</SELECT></td>
                                <td><SELECT name="start_day">
                                        <option value="1">1     <option value="2">2     <option value="3">3     <option
value="4">4
                                        <option value="5">5     <option value="6">6     <option value="7">7     <option
value="8">8
                                        <option value="9">9     <option value="10">10   <option value="11">11   <option
value="12">12
                                        <option value="13">13   <option value="14">14   <option value="15">15   <option
value="16">16
                                        <option value="17">17   <option value="18">18   <option value="19">19   <option
value="20">20
                                        <option value="21">21   <option value="22">22   <option value="23">23   <option
value="24">24
                                        <option value="25">25   <option value="26">26   <option value="27">27   <option
value="28">28
                                        <option value="29">29   <option value="30">30   <option value="31">31
                                </SELECT></td>
				<TD rowspan="2">
				<SELECT name="yeer">
					<option>2003
					<option>2002
					<option>2001
					<option>2000
					<option>1999
				</SELECT>
				</TD>
                                </TR>
                                
<TR><TH>Ending On:</TH>
                                <td><SELECT name="end_month">
                                        <option value="1">January
                                        <option value="2">Febuary
                                        <option value="3">March
                                        <option value="4">April
                                        <option value="5">May
                                        <option value="6">June
                                        <option value="7">July
                                        <option value="8">August
                                        <option value="9">September
                                        <option value="10">October
                                        <option value="11">November
                                        <option value="12">December
                                </SELECT></td>
                                <td><SELECT name="end_day">
                                        <option value="1">1     <option value="2">2     <option value="3">3     <option
value="4">4
                                        <option value="5">5     <option value="6">6     <option value="7">7     <option
value="8">8
                                        <option value="9">9     <option value="10">10   <option value="11">11   <option
value="12">12
                                        <option value="13">13   <option value="14">14   <option value="15">15   <option
value="16">16
                                        <option value="17">17   <option value="18">18   <option value="19">19   <option
value="20">20
                                        <option value="21">21   <option value="22">22   <option value="23">23   <option
value="24">24
                                        <option value="25">25   <option value="26">26   <option value="27">27   <option
value="28">28
                                        <option value="29">29   <option value="30">30   <option value="31">31
                                </SELECT></td>
                                </TR>
                        </TABLE>

<input type="Submit" value="Generate Plot">

</div></div>

<BR>

<B>Caveats:</B><BR>
<P>Any precipation data, collected while temperatures are often below freezing, may be 
incorrect.  Use with caution.

<P>When selecting dates, the end dates are inclusive.

<P><B>Notes:</B><BR>
30 May 2000: I took away the Soil Degree Day plotting function, because it takes *way* to long.  If you are really
interested in those plots, let me know.

<br><br>
<?php include("../../include/footer2.php"); ?>
