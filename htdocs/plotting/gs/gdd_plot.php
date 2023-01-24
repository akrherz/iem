<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/station.php";

require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_plotline.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_bar.php";

$station = isset($_GET['station']) ? $_GET['station'] : "DSM";
$network = isset($_GET['network']) ? $_GET['network'] : 'IA_ASOS';
$year = isset($_GET['year']) ? $_GET['year'] : date("Y");
$smonth = isset($_GET['smonth']) ? $_GET['smonth'] : 5;
$emonth = isset($_GET['emonth']) ? $_GET['emonth'] : 10;
$sday = isset($_GET['sday']) ? $_GET['sday'] : 1;
$eday = isset($_GET['eday']) ? $_GET['eday'] : 1;
$sts = mktime(0, 0, 0,  $smonth, $sday, $year);
$ets = mktime(0, 0, 0, $emonth, $eday, $year);
if ($ets > time()) {
    $ets = time();
}
$sdate = date("Y-m-d", $sts);
$edate = date("Y-m-d", $ets);
$s2date = date("2000-m-d", $sts);
$e2date = date("2000-m-d", $ets);
$today = time();

$st = new StationData($station, $network);
$climate_site = $st->table[$station]['climate_site'];
$st->loadStation($climate_site);
$cities = $st->table;
$coopdb = iemdb("coop");
$iem = iemdb("iem");

function calcGDD($high, $low)
{
    if ($low < 50)  $low = 50.00;
    if ($high > 86) $high = 86.00;
    if ($high < 50) return 0.00;
    return (($high + $low) / 2.00) - 50.00;
}
if (strrpos($network, "CLIMATE") > 0) {
    $rs = pg_prepare($coopdb, "SELECT", "SELECT high as max_tmpf, low as min_tmpf, day from 
    alldata_" . substr($climate_site, 0, 2) . "
        WHERE station = $1 and day between $2 and $3 " .
        " ORDER by day ASC");
    $rs = pg_execute($coopdb, "SELECT", array($station, $sdate, $edate));
} else {
    $rs = pg_prepare($iem, "SELECT", "SELECT max_tmpf, min_tmpf, day from summary_$year s JOIN stations t
    ON (t.iemid = s.iemid) 
        WHERE id = $1 and day between $2 and $3 " .
        "and network = $4 ORDER by day ASC");
    $rs = pg_execute($iem, "SELECT", array($station, $sdate, $edate, $network));
}

$obs = array();
$aobs = array();
$atot = 0;
$atimes = array();
$zeros = array();
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $hi = (float)$row["max_tmpf"];
    $lo = (float)$row["min_tmpf"];
    $gdd = calcGDD($hi, $lo);
    $atot += $gdd;
    $aobs[$i] = $atot;
    $obs[$i] = $gdd;
    $zeros[$i] = 0;
    $atimes[$i] = strtotime("2000-" . substr($row["day"], 5, 15));
}

/* Now we need the climate data */
$q = "SELECT gdd50, valid from climate
        WHERE station = '" . $climate_site . "' and valid between '$s2date' and
        '$e2date'
        ORDER by valid ASC";

$rs = pg_exec($coopdb, $q);
$climate = array();
$cdiff = array();
$aclimate = array();
$atot = 0;
$times = array();
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $gdd = (float)$row["gdd50"];
    $atot += $gdd;
    if (@$aobs[$i] > 0) {
        $cdiff[$i] = $aobs[$i] - $atot;
    } else $cdiff[$i] = "";
    $aclimate[$i] = $atot;

    $times[$i] = strtotime($row["valid"]);
}

pg_close($coopdb);

// Create the graph. These two calls are always required
$graph = new Graph(640, 480, "example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(45, 10, 80, 60);
$graph->xaxis->SetFont(FF_FONT1, FS_BOLD);
$graph->yaxis->SetTitleMargin(30);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->SetLabelAngle(90);

$graph->yaxis->SetTitle("Growing Degree Days");
$graph->title->Set($cities[$station]["name"] . " [$station] Growing Degree Days (base=50) for $year");
$graph->subtitle->Set("Climate Site: " . $cities[$climate_site]["name"] . "[" . $climate_site . "]");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

foreach ($times as $k => $v) {
    if (date("d", $v) == 1)
        $graph->AddLine(new PlotLine(VERTICAL, $v, "tan", 1));
}

// Create the linear plot
$b1plot = new BarPlot($cdiff, $times);
$b1plot->SetLegend("Accum Difference");

// Create the linear plot
$lp1 = new LinePlot($aobs, $atimes);
$lp1->SetLegend("Actual Accum");
$lp1->SetColor("blue");
$lp1->SetWeight(3);

$lp2 = new LinePlot($aclimate, $times);
$lp2->SetLegend("Climate Accum");
$lp2->SetColor("red");
$lp2->SetWeight(3);

$z = new LinePlot($zeros, $atimes);
$z->SetWeight(3);

// Add the plot to the graph
$graph->Add($lp1);
$graph->Add($lp2);
$graph->Add($b1plot);
$graph->Add($z);

// Display the graph
$graph->Stroke();
