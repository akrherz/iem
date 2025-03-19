<?php
// Cool.....

require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
$nt = new NetworkTable("IA_ASOS");
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_led.php";

$station = isset($_GET["station"]) ? xssafe($_GET["station"]) : "";
$year = get_int404("year", date("Y", time() - 86400));
$month = get_int404("month", date("m", time() - 86400));
$day = get_int404("day", date("d", time() - 86400));

$myTime = strtotime($year . "-" . $month . "-" . $day);

$titleDate = date("M d, Y", $myTime);
$tableName = sprintf("t%s", date("Y_m", $myTime));
$sqlDate = date("Y-m-d", $myTime);

$connection = iemdb("awos");
$stname = iem_pg_prepare($connection, "SELECT " .
    "to_char(valid, 'HH24:MI') as tvalid, p01i, alti from " .
    "alldata WHERE station = $1 and " .
    "valid >= $2 and valid < $3 ORDER by tvalid");

$result = pg_execute($connection, $stname, array($station, $sqlDate, $sqlDate . " 23:59:59"));

if (pg_num_rows($result) == 0) {
    $led = new DigitalLED74();
    $led->StrokeNumber('NO DATA FOR THIS DATE', LEDC_GREEN);
    die();
}

$prec = array();
$alti = array();
$xlabel = array();

$start = intval($myTime);
$i = 0;

$dups = 0;
$missing = 0;
$accumP = 0;
$lastP = 0;

for ($p = 0; $row = pg_fetch_assoc($result); $p++) {
    $strDate = $sqlDate . " " . $row["tvalid"];
    $timestamp = strtotime($strDate);

    $thisALTI = $row["alti"] * 33.8639;
    $thisPREC = $row["p01i"];
    if ($thisALTI < 800) {
        $thisALTI = "";
    }

    if ($thisPREC > $lastP) {
        $accumP = $accumP + $thisPREC - $lastP;
        $lastP = $thisPREC;
    } else if ($thisPREC < $lastP) { // RESET
        $accumP = $accumP + $thisPREC;
        $lastP = $thisPREC;
    }
    #  echo $thisPREC ." - ". $accumP ." - ". $lastP ."<br>\n";

    $shouldbe = intval($start) + 60 * $i;

    #  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;

    // We are good, write data, increment i
    if ($shouldbe == $timestamp) {
        #    echo " EQUALS <br>";
        $prec[$i] = $accumP;
        $alti[$i] = $thisALTI;
        $i++;
        continue;

        // Missed an ob, leave blank numbers, inc i
    } else if (($timestamp - $shouldbe) > 0) {
        #    echo " TROUBLE <br>";
        $tester = $shouldbe + 60;
        while ($tester <= $timestamp) {
            $tester = $tester + 60;
            $prec[$i] = $accumP;
            $alti[$i] = "";

            $i++;
            $missing++;
        }
        $prec[$i] = $accumP;
        $alti[$i] = $thisALTI;
        $i++;
        continue;

        $p--;
    } else if (($timestamp - $shouldbe) < 0) {
        #    echo "DUP <br>";
        $dups++;
    }
} // End of while

$xpre = array(
    0 => '12 AM',
    '1 AM',
    '2 AM',
    '3 AM',
    '4 AM',
    '5 AM',
    '6 AM',
    '7 AM',
    '8 AM',
    '9 AM',
    '10 AM',
    '11 AM',
    'Noon',
    '1 PM',
    '2 PM',
    '3 PM',
    '4 PM',
    '5 PM',
    '6 PM',
    '7 PM',
    '8 PM',
    '9 PM',
    '10 PM',
    '11 PM',
    'Midnight'
);


for ($j = 0; $j < 24; $j++) {
    $xlabel[$j * 60] = $xpre[$j];
}



// Create the graph. These two calls are always required
$graph = new Graph(600, 300, "example1");
$graph->SetScale("textlin");
$graph->SetY2Scale("lin", 0, $accumP + 1.00);
$graph->img->SetMargin(55, 40, 55, 60);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($nt->table[$station]['name'] . " Time Series");
$graph->subtitle->Set($titleDate);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01, 0.07);

//$graph->yaxis->scale->ticks->Set(90,15);
$graph->y2axis->scale->ticks->Set(1, 0.25);

$graph->yaxis->SetColor("black");
$graph->yscale->SetGrace(10);
$graph->y2axis->SetColor("blue");

$graph->yaxis->SetTitle("Altimeter [mb]");
$graph->y2axis->SetTitle("Accumulated Precipitation [inches]");

$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(43);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot = new LinePlot($alti);
$graph->Add($lineplot);
$lineplot->SetLegend("Altimeter");
$lineplot->SetColor("black");

// Create the linear plot
$lineplot2 = new LinePlot($prec);
$graph->AddY2($lineplot2);
$lineplot2->SetLegend("Precipitation");
$lineplot2->SetColor("blue");
//$lineplot2->SetFilled();
//$lineplot2->SetFillColor("blue");

// Box for error notations
$t1 = new Text("Dups: " . $dups . " Missing: " . $missing);
$t1->SetPos(0.4, 0.95);
$t1->SetOrientation("h");
//$t1->SetBox("white","black",true);
$t1->SetColor("black");
$graph->AddText($t1);

$graph->Stroke();
