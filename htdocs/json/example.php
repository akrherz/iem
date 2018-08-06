<?php 
/*
 * This is the example referenced on the /json/ webpage
 */

header('Content-type: application/json; charset=utf-8');

$json = '{"Name": "daryl", "Profession": "nerd", "Age": 99}';

// JSON if no callback
if( ! isset($_REQUEST['callback']))
	exit( $json );

exit( "{$_REQUEST['callback']}($json)" );

?>