<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Information";
$t->content = <<<EOF

<h3>Iowa Environmental Mesonet</h3>

<p><strong>Last Updated:</strong> 2 February 2024</p>

<br><div><h3>Background</h3>
<p>The Iowa Environmental Mesonet [IEM] aims to gather, collect,
compare, disseminate and archive observations made in Iowa and beyond.  Unlike other 
mesonet projects, the IEM does not own or operate any of the automated stations.
Rather, the IEM collects data from existing public resources.  The result
is a low-cost, high resolution mesonet for use in a wide 
range of disciplines.</p>

<p>One of the first questions we are often asked is, 'What does
Mesonet mean?' <i>Meso-net</i> is a combination of two meteorological
terms.  <i>Meso</i> refers to a spatial scale on which Meteorologists
define certain weather phenomena. In the context of an observing network,
<i>meso</i> refers to a spatial scale at which a network of sensors can
resolve mesoscale phenomena.  Mesonet implies a spatially and temporarily
dense set of observing stations.</p>

<br><h3>Partners</h3>
<p>The IEM would not be possible without the generous cooperation
and support from federal, state and local agencies as well as the private 
sector.  These groups have been very supportive of the IEM and responsive to
requests made by the IEM. Among these include...
<ul>
 <li>Iowa Department of Transportation [IaDOT]</li>
 <li>Iowa State University & Department of Agronomy [ISU]</li>
 <li>Various broadcast TV stations</li>
 <li>National Weather Service [NWS]</li>
</ul>

<br><h3>Data Networks</h3>
<p>As of the year 2024, the IEM is gathering information from the following:
<ul>
 <li>Automated Surface Observing System [<a href="/ASOS/">ASOS/AWOS</a>]</li>
 <li>Cooperative Observer Program [<a href="/COOP/">COOP</a>]</li>
 <li>Community Collaborative Rain, Hail and Snow Network [<a href="https://cocorahs.org">CoCoRaHS</a>]</li>
 <li>River Gauges / Data Collection Platforms [<a href="/DCP/">DCP</a>]</li>
 <li>Iowa State University Soil Moisture Network [<a href="/agclimate">ISUAG</a>]</li>
 <li>Roadway Weather Information System [<a href="/RWIS/">RWIS</a>]</li>
 <li>Soil Climate Analysis Network [<a href="/scan/">SCAN</a>]</li>
 <li>US Climate Reference Network [<a href="/current/uscrn.phtml">USCRN</a>]</li>
</ul></p>

<p>Clearly, the aforementioned list provides a wide range of
measurements for the state of Iowa.  The networks have <b>not</b> been
developed for similar purposes.  The ASOS/AWOS stations are located at
Airports in support of aviation and weather prediction.  The SCAN site
provides detailed information about soil conditions and has no direct
application for use in aviation.  The RWIS sites are located near major
highways and provide pavement temperatures for frost forecasting and
chemical application guidance.  The ISUAG sites primarily monitor soil
temperatures and augment precipitation observations in the state. 
 The DCP network provides river gauging needed
for flood prediction and observation.  The COOP provides a daily weather 
record for climatological use.</p>

<p>If you put all of these networks together, you can see the value
that each network brings.  Combining them into one product is very
difficult, hence the need for the IEM.  Sites in different networks are 
not always similar in reporting
routines.  For example, many stations report wind information, but not 
every station is
at the same height or not every station averages the same way or not every
station reports in the same units.  These issues are important to consider
before beginning any quality control work.</p>


<p>If you have any questions or comments, please
<a href="contacts.php">let us know</a>.

EOF;
$t->render('single.phtml');
