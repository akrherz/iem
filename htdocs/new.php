<?php
require '../config/settings.inc.php';
define("IEM_APPID", 1);
include_once('../include/myview.php');

$t = new MyView();
$t->friends = array(
    'Rachel', 'Monica', 'Phoebe', 'Chandler', 'Joey', 'Ross'
);
$t->render('homepage.phtml');
?>
