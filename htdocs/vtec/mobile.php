<?php
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
$v = get_str404("vtec", "2008-O-NEW-KJAX-TO-W-0048", 25);

header("Location: /vtec/f/$v");
