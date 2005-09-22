<?php
header("Content-type: text/plain");

readfile("http://mesonet.agron.iastate.edu/sites/networks.php?network=KCCI&format=madis&nohtml=on");
readfile("http://mesonet.agron.iastate.edu/sites/networks.php?network=KELO&format=madis&nohtml=on");
readfile("http://mesonet.agron.iastate.edu/sites/networks.php?network=KIMT&format=madis&nohtml=on");

?>
