<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/mlib.php");

    $relh = relh( 86, 75);
    $feel = heat_idx(86, $relh);
echo $feel;
?>
