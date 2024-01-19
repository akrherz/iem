<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";
require_once "../../../include/mlib.php";
require_once "../../../include/network.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_bar.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_led.php";

/** We need these vars to make this work */
$subc = isset($_GET["subc"]) ? $_GET["subc"] : "";
$dwpf = isset($_GET["dwpf"]) ? $_GET["dwpf"] : "";
$tmpf = isset($_GET["tmpf"]) ? $_GET["tmpf"] : "";
$pcpn = isset($_GET["pcpn"]) ? $_GET["pcpn"] : "";
$s0 = isset($_GET["s0"]) ? $_GET["s0"] : "";
$s1 = isset($_GET["s1"]) ? $_GET["s1"] : "";
$s2 = isset($_GET["s2"]) ? $_GET["s2"] : "";
$s3 = isset($_GET["s3"]) ? $_GET["s3"] : "";
$syear = get_int404("syear", date("Y"));
$smonth = get_int404("smonth", date("m"));
$sday = get_int404("sday", date("d"));
$days = get_int404("days", 2);
$station = isset($_GET['station']) ? xssafe($_GET["station"]) : "";
$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_RWIS";

/** Lets assemble a time period if this plot is historical */
$sts = new DateTime("$syear-$smonth-$sday");
$ets = new DateTime("$syear-$smonth-$sday");
$ets->modify("+$days days");

if (isset($_GET["limit"])) $val = "between 25 and 35";

$rwisdb = iemdb('rwis');
$rs = pg_prepare($rwisdb, "OBS", "
 SELECT * FROM alldata WHERE 
 station = $1 and valid >= $2 and valid < $3 
 ORDER by valid ASC");
$minInterval = 20;
$result = pg_execute($rwisdb, "OBS", array($station, $sts->format("Y-m-d H:i"), $ets->format("Y-m-d H:i")));

$minInterval = 20;

$rs = pg_prepare($rwisdb, "META", "SELECT * from sensors WHERE station = $1");
$r1 = pg_execute($rwisdb, "META", array($station));

$ns0 = "Sensor 1";
$ns1 = "Sensor 2";
$ns2 = "Sensor 3";
$ns3 = "Sensor 4";
if (pg_num_rows($r1) > 0) {
    $row = pg_fetch_array($r1);
    $ns0 = $row['sensor0'];
    $ns1 = $row['sensor1'];
    $ns2 = $row['sensor2'];
    $ns3 = $row['sensor3'];
}

if (pg_num_rows($result) == 0) {
    $led = new DigitalLED74();
    $led->StrokeNumber('NO DATA AVAILABLE', LEDC_GREEN);
    die();
}


$tfs0 = array();
$tfs1 = array();
$tfs2 = array();
$tfs3 = array();
$pcpn = array();
$Asubc = array();
$Atmpf = array();
$Adwpf = array();
$freezing = array();
$times = array();

function checker($v)
{
    if ($v == "") {
        return $v;
    }
    if (floatval($v) > 200) {
        return '';
    }
    return $v;
}

$lastp = 0;
for ($i = 0; $row = pg_fetch_array($result); $i++) {
    $times[] = strtotime(substr($row["valid"], 0, 16));
    $tfs0[] = checker($row["tfs0"]);
    $tfs1[] = checker($row["tfs1"]);
    $tfs2[] = checker($row["tfs2"]);
    $tfs3[] = checker($row["tfs3"]);
    $Asubc[] = checker($row["subf"]);
    $Atmpf[] = checker($row["tmpf"]);
    $Adwpf[] = checker($row["dwpf"]);
    $p = floatval($row["pcpn"]);
    $newp = 0;
    if ($p > $lastp) {
        $newp = $p - $lastp;
    }
    if ($p < $lastp && $p > 0) {
        $newp = $p;
    }
    $pcpn[] = $newp;
    $lastp = $p;
    $freezing[] = 32;
}
pg_close($rwisdb);

$nt = new NetworkTable($network);
$cities = $nt->table;

// Create the graph. These two calls are always required
$graph = new Graph(800, 600);
$graph->SetScale("datlin");
$graph->SetMarginColor("white");
$graph->SetColor("lightyellow");
if (max($pcpn) != "" && isset($_GET["pcpn"])) $graph->SetY2Scale("lin");
if (isset($limit))  $graph->SetScale("datlin", 25, 35);
$graph->img->SetMargin(40, 55, 105, 115);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

if (max($pcpn) != "" && isset($_GET["pcpn"])) {
    $graph->y2axis->SetTitle("Precipitation [inch]");
    $graph->y2axis->SetTitleMargin(40);
}

$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1, FS_BOLD, 12);

