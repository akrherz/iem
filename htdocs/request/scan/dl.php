<?php
// Automatically forward request with all the parameters to the new location
$uri = sprintf("/cgi-bin/request/scan.py?%s", $_SERVER['QUERY_STRING']);
header("Location: $uri");

