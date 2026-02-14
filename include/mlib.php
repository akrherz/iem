<?php

/**
 * Convert a vague 3 character WFO identifier to a 4 character one
 * @param wfo3 the 3 character WFO identifier
 * @return the 4 character WFO identifier
 */
function rectify_wfo($wfo3){
    $xref = Array(
        "AFC" => "PAFC",
        "AJK" => "PAJK",
        "AFG" => "PAFG",
        "HFO" => "PHFO",
        "GUM" => "PGUM",
        "SJU" => "TJSJ",
        "JSJ" => "TJSJ",
    );
    if (array_key_exists($wfo3, $xref)){
        return $xref[$wfo3];
    };
    return sprintf("K%s", $wfo3);
}

/**
 * Figure out the vague 3 character ID :/
 * @param wfo3 the 3 character WFO identifier
 * @return the 4 character WFO identifier
 */
function unrectify_wfo($wfo){
    if (strlen($wfo) == 4){
        $wfo = substr($wfo, 1, 3);
    }
    if ($wfo == "SJU"){
        return "JSJ";
    }
    return $wfo;
}


function getClientIp() {
    if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $ipArray = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
        // Likely want the last IP in the list
        $ip = trim(end($ipArray));
    } else {
        $ip = $_SERVER['REMOTE_ADDR'];
    }
    return $ip;
}

// Helper
function printTags($tokens)
{
    if (sizeof($tokens) == 0 || $tokens[0] == "") {
        return "";
    }
    $s = "<br /><span style=\"font-size: smaller; float: left;\">Tags: &nbsp; ";
    foreach ($tokens as $k => $v) {
        $s .= sprintf(
            "<a href=\"/onsite/features/tags/%s.html\">%s</a> &nbsp; ",
            $v,
            $v
        );
    }
    $s .= "</span>";
    return $s;
}


// Workaround round() quirks
function myround($val, $prec){
    if (is_null($val)) return "";
    if (is_string($val)) return $val;
    return round($val, $prec);
}

// Helper to make an IEM webservice call, returns FALSE if fails
function iemws_json($endpoint, $args)
{
    // Everything is method get at the moment
    $cgi = http_build_query($args);
    // Nginx lives here
    $uri = "http://iem-web-services.agron.iastate.edu:8080/{$endpoint}?{$cgi}";
    // Try twice to get the content
    $jobj = FALSE;
    for ($i = 0; $i < 2; $i++) {
        // Use curl to get the data with a 15 second timeout
        $ch = curl_init($uri);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
        curl_setopt($ch, CURLOPT_TIMEOUT, 15);
        $res = curl_exec($ch);
        $http_status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($res === FALSE || $http_status != 200) {
            openlog("iem", LOG_PID | LOG_PERROR, LOG_LOCAL1);
            syslog(LOG_WARNING, "iemws fail[$i] $http_status ".
                "from:" . $_SERVER["REQUEST_URI"] .
                ' remote: ' . getClientIp() .
                ' to: ' . $uri);
            closelog();
            sleep(3);
            continue;
        }
        try {
            $jobj = json_decode($res, $assoc = TRUE);
            break;
        } catch (Exception $e) {
            // Log
            openlog("iem", LOG_PID | LOG_PERROR, LOG_LOCAL1);
            syslog(
                LOG_WARNING,
                "iemws jsonfail  from:" . $_SERVER["REQUEST_URI"] .
                    ' remote: ' . getClientIp() .
                    ' msg: ' . $e .
                    ' to: ' . $uri
            );
            closelog();
        }
    }
    if ($jobj === FALSE) {
        header("Content-type: text/plain");
        http_response_code(503);
        die("Backend web service failure, please try again later.");
    }
    return $jobj;
}

// Make sure a page is HTTPS when called
function force_https()
{
    global $EXTERNAL_BASEURL;
    // Require that EXTERNAL_BASEURL is https, otherwise we have infinite loop
    if (strpos($EXTERNAL_BASEURL, "https://") !== 0) {
        return;
    }
    if (empty($_SERVER["HTTPS"]) || $_SERVER["HTTPS"] !== "on") {
        // Ensure we collapse folks that have bookmarks to aliases
        header("Location: {$EXTERNAL_BASEURL}" . $_SERVER["REQUEST_URI"]);
        exit();
    }
}

//________________________________________________________
function aSortBySecondIndex($multiArray, $secondIndex, $sorder = "asc")
{
    reset($multiArray);
    if (sizeof($multiArray) == 0) {
        return array();
    }
    $indexMap = array();
    foreach ($multiArray as $firstIndex => $value) {
        if (array_key_exists($secondIndex, $value)) {
            $val = $value[$secondIndex];
        } else {
            $val = null;
        }
        $indexMap[$firstIndex] = $val;
    }
    if ($sorder == "asc") {
        asort($indexMap);
    } else {
        arsort($indexMap);
    }
    $sortedArray = array();
    foreach ($indexMap as $firstIndex => $unused) {
        $sortedArray[$firstIndex] = $multiArray[$firstIndex];
    }
    return $sortedArray;
}

//_____________________________________________________________
function c2f($myC)
{
    if ($myC == "") {
        return "";
    }
    return round(((9.00 / 5.00) * $myC + 32.00), 2);
} // End of function c2f()

//_____________________________________________________________
function f2c($tmpf)
{
    if (is_null($tmpf)) return null;
    return round(((5.00 / 9.00) * ((float)$tmpf - 32.00)), 2);
} // End of function f2c()


//______________________________________________________________
function dwpf($tmpf, $relh)
{
    $tmpk = 273.15 + (5.00 / 9.00 * ($tmpf - 32.00));
    $dwpk = $tmpk / (1 + 0.000425 * $tmpk * - (log10($relh / 100)));
    return ($dwpk - 273.15) * 9.00 / 5.00 + 32;
}


//______________________________________________________________
// /home/nawips/nawips56.e.1/gempak/source/gemlib/pr/prvapr.f
// /home/nawips/nawips56.e.1/gempak/source/gemlib/pr/prrelh.f
function relh($tmpc, $dwpc)
{
    if (is_null($tmpc) || is_null($dwpc)) return null;
    $e  = 6.112 * exp((17.67 * (float)$dwpc) / ((float)$dwpc + 243.5));
    $es  = 6.112 * exp((17.67 * (float)$tmpc) / ((float)$tmpc + 243.5));
    $relh = ($e / $es) * 100.00;
    return round($relh, 0);
}


function drct2txt($dir)
{
    $dir = intval($dir);
    $directions = [
        "N" => [350, 360, 0, 13],
        "NNE" => [13, 35],
        "NE" => [35, 57],
        "ENE" => [57, 80],
        "E" => [80, 102],
        "ESE" => [102, 127],
        "SE" => [127, 143],
        "SSE" => [143, 166],
        "S" => [166, 190],
        "SSW" => [190, 215],
        "SW" => [215, 237],
        "WSW" => [237, 260],
        "W" => [260, 281],
        "WNW" => [281, 304],
        "NW" => [304, 324],
        "NNW" => [324, 350]
    ];

    foreach ($directions as $text => $ranges) {
        if (count($ranges) == 4) {
            if (($dir >= $ranges[0] && $dir <= $ranges[1]) || ($dir >= $ranges[2] && $dir < $ranges[3])) {
                return $text;
            }
        } else {
            if ($dir >= $ranges[0] && $dir < $ranges[1]) {
                return $text;
            }
        }
    }

    return "";
}
