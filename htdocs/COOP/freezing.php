<?php
define("IEM_APPID", 158);
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/mlib.php";
require_once "../../include/imagemaps.php";

$sortcol = isset($_GET["sortcol"]) ? xssafe($_GET["sortcol"]) : "station";
$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IACLIMATE";

$t = new MyView();
$t->title = "Freezing Dates";

$nt = new NetworkTable($network);
$cities = $nt->table;

$nselect = selectNetworkType("CLIMATE", $network);

$conn = iemdb("coop");

$query = "select station, valid, min_low, min_low_yr from climate
     WHERE valid > '2000-08-01' and min_low <= $2
     and substr(station,0,3) = $1 ORDER by valid";
$stname = iem_pg_prepare($conn, $query);
$rs = pg_execute($conn, $stname, array(substr($network, 0, 2), 32));

 
$query = "select station, valid, low from climate
     WHERE valid > '2000-08-01' and low <= $2
     and substr(station,0,3) = $1 ORDER by valid";
$stname = iem_pg_prepare($conn, $query);
$rs2 = pg_execute($conn, $stname, array(substr($network, 0, 2), 40));

$data = array();
while ($row = pg_fetch_assoc($rs)) {
    $st = $row["station"];
    if (!isset($data[$st])) {
        $data[$st] = array(
            "min_low" => 100,
            "avglow32day" => null,
            "avglow28day" => null,
            "station" => $st);
        $data[$st]["low"] = $row["min_low"];
        $data[$st]["lowyr"] = $row["min_low_yr"] . "-" . substr($row["valid"], 5, 6);
    }
    if (!isset($data[$st]["low28"])) {
        if (intval($row["min_low"]) < 29) {
            $data[$st]["low28"] = $row["min_low"];
            $data[$st]["low28yr"] = $row["min_low_yr"] . "-" . substr($row["valid"], 5, 6);
        }
    }
}

while ($row = pg_fetch_assoc($rs2)) {
    $st = $row["station"];
    if (!isset($data[$st]["avelow40day"])) {
        if (intval($row["low"]) < 41) {
            $data[$st]["avelow40day"] = substr($row["valid"], 5, 6);
        }
    }
    if (!isset($data[$st]["avelow32day"])) {
        if (intval($row["low"]) < 33) {
            $data[$st]["avelow32day"] = substr($row["valid"], 5, 6);
        }
    }
    if (!isset($data[$st]["avelow28day"])) {
        if (intval($row["low"]) < 28) {
            $data[$st]["avelow28day"] = substr($row["valid"], 5, 6);
        }
    }
}

$finalA = array();
$finalA = aSortBySecondIndex($data, $sortcol);

$table = "";
foreach ($finalA as $key => $value) {
    if (!array_key_exists($key, $cities)) continue;
    $table .= "<tr><td>" . $cities[strtoupper($key)]["name"] . "</td>
    <td>" . $data[$key]["low"] . "</td>
    <td>" . $data[$key]["lowyr"] . "</td>
    <td>" . $data[$key]["low28"] . "</td>
    <td>" . $data[$key]["low28yr"] . "</td>
    <td>" . $data[$key]["avelow40day"] . "</td>
    <td>" . $data[$key]["avelow32day"] . "</td>
    <td>" . $data[$key]["avelow28day"] . "</td>
    </tr>\n";
}


$t->content = <<<EOM
<h3>Freezing Dates</h3>

<p>Using the NWS COOP data archive, significant dates relating to fall are
extracted and presented on this page.  The specific dates are the first 
occurance of that temperature and may have occured again in subsequent 
years.

<br>The "Record Lows" columns show the first fall occurance of a low
temperature.  The "Average Lows" column shows when certain climatological
thresholds are surpassed in the fall.
</p>

<form method="GET" action="freezing.php">
  <div class="row">
    <div class="col-md-4">
      <strong>Select Network:</strong> {$nselect}
      <input type="submit" value="Switch Network">
    </div>
  </div>
</form>

<table class="table table-condensed table-striped">
<thead class="sticky">
  <tr>
    <th rowspan='3'><a href='freezing.php?sortcol=station'>COOP Site:</a></th>
    <th colspan='4'>Record Lows:</th>
    <th colspan='3'>Average Lows:</th>
  </tr>
  <tr>
    <th colspan='2'>Temp <= 32&deg;F</th>
    <th colspan='2'>Temp <= 28&deg;F</th>
    <td rowspan='2'><a href='freezing.php?sortcol=avelow40day'>Below 40&deg;F</a></td>
    <td rowspan='2'><a href='freezing.php?sortcol=avelow32day'>Below 32&deg;F</a></td>
    <td rowspan='2'><a href='freezing.php?sortcol=avelow28day'>Below 28&deg;F</a></td>
  </tr>
    <td>Temp:</td>
    <td><a href='freezing.php?sortcol=lowyr'>Date:</a></td>
    <td>Temp:</td>
    <td><a href='freezing.php?sortcol=low28yr'>Date:</a></td>
  </tr>
</thead>
<tbody>
  {$table}
</tbody>
</table>
EOM;
$t->render('single.phtml');
