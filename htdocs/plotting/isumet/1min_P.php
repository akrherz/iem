<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_date.php";

$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$station = isset($_REQUEST['station']) ? xssafe($_REQUEST['station']) : null;

if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0) {
    $myTime = strtotime($year . "-" . $month . "-" . $day);
} else {
    $myTime = strtotime(date("Y-m-d"));
}

$titleDate = date("M d, Y", $myTime);
$dirRef = date("Y/m/d", $myTime);


$prec = array();
$valid = array();

if (is_null($station)) {
    $firstval = null;
    $fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");
    foreach ($fcontents as $line_num => $line) {
        $valid[] = strtotime(substr($line, 0, 26));
        $parts = preg_split("/\s+/", $line);
        $val = floatval($parts[10]) / 100.;
        if ($firstval == null) $firstval = $val;
        $prec[] = $val - $firstval;
    } // End of while
} else {
    $fn = "/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0010.dat";
    if (!file_exists($fn)){
        die("File not found");
    }
    $fcontents = file($fn);

    /*
     * month, day, year, hour, minute, outside temp, hi outside temp, lo outside
       temp, outside humidity, wind speed, wind direction, wind gust speed, time
         of gust, pressure, daily_precip, monthly_rain, yearly_rain, inside
         temp, inside humidity, solar radiation, UV index
     */
    foreach ($fcontents as $line_num => $line) {
        $tokens = explode(' ', $line);
        if (sizeof($tokens) != 21) {
            continue;
        }
        $tstring = sprintf("%s %s %s %s", $tokens[0], $tokens[1], $tokens[2], $tokens[3]);
        $v = strtotime($tstring);

        if ($v < $myTime || trim($tstring) == "") {
            continue;
        }
        $valid[] = $v;
        $prec[] = floatval($tokens[14]) / 100.;
    } // End of while

}

// Create the graph. These two calls are always required
$graph = new Graph(600, 400, "example1");

$graph->SetScale("datelin");
$graph->img->SetMargin(55, 40, 55, 60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->title->Set(" Time Series");
$graph->subtitle->Set($titleDate);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01, 0.08);

//$graph->yaxis->scale->ticks->SetPrecision(2);

$graph->yscale->SetGrace(10);
$graph->yaxis->SetColor("blue");
$graph->xaxis->SetLabelAngle(90);
$graph->title->SetFont(FF_FONT1, FS_BOLD, 14);
$graph->yaxis->SetTitle("Accumulated Precipitation [inches]");
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(43);
$graph->xaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);
//$graph->SetAxisStyle(AXSTYLE_YBOXIN);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot = new LinePlot($prec, $valid);
$lineplot->SetLegend("Daily Precipitation");
$lineplot->SetColor("blue");
$lineplot->SetWeight(2);

$graph->Add($lineplot);
$graph->Stroke();
