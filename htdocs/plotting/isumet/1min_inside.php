<?php
include("../../../config/settings.inc.php");
include_once "../../../include/mlib.php";
include_once "../../../include/form.php";
//  1 minute data plotter 

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
    $fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");
    foreach ($fcontents as $line_num => $line) {
        $parts = preg_split("/\s+/", $line);
        $valid[] = strtotime(substr($line, 0, 26));
        $tmpf[] = round(substr($line, 31, 5), 2);
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
        $valid[] = $v;
        $tmpf[] = $tokens[17];
        $relh[] = $tokens[18];
        $dwpf[] = dwpf($tokens[17], $tokens[18]);
    } // End of while

}


include("../../../include/jpgraph/jpgraph.php");
include("../../../include/jpgraph/jpgraph_line.php");
include("../../../include/jpgraph/jpgraph_date.php");

// Create the graph. These two calls are always required
$graph = new Graph(600, 400, "example1");
$graph->SetScale("datelin");
//$graph->SetY2Scale("lin",0,100);
$graph->img->SetMargin(65, 40, 55, 70);

$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->yaxis->scale->ticks->Set(1, 0.5);
//$graph->yscale->SetGrace(10);
$graph->title->Set("$titleDate Map Room Temperature & Dew Point");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.2, 0.09);

$graph->title->SetFont(FF_FONT1, FS_BOLD, 14);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->xaxis->SetLabelFormatString("h:i A", true);
//$graph->y2axis->SetTitle("Relative Humidity [%]");
//$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);
$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitleMargin(48);
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

// Create the linear plot
//$lineplot3=new LinePlot($relh, $valid);
//$lineplot3->SetLegend("Rel Humid");
//$lineplot3->SetColor("black");

// Box for error notations
//[DMF]$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//[DMF]$t1->SetPos(0.4,0.95);
//[DMF]$t1->SetOrientation("h");
//[DMF]$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//[DMF]$t1->SetColor("black");
//[DMF]$graph->AddText($t1);

$graph->Add($lineplot);
$graph->Add($lineplot2);
//$graph->AddY2($lineplot3);
$graph->Stroke();
