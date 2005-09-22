<pre>
Output the DB SQL dump corresponding to the Menu Structure

<?php
include ("lib/PHPLIB.php");
include ("lib/layersmenu-common.inc.php");
include ("lib/layersmenu-process.inc.php");
$mid = new ProcessLayersMenu();
$mid->setMenuStructureFile("layersmenu-horizontal-1.txt");
$mid->parseStructureForMenu("hormenu1");
//$mid->setDBConnParms("pgsql://postgres:postgres@localhost/phplayersmenu");
//$mid->setDBConnParms("mysql://mysql:mysql@localhost/phplayersmenu");
//$mid->scanTableForMenu("hormenu1");
print $mid->getSQLDump("hormenu1");
?>

</pre>
