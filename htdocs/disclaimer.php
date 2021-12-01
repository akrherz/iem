<?php 
require_once "../config/settings.inc.php";
require_once "../include/myview.php";
$t = new MyView();
$t->title = "Disclaimer";
$t->content = <<< EOF
<h3><i class="fa fa-exclamation-triangle"></i> Disclaimer</h3>

<p>While we use care to provide accurate weather/climatic information,
errors may occur because of equipment or other failure. We therefore provide this
information without any warranty of accuracy. Users of this weather/climate data
do so at their own risk, and are advised to use independent judgement as to 
whether to verify the data presented.</p>

<h3>Usage of IEM Products</h3>

<p>The materials found on this website are in the public domain and may be used
freely by anyone for any lawful purpose.  Attributing the Iowa Environmental
Mesonet of Iowa State University would be appreciated.</p>

<p>The IEM is a volunteer effort and receives no funds for facilities or
staff from Iowa State University or the State of Iowa.  Users of the IEM
must therefore recognize that the IEM may be discontinued at any time
with little or no notice.</p>

EOF;
$t->render('single.phtml');
?>