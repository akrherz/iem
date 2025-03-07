<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";

$t = new MyView();
$t->title = "Ag Climate";
$prod = get_int404("prod", 1);
$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));

$old2new = array(
    "/data/agclimate/air-temp-out.png" => 1,
    "/data/agclimate/4in-temp-out.png" => 2,
    "/agclimate/daily_pics/4in-temp-out.png" => 2,
    "/data/agclimate/soil-hilo-out.png" => 3,
    "/agclimate/daily_pics/soil-hilo-out.png" => 3,
    "/data/agclimate/rad-out.png" => 4,
    "/data/agclimate/prec-out.png" => 5,
    "/data/agclimate/et-out.png" => 6,
    "/data/agclimate/pk-wind-out.png" => 7,
    "/data/agclimate/avewind-out.png" => 8,
    "/data/agclimate/mon-et-out.png" => 10,
    "/data/agclimate/mon-prec-out.png" => 11
);

// Legacy
if (isset($_GET["src"]) && array_key_exists(xssafe($_GET["src"]), $old2new)) {
    $prod = $old2new[$_GET["src"]];
}

$data = array(
    1 => array(
        "mapurl" => "/data/agclimate/air-temp-out.png",
        "desc" => "High and low air temperature for a local day. Measurements are 
            made at a 2 meter height.",
    ),
    2 => array(
        "mapurl" => "/data/agclimate/4in-temp-out.png",
        "desc" => "Average 4 inch soil depth temperature.  Usually under a 
            bare soil.",
    ),
    3 => array(
        "mapurl" => "/data/agclimate/soil-hilo-out.png",
        "desc" => "High and low 4 inch soil depth temperature.  Usually under a 
            bare soil.",
    ),
    4 => array(
        "mapurl" => "/data/agclimate/rad-out.png",
        "desc" => "Daily total (direct + diffuse) solar radiation.",
    ),
    5 => array(
        "mapurl" => "/data/agclimate/prec-out.png",
        "desc" => "Daily total precipitation.  This is measured with a <b>non-heated</b> tipping bucket located near the ground.  These reported values should be
used with extreme caution.  For various reasons, the reported values are 
often too low.",
    ),
    6 => array(
        "mapurl" => "/data/agclimate/et-out.png",
        "desc" => "Potential maximum estimated evapotranspiration.  This value uses
            a daily Penman formulation with a crop coefficient of 1.",
    ),
    7 => array(
        "mapurl" => "/data/agclimate/pk-wind-out.png",
        "desc" => "Peak 5 second sustained wind gust.  The value is presented along
      with the time using a 24 hour clock.  For example, 18:00 would be 6 PM.
      Values are in local time, either CDT or CST depending on the time of
      year.",
    ),
    8 => array(
        "mapurl" => "/data/agclimate/avewind-out.png",
        "desc" => "Average wind speed for the day as recorded by the data logger
            on the station.",
    ),
    10 => array(
        "mapurl" => "/GIS/apps/agclimate/month.php?dvar=dailyet&year=$year&month=$month",
        "desc" => "Monthly total of daily maximum potential evapotranspiration. The
            daily value is calculated via a Penman formulation with a crop
            coefficient of 1.  The value would be a theoretical maximum."
    ),
    11 => array(
        "mapurl" => "/GIS/apps/agclimate/month.php?dvar=rain_in_tot&year=$year&month=$month",
        "desc" => "Monthly total of daily reported precipitation. This is measured with a <b>non-heated</b> tipping bucket located near the ground.  These reported values should be
used with extreme caution.  For various reasons, the reported values are 
often too low."
    ),
    12 => array(
        "mapurl" => "/data/agclimate/chill-sum.png",
        "desc" => "The Standard Chill Unit map is a summation of hours during 
   which the temperature was between 32 and 45 degrees <b>after</b> 
   1 September.  The value has application for 
   fruit growers in the state.  The departure from average is also 
   presented.  This average is computed from the observational record at
   the site."
    ),
);

$extra = "";
if ($prod == 10 || $prod == 11) {
    $extra .= "<form method='GET' name='ts'>";
    $extra .= "<input type='hidden' value='$prod' name='prod'>";
    $extra .= "<strong>Select Year: </strong>" . yearSelect(1987, $year);
    $extra .= "<strong>Select Month: </strong>" . monthSelect($month, "month");
    $extra .= "<input type='submit' value='Update Plot' />";
    $extra .= '</form>';
}

$t->content = <<<EOM
<table style="float: left;" width="100%">
<tr>
<td valign="top">
{$extra}

<img src="{$data[$prod]["mapurl"]}" ALT="ISU Ag Climate" style="border: 1px solid #000; ">

<p><strong>Plot Description:</strong><br />
{$data[$prod]["desc"]}

<p><strong>QC Flags:</strong>
<table>
<tr>
  <th>M</th>
  <td>the data is missing</td></tr>

<tr>
  <th>E</th>
  <td>An instrument may be flagged until repaired</td></tr>

<tr>
  <th>R</th>
  <td>Estimate based on weighted linear regression from surrounding stations</td></tr>

<tr>
  <th>e</th>
  <td>We are not confident of the estimate</td></tr>

</table>
</td>
<td valign="TOP" width="250">

<div id="right">
<table width="100%" cellspacing="0" cellpadding="1">
<tr>
  <td class="heading">
     <b>Yesterday values:</b></td></tr>
<tr>
  <td>
<div style="padding: 5px;">
  <A HREF="display.php?prod=1">Max/Min Air Temps</A><br>
  <A HREF="display.php?prod=2">Avg 4in Soil Temps</A><br>
  <A HREF="display.php?prod=3">Max/Min 4in Soil Temps</A><br>
  <a href="/data/soilt_day1.png">County-based Soil Temps</a><br />
  <A HREF="display.php?prod=4">Solar Radiation Values</A><br>
  <A HREF="display.php?prod=5">Precipitation</A><br>
  <A HREF="display.php?prod=6">Potential E-T</A><br>
  <A HREF="display.php?prod=7">Peak Wind Gust (5 sec)</A><br>
  <A HREF="display.php?prod=8">Average Wind Speed</A><br>
</div>
  </td>
</tr>

<tr>
  <td class="heading">
     <b>Accumulated values:</b></td></tr>
<tr>
  <td>
<div style="padding: 5px;">
      <A HREF="display.php?prod=10">Monthly evapotranspiration</A><br>
      <A HREF="display.php?prod=11">Monthly rainfall</A><br>
      <A HREF="display.php?prod=12">Standard Chill Units since 1 Sept</A><br>
</div>
  </td>
</tr>

<tr>
  <td class="heading">
     <b>Data Applications:</b></td></tr>
<tr><td>
<div style="padding: 5px;">
  <a href="/GIS/apps/agclimate/gsplot.phtml">Growing Season Maps</a><br>
  <a href="/plotting/auto/?q=177">Time Series Charts</a><br>
  <a href="soilt-prob.php">4in Soil Temperatures</a><br>
  <A HREF="/plotting/auto/?q=199">Daily Data Plotter</a><br>
</div>
  </td>
</tr>

<tr>
  <td class="heading">
     <b>Data Request:</b></td></tr>
<tr>
  <td>
<div style="padding: 5px;">
   <A HREF="/agclimate/hist/hourlyRequest.php">Request Hourly Data</A><br>
   <A HREF="/agclimate/hist/dailyRequest.php">Request Daily Data</A><br>
</div>
  </td>
</tr>

</table>
</div>

</td></tr>
</table>

<br clear="all" /><p>&nbsp;</p>
EOM;
$t->render('single.phtml');
