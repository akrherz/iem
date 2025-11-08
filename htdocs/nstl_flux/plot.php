<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "../../include/jpgraph/jpgraph.php";
require_once "../../include/jpgraph/jpgraph_line.php";
require_once "../../include/jpgraph/jpgraph_date.php";
/* We need to get some CGI vars! */
$year = get_str404("year", null);
$month = get_str404("month", null);
$day = get_str404("day", null);
$pvar = get_str404("pvar", null);
if (is_null($year) || is_null($month) || is_null($day) || is_null($pvar)) {
    http_response_code(422);
    die("Missing year, month, day, pvar");
}
$sts = mktime(0, 0, 0, $month, $day, $year);

$vars = array();
$pgconn = iemdb("other");

$sql = "SELECT * from flux_vars ORDER by details ASC";
$rows = pg_exec($pgconn, $sql);
while ($row = pg_fetch_assoc($rows)) {
    $vars[$row["name"]] = array("units" => $row["units"], "details" => $row["details"]);
}

$stname = iem_pg_prepare($pgconn, "SELECT * from flux_data WHERE " .
    "valid >= $1 and valid < ($1 + '1 day'::interval) " .
    "and $pvar IS NOT NULL ORDER by valid ASC");
$stname2 = iem_pg_prepare($pgconn, "SELECT * from flux_meta WHERE " .
    "sts < $1 and ets > $1");

$rs = pg_execute($pgconn, $stname, array(date('Y-m-d', $sts)));

$data = array(
    "NSTL11" => array(),
    "NSTL10" => array(),
    "NSTL30FT" => array(),
    "NSTL110" => array(),
    "NSTLNSPR" => array()
);
$times = array(
    "NSTL11" => array(),
    "NSTL10" => array(),
    "NSTL30FT" => array(),
    "NSTL110" => array(),
    "NSTLNSPR" => array()
);

while ($row = pg_fetch_assoc($rs)) {
    $ts = strtotime(substr($row["valid"], 0, 16));
    $stid = $row["station"];
    $val = floatval($row[$pvar]);
    if ($val > -90000) {
        $data[$stid][] = floatval($row[$pvar]);
        $times[$stid][] = $ts;
    }
}

$labels = array(
    "NSTLNSPR" => "NSTLNSPR",
    "NSTL11" => "NSTL11",
    "NSTL10" => "NSTL10",
    "NSTL30FT" => "NSTL30FT",
    "NSTL110" => "NSTL110"
);
$rs = pg_execute($pgconn, $stname2, array(date('Y-m-d', $sts)));
while ($row = pg_fetch_assoc($rs)) {
    $st = $row["station"];
    $labels[$st] =  $row["surface"];
}

$ts_lbl = date("d M Y", $sts);

// Create the graph. These two calls are always required
$graph = new Graph(640, 350);
$graph->SetScale("datlin");
$graph->img->SetMargin(65, 8, 45, 70);
$graph->SetMarginColor('white');
// Box around plotarea
$graph->SetBox();

// Setup the X and Y grid
$graph->ygrid->SetFill(true, '#DDDDDD@0.5', '#BBBBBB@0.5');
$graph->ygrid->SetLineStyle('dashed');
$graph->ygrid->SetColor('gray');
$graph->xgrid->Show();
$graph->xgrid->SetLineStyle('dashed');
$graph->xgrid->SetColor('gray');

$graph->xaxis->SetFont(FF_FONT1, FS_NORMAL);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelFormatString("h A", true);
$graph->xaxis->SetTitleMargin(35);

$graph->tabtitle->Set($vars[$pvar]["details"]);

$graph->xaxis->SetTitle("Timeseries for {$ts_lbl}");
$graph->yaxis->SetTitle($vars[$pvar]["details"] . " [" . $vars[$pvar]["units"] . "]");
$graph->yaxis->SetTitleMargin(45);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.92, "left", "top");

// Create the linear plot
if (sizeof($data["NSTL11"]) > 1) {
    $lineplot = new LinePlot($data["NSTL11"], $times["NSTL11"]);
    $lineplot->SetColor("red");
    $lineplot->SetLegend($labels["NSTL11"]);
    $lineplot->SetWeight(2);
    $graph->Add($lineplot);
}

if (sizeof($data["NSTL10"]) > 1) {
    $lineplot2 = new LinePlot($data["NSTL10"], $times["NSTL10"]);
    $lineplot2->SetColor("blue");
    $lineplot2->SetLegend($labels["NSTL10"]);
    $lineplot2->SetWeight(2);
    $graph->Add($lineplot2);
}

// Create the linear plot
if (sizeof($data["NSTLNSPR"]) > 1) {
    $lineplot3 = new LinePlot($data["NSTLNSPR"], $times["NSTLNSPR"]);
    $lineplot3->SetColor("black");
    $lineplot3->SetLegend($labels["NSTLNSPR"]);
    $lineplot3->SetWeight(2);
    $graph->Add($lineplot3);
}

// Create the linear plot
if (sizeof($data["NSTL30FT"]) > 1) {
    $lineplot4 = new LinePlot($data["NSTL30FT"], $times["NSTL30FT"]);
    $lineplot4->SetColor("green");
    $lineplot4->SetLegend($labels["NSTL30FT"]);
    $lineplot4->SetWeight(2);
    $graph->Add($lineplot4);
}

// Create the linear plot
if (sizeof($data["NSTL110"]) > 1) {
    $lineplot5 = new LinePlot($data["NSTL110"], $times["NSTL110"]);
    $lineplot5->SetColor("brown");
    $lineplot5->SetLegend($labels["NSTL110"]);
    $lineplot5->SetWeight(2);
    $graph->Add($lineplot5);
}

// Display the graph
$graph->Stroke();
