<?php header('content-type: application/json; charset=utf-8');


$json = '{"Name": "daryl", "Profession": "nerd", "Age": 99}';

# JSON if no callback
if( ! isset($_GET['callback']))
	exit( $json );

exit( "{$_GET['callback']}($json)" );

?>