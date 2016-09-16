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


<h4>Meteorological Data @ 1 Second Resolution</h4>

<p>This information is freely available from this website.  A
		<a href="analog_download.php">download interface</a> exists to request
		this data.</p>
		
<h4>Turbulence Data @ 20 Hertz Resolution</h4>

<p>This information is available on a password protected website found on the
	<a href="http://talltowers.agron.iastate.edu">Tall Towers Project Website</a>
</p>

EOF;

$t->render('single.phtml');
?>