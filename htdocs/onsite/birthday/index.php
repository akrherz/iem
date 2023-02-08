<?php  
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
$t = new MyView();
  $t->title = "Birthday Weather";
require_once "../../../include/forms.php";
require_once "../../../include/imagemaps.php";

$startYear = isset($_GET['startYear']) ? intval($_GET['startYear']): 1951;

$cselect = networkSelect("IACLIMATE", "IA0200", Array(), "city");
$mselect = monthSelect2("1", "month");
$dselect = daySelect2("1", "day");

$t->content = <<<EOF
<H3 class="heading">The Weather on your Birthday!!</H3>
<BR>

If you were born in Iowa between 1900 and 2005, you can fill out the form below and discover the weather
conditions at a location near to you.  Just follow the instructions below.


<BR><BR>

<form method="GET" action="/cgi-bin/onsite/birthday/getweather.py">

<p><H3 class="subtitle">1. Select the city nearest to you:</H3><p>
{$cselect}

<p><H3 class="subtitle">2. Enter your Birthdate:</H3><p>

<table><TR><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
<TR>
<TD><INPUT type="TEXT" name="year" size="5" MAXLENGTH="4" value="1951"></TD>

<TD>{$mselect}</TD>

<TD>{$dselect}</TD>

</TR></TABLE><p>

<H3 class="subtitle">4. Submit your values:</H3><p>
<input type="SUBMIT" value="Get Weather"><input type="RESET">

</form>

<P>The weather data is not guarenteed to be accurate and it should be used for educational and entertainment
purposes only.
EOF;
$t->render('single.phtml');
