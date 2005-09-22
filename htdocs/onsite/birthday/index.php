<?php  
  $TITLE = "IEM | Birthday Weather";
include("/mesonet/php/include/header.php"); 
?>

<H3 class="heading">The Weather on your Birthday!!</H3>
<BR>

<?php
	if (!$startYear)
	{
		$startYear = "1951";
	}

	include("../../include/COOPstations.php");		
?>
<div class="text">
If you were born in Iowa between 1900 and 1998, you can fill out the form below and discover the weather
conditions at a location near to you.  Just follow the instructions below.


<BR><BR>

<H3 class="subtitle">1. Time period:</H3><p>
Weather data records do not date back as far for a particular station.  By selecting which period you where
born, you will be presented a list of stations with data for that time.<p>

<TABLE>
<TR>
	<?php
		if ($startYear != "1951") { 
			echo "<TD>I was born before 1951 <b>--</b></TD>"; 
			echo "<TD><a href='index.php?startYear=1951'>I was born after 1951</a></TD>";
			}
		else{
			echo "<TD><a href='index.php?startYear=1893'>I was born
			before 1951</a> <b>--</b></TD>";
			echo "<TD>I was born after 1951</TD>";
			}
	?>
	
</TR></TABLE>

<form method="GET" action="/cgi-bin/onsite/birthday/getweather.py">

<p><H3 class="subtitle">2. Select the city nearest to you:</H3><p>
<SELECT name="city" size="10">

<?php
	for(reset($cities); $key = key($cities); next($cities))
	{
		if ($startYear == "1951"){
			print("<option value=\"" . $cities[$key]["id"] . "__" . $cities[$key]["city"] . "\">" . $cities[$key]["city"] . "\n");
		}
		elseif ($cities[$key]["startYear"] == $startYear){
			print("<option value=\"" . $cities[$key]["id"] . "__" . $cities[$key]["city"] . "\">" . $cities[$key]["city"] . "\n");
		}
	}
?>
</SELECT>

<p><H3 class="subtitle">3. Enter your Birthdate:</H3><p>

<table><TR><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
<TR>
	<TD><INPUT type="TEXT" name="year" size="5" MAXLENGTH="4" value="1951"></TD>

<TD>
<SELECT name="month">
	<option value="1">January
	<option value="2">Feburary
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
</SELECT>
</TD>

<TD>
<SELECT name="day">
<?php
	for($i = 1; $i <= 31; $i++)
	{
		print("<option value=\"" . $i ."\">" . $i . "\n");
	}
?>
</SELECT>
</TD>

</TR></TABLE><p>

<H3 class="subtitle">4. Submit your values:</H3><p>
<input type="SUBMIT" value="Get Weather"><input type="RESET">

</form>

<P>The weather data is not guarenteed to be accurate and it should be used for educational and entertainment
purposes only.
</div>

<?php include("/mesonet/php/include/footer.php") ?>
