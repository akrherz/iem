<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/station.php";
require_once "../../../include/forms.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_plotline.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_bar.php";

$station = isset($_GET['station']) ? xssafe($_GET['station']) : "DSM";
$network = isset($_GET['network']) ? xssafe($_GET['network']) : 'IA_ASOS';
$year = get_int404("year", date("Y"));
$smonth = get_int404("smonth", 5);
$emonth = get_int404("emonth", 10);
$sday = get_int404("sday", 1);
$eday = get_int404("eday", 1);
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
$st->loadStation(iemdb("mesosite"), $st->table[$station]['climate_site']);
$cities = $st->table;
$coopdb = iemdb("coop");
$iem = iemdb("iem");

$climate_site = $cities[$station]["climate_site"];

$stname = uniqid("rainfall_plot");
if (strrpos($network, "CLIMATE") > 0) {
    pg_prepare($coopdb, $stname, "SELECT precip as pday, day from 
    alldata WHERE station = $1 and day between $2 and $3 " .
        " ORDER by day ASC");
    $rs = pg_execute($coopdb, $stname, array($station, $sdate, $edate));
} else {
    pg_prepare($iem, $stname, "SELECT pday, day from summary_$year s JOIN stations t
    ON (t.iemid = s.iemid)
        WHERE id = $1 and day between $2 and $3 " .
        "and network = $4 ORDER by day ASC");
    $rs = pg_execute($iem, $stname, array($station, $sdate, $edate, $network));
}

$obs = array();
$aobs = array();
$zeros = array();
$atimes = array();
$atot = 0;
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $p = $row["pday"];
    if ($p < 0) $p = 0;
    $atot += $p;
    $aobs[$i] = $atot;
    $obs[$i] = $p;
    $zeros[$i] = 0;
    $atimes[$i] = strtotime("2000-" . substr($row["day"], 5, 15));
}

/* Now we need the climate data */
$stname = uniqid("select");
pg_prepare(
    $coopdb,
    $stname,
    "SELECT precip, valid from climate WHERE station = $1 ".
    "and valid between $2 and $3 ORDER by valid ASC"
);
$rs = pg_execute($coopdb, $stname, array($climate_site, $s2date, $e2date));
$climate = array();
$cdiff = array();
$aclimate = array();
$atot = 0;

$times = array();
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $p = $row["precip"];
    $climate[$i] = $p;
    $atot += $p;
    if (array_key_exists($i, $aobs) && $aobs[$i] > 0) {
        $cdiff[$i] = $aobs[$i] - $atot;
    } else {
        $cdiff[$i] = "";
    }
    $aclimate[$i] = $atot;
    $xlabels[$i] = "";
    $times[$i] = strtotime($row["valid"]);
}

// Create the graph. These two calls are always required
$graph = new Graph(640, 480, "example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(45, 10, 80, 60);
$graph->xaxis->SetFont(FF_FONT1, FS_BOLD);
$graph->yaxis->SetTitleMargin(30);
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTitle("Day of Month");
//$graph->xaxis->SetTickLabels($xlabels);
$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->SetLabelAngle(90);


$graph->yaxis->SetTitle("Precipitation (in)");
$graph->title->Set($cities[$station]["name"] . " [$station] Precipitation for " . $year);
$graph->subtitle->Set("Climate Site: " . $cities[$climate_site]["name"] . "[" . $climate_site . "]");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

foreach ($times as $k => $v) {
    if (date("d", $v) == 1)
        $graph->AddLine(new PlotLine(VERTICAL, $v, "tan", 1));
}


// Create the linear plot
$lp0 = new LinePlot($cdiff, $times);
$lp0->SetColor("green");
$lp0->SetLegend("Accum Difference");

$b2plot = new BarPlot($obs, $atimes);
$b2plot->SetFillColor("blue");
$b2plot->SetLegend("Obs Rain");

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
$graph->Add($lp0);
$graph->Add($lp1);
$graph->Add($lp2);
$graph->Add($b2plot);
$graph->Add($z);

// Display the graph
$graph->Stroke();
