<?php
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_led.php";

function dwpf($tmpf, $relh)
{
    $tmpk = 273.15 + (5.00 / 9.00 * ($tmpf - 32.00));
    $dwpk = $tmpk / (1 + 0.000425 * $tmpk * - (log10($relh / 100)));
    return round(($dwpk - 273.15) * 9.00 / 5.00 + 32, 2);
}


function read_data($dt, $candie = TRUE) {
    $dirRef = date("Y/m/d", $dt);
    $fn = "/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat";
    $data = array();
    $data["times"] = array();
    $data["tmpf"] = array();
    $data["rh"] = array();
    $data["dwpf"] = array();
    $data["max_tmpf"] = -99;
    $data["min_tmpf"] = 999;
    $data["max_gust"] = -99;
    $data["max_gust_time"] = "";
    $data["baro"] = array();
    $data["mph"] = array();
    $data["gust"] = array();
    $data["drct"] = array();
    $data["inTmpf"] = array();
    $data["inDwpf"] = array();
    $data["inRh"] = array();
    $data["precip"] = array();


    if (!file_exists($fn)) {
        if ($candie) {
            $led = new DigitalLED74();
            $led->StrokeNumber('NO DATA FOR THIS DATE', LEDC_GREEN);
            die();
        }
        return $data;
    }
    $fcontents = file($fn);

    foreach ($fcontents as $line_num => $line) {
        $parts = explode(" ", $line);
        // Ensure we have enough tokens
        if (count($parts) < 19) {
            continue;
        }
        $linedt = strtotime(sprintf(
            "%s %s %s %s %s",
            $parts[0],
            $parts[1],
            $parts[2],
            $parts[3],
            $parts[4]
        ));
        // Ensure that the date matches the requested dt as sometimes
        // timestamps leak
        if ($linedt < $dt || $linedt >= ($dt + 86400)) {
            continue;
        }
        $data["times"][] = $linedt;

        $thisTmpf = $parts[5];
        $thisrh = $parts[8];
        $thisDwpf = dwpf($thisTmpf, $thisrh);
        if ($thisTmpf < -50 || $thisTmpf > 150) {
            $thisTmpf = "";
            $thisDwpf = "";
        }
        $data["tmpf"][] = $thisTmpf;
        $data["dwpf"][] = $thisDwpf;
        $data["rh"][] = $thisrh;

        // Max/Min
        if ($thisTmpf > $data["max_tmpf"]) {
            $data["max_tmpf"] = $thisTmpf;
        }
        if ($thisTmpf < $data["min_tmpf"]) {
            $data["min_tmpf"] = $thisTmpf;
        }

        $thisMPH = intval($parts[9]);
        $thisDRCT = intval($parts[10]);

        if ($line_num % 5 == 0){
        $data["drct"][] = $thisDRCT;
        }else{
        $data["drct"][] = "-199";
        }
        $data["mph"][] = $thisMPH;

        $gust = floatval($parts[11]);
        $data["gust"][] = $gust;
        $gust_time = $parts[12];
        if ($gust > $data["max_gust"]) {
            $data["max_gust"] = $gust;
            $data["max_gust_time"] = $gust_time;
        }

        $data["precip"][] = floatval($parts[14]);

        // Inside
        $inTmpf = floatval($parts[17]);
        $inRH = floatval($parts[18]);
        $inDwpf = dwpf($inTmpf, $inRH);

        $data["inTmpf"][] = $inTmpf;
        $data["inDwpf"][] = $inDwpf;
        $data["inRh"][] = $inRH;

        // Barometer
        $value = $parts[13];
        $value = round((floatval($value) * 33.8639), 2);
        if ($value < 900 || $value > 1100) {
            $value = "";
        }
        $data["baro"][] = $value;
    } // End of while

    return $data;
}