$graph->xaxis->SetTitle("Time Period: " . date('Y-m-d h:i A', $times[0]) . " thru " . date('Y-m-d h:i A', max($times)));
$graph->xaxis->SetTitleMargin(90);
$graph->xaxis->title->SetColor("brown");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M-j h A", true);

$graph->legend->Pos(0.01, 0.01);
$graph->legend->SetLayout(LEGEND_VERT);

// Create the linear plot
$lineplot = new LinePlot($tfs0, $times);
$lineplot->SetLegend("0: " . $ns0);
$lineplot->SetColor("blue");
$lineplot->SetWeight(3);

// Create the linear plot
$lineplot2 = new LinePlot($tfs1, $times);
$lineplot2->SetLegend("1: " . $ns1);
$lineplot2->SetColor("pink");
$lineplot2->SetWeight(3);

// Create the linear plot
$lineplot3 = new LinePlot($tfs2, $times);
$lineplot3->SetLegend("2: " . $ns2);
$lineplot3->SetColor("gray");
$lineplot3->SetWeight(3);

// Create the linear plot
$lineplot4 = new LinePlot($tfs3, $times);
$lineplot4->SetLegend("3: " . $ns3);
$lineplot4->SetColor("purple");
$lineplot4->SetWeight(3);

// Create the linear plot
$lineplot5 = new LinePlot($Asubc, $times);
$lineplot5->SetLegend("Sub Surface");
$lineplot5->SetColor("black");
$lineplot5->SetWeight(3);

// Create the linear plot
$lineplot6 = new LinePlot($Atmpf, $times);
$lineplot6->SetLegend("Air Temperature");
$lineplot6->SetColor("red");
$lineplot6->SetWeight(3);

// Create the linear plot
$lineplot7 = new LinePlot($Adwpf, $times);
$lineplot7->SetLegend("Dew Point");
$lineplot7->SetColor("green");
$lineplot7->SetWeight(3);

$bp1 = new BarPlot($pcpn, $times);
$bp1->SetLegend("Precip");
$bp1->SetFillColor("black");
$bp1->SetAbsWidth(1.0);

// Create the linear plot
$fz = new LinePlot($freezing, $times);
$fz->SetColor("blue");

// Title Box
$tx1 = new Text($cities[$station]['name'] . " \nMeteogram ");
$tx1->SetPos(0.01, 0.01, 'left', 'top');
$tx1->SetFont(FF_FONT1, FS_BOLD, 16);

$tx2 = new Text("Time series showing temperatures
   from the pavement sensors and 
   the sub-surface sensor ");
$tx2->SetPos(0.01, 0.11, 'left', 'top');
$tx2->SetFont(FF_FONT1, FS_NORMAL, 10);

$ptext = "Historical Plot for dates:\n";
$tx3 = new Text($ptext);
$graph->AddText($tx1);
$graph->AddText($tx2);

// Add the plot to the graph
$graph->Add($fz);
if (max($tfs0) != "" && isset($_GET["s0"]))
    $graph->Add($lineplot);
if (max($tfs1) != "" && isset($_GET["s1"]))
    $graph->Add($lineplot2);
if (max($tfs2) != "" && isset($_GET["s2"]))
    $graph->Add($lineplot3);
if (max($tfs3) != "" && isset($_GET["s3"]))
    $graph->Add($lineplot4);
if (max($Asubc) != "" && isset($_GET["subc"]))
    $graph->Add($lineplot5);
if (max($Atmpf) != "" && isset($_GET["tmpf"]))
    $graph->Add($lineplot6);
if (max($Adwpf) != "" && isset($_GET["dwpf"]))
    $graph->Add($lineplot7);

if (max($pcpn) != "" && isset($_GET["pcpn"]))
    $graph->AddY2($bp1);

$graph->Stroke();
