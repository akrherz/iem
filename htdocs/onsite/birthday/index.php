<?php  
include("../../../config/settings.inc.php");
  $TITLE = "IEM | Birthday Weather";
$THISPAGE = "archive-birthday";
include("$rootpath/include/header.php"); 
include("$rootpath/include/network.php");     
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;
?>

<H3 class="heading">The Weather on your Birthday!!</H3>
<BR>

<?php
$startYear = isset($_GET['startYear']) ? $_GET['startYear']: 1951;

?>
<div class="text">
If you were born in Iowa between 1900 and 2005, you can fill out the form below and discover the weather
conditions at a location near to you.  Just follow the instructions below.


<BR><BR>

<form method="GET" action="/cgi-bin/onsite/birthday/getweather.py">

<p><H3 class="subtitle">1. Select the city nearest to you:</H3><p>
<SELECT name="city" size="10">

<?php
	for(reset($cities); $key = key($cities); next($cities))
	{
			print("<option value=\"" . $cities[$key]["id"] . "__" . $cities[$key]["name"] . "\">" . $cities[$key]["name"] . "\n");
	}
?>
</SELECT>

<p><H3 class="subtitle">2. Enter your Birthdate:</H3><p>

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

<?php include("$rootpath/include/footer.php") ?>
