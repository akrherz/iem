<?php
// Automatically forward request with all the parameters to the new location
$uri = sprintf("/cgi-bin/request/asos1min.py?%s", $_SERVER['QUERY_STRING']);
http_response_code(301);
header("Location: $uri");
