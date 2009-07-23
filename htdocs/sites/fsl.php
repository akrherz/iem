<?php
/* Special script that GSD MADIS calls to get schoolnet station tables
 * for them to see what has updated
 */
header("Content-type: text/plain");

readfile("http://localhost/sites/networks.php?network=KCCI&format=madis&nohtml=on");
readfile("http://localhost/sites/networks.php?network=KELO&format=madis&nohtml=on");
readfile("http://localhost/sites/networks.php?network=KIMT&format=madis&nohtml=on");

?>
