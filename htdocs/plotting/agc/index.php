<?php $TITLE = "IEM | ISU Ag Plotting";
include("/mesonet/php/include/header.php"); ?>

<div class="text">
Back to <a href="/agclimate/">ISU Ag Climate</a> Homepage.<p>

<BR>
We will be creating new interactive plotting programs for the ISU Ag Climate data.  If you 
have a particular plot you would like to see, please let us know.

<p><a href="/agclimate/src/stations.gif">Location</a> of AgClimate Stations.

<P><h3 class="subtitle">Yesterday Solar Radiation with Temps:</h3><BR>
This program will plot a timeseries of hourly solar radiation values with 4in soil temperatures
and air temperatures.  You will need to select a station to plot.
<P>
<FORM name="rad" METHOD="GET" ACTION="/plotting/agc/solarRad.php">
<TABLE>
<TR>
<TD>
<SELECT name="station">
	<option value="A130209">Ames
	<option value="A131069">Calmar
	<option value="A131299">Castana
	<option value="A131329">Cedar Rapids
	<option value="A131559">Chariton
	<option value="A131909">Crawfordsville
	<option value="A135879">Nashua
	<option value="A138019">Sutherland
	<option value="A134759">Lewis
	<option value="A136949">Rhodes
	<option value="A134309">Kanawha
	<option value="A135849">Muscatine
</SELECT>
</TD>
<TD>
	<INPUT TYPE="submit" value="Create Plot">
</TD>
</TR></TABLE>
</form>

<P><h3 class="subtitle">Daily High/Low for last 60 days:</h3><BR>
This program will plot the daily high and low temperatures for the previous 60 days.
You need to select a station below.
<P>
<FORM name="temps" METHOD="GET" ACTION="/plotting/agc/l30temps.php">
<TABLE>
<TR>
<TD>
<SELECT name="station">
        <option value="A130209">Ames
	<option value="A131069">Calmar
        <option value="A131299">Castana
        <option value="A131329">Cedar Rapids
        <option value="A131559">Chariton
        <option value="A131909">Crawfordsville
        <option value="A135879">Nashua
        <option value="A138019">Sutherland
        <option value="A134759">Lewis
        <option value="A136949">Rhodes
        <option value="A134309">Kanawha
        <option value="A135849">Muscatine
</SELECT>
</TD>
<TD>
        <INPUT TYPE="submit" value="Create Plot">
</TD>
</TR></TABLE>
</form>

<P><h3 class="subtitle">Daily 4in Soil Temps & Solar Rad for last 60 days:</h3><BR>
This program will plot the daily average 4in soil temperatures with daily solar 
radiation values. You need to select a station below.
<P>
<FORM name="rad2" METHOD="GET" ACTION="/plotting/agc/l60rad.php">
<TABLE>
<TR>
<TD>
<SELECT name="station">
        <option value="A130209">Ames
	<option value="A131069">Calmar
        <option value="A131299">Castana
        <option value="A131329">Cedar Rapids
        <option value="A131559">Chariton
        <option value="A131909">Crawfordsville
        <option value="A135879">Nashua
        <option value="A138019">Sutherland
        <option value="A134759">Lewis
        <option value="A136949">Rhodes
        <option value="A134309">Kanawha
        <option value="A135849">Muscatine
</SELECT>
</TD>
<TD>
        <INPUT TYPE="submit" value="Create Plot">
</TD>
</TR></TABLE>
</form>

<P><h3 class="subtitle">Precipitation minus PET for last 60 days:</h3><BR>
This program plots an accumulated difference between observed precipitation
and potiential evapotranspiration (PET).  You will need to select a station below in 
order to create the plot.
<br><b>NOTE:</b> Precipitation is not recorded in the cold season, so this plot should 
be carefully considered.

<P>
<FORM name="prec2" METHOD="GET" ACTION="/plotting/agc/l60p-et.php">
<TABLE>
<TR>
<TD>
<SELECT name="station">
        <option value="A130209">Ames
	<option value="A131069">Calmar
        <option value="A131299">Castana
        <option value="A131329">Cedar Rapids
        <option value="A131559">Chariton
        <option value="A131909">Crawfordsville
        <option value="A135879">Nashua
        <option value="A138019">Sutherland
        <option value="A134759">Lewis
        <option value="A136949">Rhodes
        <option value="A134309">Kanawha
        <option value="A135849">Muscatine
</SELECT>
</TD>
<TD>
        <INPUT TYPE="submit" value="Create Plot">
</TD>
</TR></TABLE>
</form></div>


<?php include("/mesonet/php/include/footer.php"); ?>
