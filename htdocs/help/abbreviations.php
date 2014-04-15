<?php 
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "Abbreviations";
$t->content = <<<EOF

<h3>Help with Abbreviations</h3>

<p>As you may have already noticed, the IEM website is filled with abbreviations!  
	This index should help you decipher them.  If there is an abbreviation that 
	is omitted, please let us know.</p>

<p><b>ASOS</b> -- Automated Surface Observing System
  <div class="def">Used on the IEM to refer to the network of stations sponsored by
  the Federal Aviation Administration, National Weather Service and the 
  Department of Defense.</div></p>


<p><b>AWOS</b> -- Automated Weather Observing System
  <div class="def">Refers to the network of stations administrated by the Federal Aviation
  Administration or owned by local entities.</div></p>

<p><b>COOP</b> -- Cooperative Observer Program
  <div class="def">Network of human observers making daily observations for the
  National Weather Service</div></p>

<p><b>DCP</b> -- Data Collection Platforms</p>

<p><b>DOT</b> -- Department of Transportation</p>

<p><b>FAA</b> -- Federal Aviation Administration</p>

<p><b>IEM</b> -- Iowa Environmental Mesonet<br>
  <div class="def">Web site you are currently visiting. :)</div></p> 

<p><b>ISU AG</b> -- Iowa State University Agricultural Climate Network<br>
  <div class="def">Network of observing stations located at ISU research farms throughout the state.</div></p>
  
<p><b>NEXRAD</b> -- Next Generation Weather Radar system<br>
  <div class="def">Is the network of Weather Surveillance Radar-1988 Doopler
  (WSR-88D) sites.</div></p>
  
<p><b>NRCS</b> -- National Resources Conservation Service
  <div class="def">Part of the US Department of Agriculture.</div></p>
  
<p><b>NWS</b> -- National Weather Service
  <div class="def">The NWS is responsible for public dissemination of 
  weather data, forecasts and warnings.</div></p>
  
<p><b>RWIS</b> -- Roadway Weather Information System
  <div class="def">Owned by the state Department of Transportation, these sensors
  are found along major roads in the state.</div></p>
  
<p><b>RUC2</b> -- Rapid Update Cycle
  <div class="def">Weather forecast model ran at the National Center for
  Environmental Prediction.  This model is executed hourly and generates 12 hour
  forecasts.</div></p>
   
<p><b>SCAN</b> -- Soil Climate Analysis Network
  <div class="def">Operated by the National Resources Conservation Service, these
  stations provide detailed soil observations on multiple levels.</div></p>
  
<p><b>USGS</b> -- United States Geological Survey</p>

<br><br>
EOF;
$t->render('single.phtml');
?>
