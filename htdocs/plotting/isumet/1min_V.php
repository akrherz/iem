<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";

require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_scatter.php";
require_once "../../../include/jpgraph/jpgraph_date.php";

$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$station = isset($_REQUEST['station']) ? $_REQUEST['station'] : null;

if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0) {
    $myTime = strtotime($year . "-" . $month . "-" . $day);
} else {
    $myTime = strtotime(date("Y-m-d"));
}

$wA = mktime(0, 0, 0, 8, 4, 2002);
$wLabel = "1min Instantaneous Wind Speed";
if ($wA > $myTime) {
    $wLabel = "Instant Wind Speed";
}

$titleDate = date("M d, Y", $myTime);
$dirRef = date("Y/m/d", $myTime);

$mph = array();
$drct = array();
$gust = array();
$valid = array();

if ($station == null) {
    $fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");
    foreach ($fcontents as $line_num => $line) {
        $valid[] = strtotime(substr($line, 0, 26));
        $parts = preg_split("/\s+/", $line);
        $mph[] = intval($parts[8]);
        $drct[] = intval($parts[9]);
    } // End of while
} else {
    $fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0010.dat");
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
        $speed = floatval($tokens[9]);
        if ($speed < 0 || $speed > 100) {
            continue;
        }
        $valid[] = $v;
        $mph[] = $speed;
        $drct[] = $tokens[10];
    } // End of while

}


// Create the graph. These two calls are always required
$graph = new Graph(600, 400, "example1");
$graph->SetScale("datelin", 0, 360);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(55, 40, 55, 60);

//$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->title->Set(" Time Series");
$graph->subtitle->Set($titleDate);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01, 0.08);
$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(90, 15);
//$graph->yaxis->scale->ticks->SetPrecision(0);
//$graph->yaxis->scale->ticks->SetPrecision(0);

$graph->yaxis->SetColor("blue");
$graph->y2axis->SetColor("red");

$graph->title->SetFont(FF_FONT1, FS_BOLD, 14);

$graph->yaxis->SetTitle("Wind Direction");
$graph->y2axis->SetTitle("Wind Speed [MPH]");

$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(30);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot = new LinePlot($mph, $valid);
$lineplot->SetLegend($wLabel);
$lineplot->SetColor("red");

// Create the linear plot
$sp1 = new ScatterPlot($drct, $valid);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);


$graph->Add($sp1);
$graph->AddY2($lineplot);

$graph->Stroke();
