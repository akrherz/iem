<?php
include("../../config/settings.inc.php");
/* I produce maps for a given ID
 * 
 */
$id = isset($_GET['id']) ? intval($_GET['id']) : die();

include("$rootpath/include/header.php");

include("$rootpath/include/footer.php");
?>