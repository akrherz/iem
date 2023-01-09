<?php
// Helper to make an IEM webservice call, returns FALSE if fails
function iemws_json($endpoint, $args)
{
    // Everything is method get at the moment
    $cgi = http_build_query($args);
    $uri = "https://iem-web-services.agron.iastate.edu/{$endpoint}?{$cgi}";
    // Try twice to get the content
    $jobj = FALSE;
    for ($i = 0; $i < 2; $i++) {
        $res = file_get_contents($uri);
        if ($res === FALSE) {
            openlog("iem", LOG_PID | LOG_PERROR, LOG_LOCAL1);
            syslog(LOG_WARNING, "iemws fail  from:" . $_SERVER["REQUEST_URI"] .
                ' remote: ' . $_SERVER["REMOTE_ADDR"] .
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
                    ' remote: ' . $_SERVER["REMOTE_ADDR"] .
                    ' msg: ' . $e .
                    ' to: ' . $uri
            );
            closelog();
        }
    }
    return $jobj;
}

// Make sure a page is HTTPS when called
function force_https()
{
    if (empty($_SERVER["HTTPS"]) || $_SERVER["HTTPS"] !== "on") {
        header("Location: https://" . $_SERVER["HTTP_HOST"] . $_SERVER["REQUEST_URI"]);
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
    if ($dir >= 350 || $dir < 13)  return "N";
    if ($dir >= 13 && $dir < 35) return "NNE";
    if ($dir >= 35 && $dir < 57) return "NE";
    if ($dir >= 57 && $dir < 80) return "ENE";
    if ($dir >= 80 && $dir < 102) return "E";
    if ($dir >= 102 && $dir < 127) return "ESE";
    if ($dir >= 127 && $dir < 143) return "SE";
    if ($dir >= 143 && $dir < 166) return "SSE";
    if ($dir >= 166 && $dir < 190) return "S";
    if ($dir >= 190 && $dir < 215) return "SSW";
    if ($dir >= 215 && $dir < 237) return "SW";
    if ($dir >= 237 && $dir < 260) return "WSW";
    if ($dir >= 260 && $dir < 281) return "W";
    if ($dir >= 281 && $dir < 304) return "WNW";
    if ($dir >= 304 && $dir < 324) return "NW";
    if ($dir >= 324 && $dir < 350) return "NNW";
    return "";
}
