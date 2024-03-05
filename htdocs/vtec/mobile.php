<?php
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
$v = isset($_GET["vtec"]) ? substr(xssafe($_GET["vtec"]), 0, 25) : "2008-O-NEW-KJAX-TO-W-0048";

header("Location: /vtec/f/$v");
