<?php 

$fn = sprintf("/mesonet/share/mec/%s.png", $_GET["i"]);
if (! is_file($fn)){
	die("nosuchfile");
}

header("Content-type: image/png");
echo file_get_contents($fn);

?>