<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
$t = new MyView();
$t->title = "School Net Data Format";
$t->content = <<<EOF

<h3 class="heading">Data Format</h3><br /><br />
<div class="text">

If you download raw schoolnet data from the IEM server, 
you are probably curious about the data format.  Well, here is the explaination.</p>

<p>The data files are in a tab deliminated text format.  
Each line is a different report.  
Here is an example line with columns denoted for reference.<br>
<pre>
20:57,03/06/02,NE,06MPH,000K,460F,028F,077%,30.18R,00.00"D,00.00"M,00.00"R,
  1       2    3    4    5    6    7    8     9      10      11      12
</pre>
</p>

<table>
<tr>
  <th class="subtitle">Column</th>
  <th class="subtitle">Ex</th>
  <th class="subtitle">Data Type / Units </th>
</tr>
<tr colspan="#eeeeee">
  <th class="subtitle">1</th>
  <th class="subtitle">20:57</th>
  <td>Time of Day in the Central Standard Timezone.  Hours are in a two digit
form.  To get the PM equivalent, subtract 12 from numbers larger than 13.  In this example, 20:57 equates to 8:57PM.</td>
</tr>
<tr>
  <th class="subtitle">2</th>
  <th class="subtitle">03/06/02</th>
  <td>Date of the observation in the Central Standard Timezone.  The format is
mm/dd/yy.  In this example, 06 March 2002.</td>
</tr>
<tr>
  <th class="subtitle">3</th>
  <th class="subtitle">NE</th>
  <td>Textual representation of where the wind is blowing from. (Wind Direction)</td>
</tr>
<tr>
  <th class="subtitle">4</th>
  <th class="subtitle">06MPH</th>
  <td>Instaneous wind speed in miles per hour.</td>
</tr>
<tr>
  <th class="subtitle">5</th>
  <th class="subtitle">000K</th>
  <td>Solar Radiation.  Multiply by 10 to get values in Watts per meter squared.</td>
</tr>
<tr>
  <th class="subtitle">6</th>
  <th class="subtitle">460F</th>
  <td>Indoor Temperature in degrees Fahrenhit.  The value of 460F means that 
this variable is not measured at this station or that the value is in error.</td>
</tr>
<tr>
  <th class="subtitle">7</th>
  <th class="subtitle">028F</th>
  <td>Outdoor Temperature in degrees Fahrenhit.</td>
</tr>
<tr>
  <th class="subtitle">8</th>
  <th class="subtitle">077%</th>
  <td>Humidity expressed as a precentage.</td>
</tr>
<tr>
  <th class="subtitle">9</th>
  <th class="subtitle">30.18R</th>
  <td>Barometric pressure expressed in inches of mercury.  The character at 
the end represents the change in pressure. 'S' == Steady.  'R' == Raising.
'F' == Falling.</td>
</tr>
<tr>
  <th class="subtitle">10</th>
  <th class="subtitle">00.00"D</th>
  <td>Accumulation of precipitation in inches for the current day.</td>
</tr>
<tr>
  <th class="subtitle">11</th>
  <th class="subtitle">00.00"M</th>
  <td>Accumulation of precipitation in inches for the current month.</td>
</tr>
<tr>
  <th class="subtitle">12</th>
  <th class="subtitle">00.00"R</th>
  <td>Calculated current hourly precipitation rate.</td>
</tr>
</table></div>
EOF;
$t->render('single.phtml');
?>