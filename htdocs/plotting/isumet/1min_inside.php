<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/mlib.php";
require_once "../../../include/forms.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
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

$titleDate = date("M d, Y", $myTime);
$dirRef = date("Y/m/d", $myTime);

$prec = array();
$tmpf = array();
$dwpf = array();
$relh = array();

if ($station == null) {
    $fn = "/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat";
    if (!file_exists($fn)){
        die("File not found");
    }
    $fcontents = file($fn);
    foreach ($fcontents as $line_num => $line) {
        $parts = preg_split("/\s+/", $line);
        $valid[] = strtotime(substr($line, 0, 26));
        $tmpf[] = round(substr($line, 31, 5), 2);
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
        $tmpf[] = $tokens[17];
        $relh[] = $tokens[18];
        $dwpf[] = dwpf($tokens[17], $tokens[18]);
    } // End of while

}

// Create the graph. These two calls are always required
$graph = new Graph(600, 400, "example1");
$graph->SetScale("datelin");
$graph->img->SetMargin(65, 40, 55, 70);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(1, 0.5);
$graph->title->Set("$titleDate Map Room Temperature & Dew Point");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.2, 0.09);

$graph->title->SetFont(FF_FONT1, FS_BOLD, 14);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->xaxis->SetLabelFormatString("h:i A", true);
$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitleMargin(40);

// Create the linear plot
$lineplot = new LinePlot($tmpf, $valid);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");
$lineplot->SetWeight(3.0);

// Create the linear plot
$lineplot2 = new LinePlot($dwpf, $valid);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(3.0);

$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Stroke();
