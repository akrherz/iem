<?php 
require_once "../../../config/settings.inc.php";

require_once "../../../include/myview.php";

$t = new MyView();
$t->title = "Tall Towers Project";

$t->content = <<<EOF

<h3>ISU Tall Towers Network</h3>
		
<p>This network consists of two 120 meter tall intensely instrumented towers.
	Dr Gene Takle oversees the network.  The IEM is providing data collection
	support for this network.</p>

<p><a href="http://talltowers.agron.iastate.edu">Tall Towers Project Website</a></p>

<h4>Meteorological Data @ 1 Second Resolution</h4>

<p>A <a href="analog_download.php">download interface</a> exists to request
	this data.  You can also <a href="/plotting/auto/?q=158">generate interactive plots</a>
	of this dataset.</p>
		
<h4>Turbulence Data @ 20 Hertz Resolution</h4>

<p>This information is currently only available in NetCDF files.  If you would
like access to them, please email <a href="mailto:gstakle@iastate.edu">Dr Takle (gstakle@iastate.edu)</a>.</p>
	
</p>

EOF;

$t->render('single.phtml');
?>