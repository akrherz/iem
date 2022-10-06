<?php
/*
 * This is the example referenced on the /json/ webpage
 */
require_once "../../include/forms.php";

header('Content-type: application/json; charset=utf-8');

$arr = array(
    "Name" => "daryl",
    "Profession" => "nerd",
    "Age" => 99,
);
$json = json_encode($arr);

// JSON if no callback
if (!isset($_REQUEST['callback']))
    exit($json);

$cb = xssafe($_REQUEST['callback']);
echo "{$cb}($json)";
