
<div id="right">
<table width="100%" cellspacing="0" cellpadding="1">
<tr>
  <td class="heading">
     <b>Yesterday values:</b></td></tr>
<tr>
  <td>
  <A HREF="display.php?prod=1">Max/Min Air Temps</A><br>
  <A HREF="display.php?prod=2">Avg 4in Soil Temps</A><br>
  <A HREF="display.php?prod=3">Max/Min 4in Soil Temps</A><br>
  <A HREF="display.php?prod=4">Solar Radiation Values</A><br>
  <A HREF="display.php?prod=5">Precipitation</A><br>
  <A HREF="display.php?prod=6">Potential E-T</A><br>
  <A HREF="display.php?prod=7">Peak Wind Gust (5 sec)</A><br>
  <A HREF="display.php?prod=8">Average Wind Speed</A><br>
  <A HREF="display.php?prod=9">Max/Min Dew Points</A><br>
  </td>
</tr>

<tr>
  <td class="heading">
     <b>Accumulated values:</b></td></tr>
<tr>
  <td>
      <A HREF="display.php?prod=10">This month evapotranspiration</A><br>
      <A HREF="display.php?prod=11">This month rainfall</A><br>
      <A HREF="display.php?prod=12">Standard Chill Units since 1 Sept</A><br>
  </td>
</tr>

<tr>
  <td class="heading">
     <b>Growing Season:</b></font></td></tr>
<tr>
  <td><a href="<?php echo $rooturl; ?>/GIS/apps/agclimate/gsplot.phtml">Interactive
GS Plotter</a><br>
  </td>
</tr>
<tr>
  <td class="heading">
     <b>Historical Plotting:</b></font></td></tr>
<tr>
  <td>
    <a href="/plotting/agc/">Interactive Plotting</a><br>
    <A HREF="<?php echo $rooturl; ?>/GIS/apps/agclimate/dayplot.phtml">Daily Data Plotter</a><br>
  </td>
</tr>

<tr>
  <td class="heading">
     <b>Data Request:</b></font></td></tr>
<tr>
  <td>
   <A HREF="<?php echo $rooturl; ?>/agclimate/hist/hourlyRequest.php">Request Hourly Data</A><br>
   <A HREF="<?php echo $rooturl; ?>/agclimate/hist/dailyRequest.php">Request Daily Data</A><br>
  </td>
</tr>

</table>
</div>
