<?php
define("IEM_APPID", 158);
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/mlib.php";

$sortcol = get_str404("sortcol", "station");
$sortable_columns = ["station", "min_low", "low", "low28", "avglow40day", "avglow32day", "avglow28day"];
if (!in_array($sortcol, $sortable_columns)) {
    $sortcol = "station";
}

$network = get_str404("network", "IACLIMATE");

$t = new MyView();
$t->title = "Freezing Dates";

$nt = new NetworkTable($network);
$cities = $nt->table;

$nselect = selectNetworkType("CLIMATE", $network);

$conn = iemdb("coop");

// Process everything after 1 August until 1 April
$query = <<<EOM
    select station,
    case when extract(month from valid) > 7
    then valid - interval '1 year' else valid end as winter_valid,
    low, min_low, min_low_yr from climate
    WHERE (valid >= '2000-08-01' or valid < '2000-04-01')
    and substr(station, 1, 2) = $1 and low is not null
    and min_low is not null ORDER by winter_valid ASC
EOM;
$stname = iem_pg_prepare($conn, $query);
$rs = pg_execute($conn, $stname, array(substr($network, 0, 2)));

$data = array();
while ($row = pg_fetch_assoc($rs)) {
    $st = $row["station"];
    $low = (float)$row["low"];
    $min_low = (int)$row["min_low"];
    if (!array_key_exists($st, $data)) {
        $data[$st] = array(
            "quorum" => 0,
            "min_low" => 100,
            "avglow40day" => null,
            "avglow32day" => null,
            "avglow28day" => null,
            "low" => null,
            "lowyr" => null,
            "low28" => null,
            "low28yr" => null,
            "station" => $st,  // allow for array sorting later.
        );
    }
    $data[$st]["quorum"] += 1;
    // Running min_low value
    $data[$st]["min_low"] = min($min_low, $data[$st]["min_low"]);
    // Do the minimum low work.
    if ($min_low <= 32 && is_null($data[$st]["low"])) {
        $data[$st]["low"] = $min_low;
        $data[$st]["lowyr"] = $row["min_low_yr"] ."-". substr($row["winter_valid"], 5, 6);
    }
    if ($min_low <= 28 && is_null($data[$st]["low28"])) {
        $data[$st]["low28"] = $min_low;
        $data[$st]["low28yr"] = $row["min_low_yr"] ."-". substr($row["winter_valid"], 5, 6);
    }
    // Check the average low value.
    if ($low < 40 && is_null($data[$st]["avglow40day"])) {
        $data[$st]["avglow40day"] = substr($row["winter_valid"], 5, 6);
    }
    if ($low < 32 && is_null($data[$st]["avglow32day"])) {
        $data[$st]["avglow32day"] = substr($row["winter_valid"], 5, 6);
    }
    if ($low < 28 && is_null($data[$st]["avglow28day"])) {
        $data[$st]["avglow28day"] = substr($row["winter_valid"], 5, 6);
    }
}

// Remove any entries without a quorum of approximately 8 months of data
foreach ($data as $key => $value) {
    if ($value["quorum"] < (8 * 29)) {
        unset($data[$key]);
    }
}

$finalA = array();
$finalA = aSortBySecondIndex($data, $sortcol);

$table = "";
foreach ($finalA as $key => $value) {
    if (!array_key_exists($key, $cities)) continue;
    $table .= "<tr>
    <td>{$key}</td>
    <td>" . $cities[strtoupper($key)]["name"] . "</td>
    <td>" . $data[$key]["min_low"] . "</td>
    <td>" . $data[$key]["low"] . "</td>
    <td>" . $data[$key]["lowyr"] . "</td>
    <td>" . $data[$key]["low28"] . "</td>
    <td>" . $data[$key]["low28yr"] . "</td>
    <td>" . $data[$key]["avglow40day"] . "</td>
    <td>" . $data[$key]["avglow32day"] . "</td>
    <td>" . $data[$key]["avglow28day"] . "</td>
    </tr>\n";
}


$t->content = <<<EOM
<h3>Freezing Dates</h3>

<p>
The IEM processed "climodat" archive is used to list out the first dates after
1 August that a given site first dipped below 32°F and 28°F.  The dates when
those events occurred are shown.  The second set of columns print out the
fall day of the year that the climatology dips below the given threshold.
</p>

<p>
Only the August through March period is considered for this analysis.  There
is currently a data processing bug whereby the year of the first dates are not
shown for all sites.  This will be fixed over the coming days.
</p>

<form method="GET" action="freezing.php">
  <div class="row">
    <div class="col-md-4">
      <strong>Select Network:</strong> {$nselect}
      <input type="submit" value="Switch Network">
    </div>
  </div>
</form>

<table class="table table-sm table-striped">
<thead class="sticky">
  <tr>
    <th rowspan="3">ID</th>
    <th rowspan='3'><a href='freezing.php?sortcol=station'>Climodat Site:</a></th>
    <th rowspan='3'><a href='freezing.php?sortcol=min_low'>Min Low:</a></th>
    <th colspan='4'>First Date with Observed Below:</th>
    <th colspan='3'>First Date with Average Below:</th>
  </tr>
  <tr>
    <th colspan='2'>Temp <= 32&deg;F</th>
    <th colspan='2'>Temp <= 28&deg;F</th>
    <td rowspan='2'><a href='freezing.php?sortcol=avglow40day'>Below 40&deg;F</a></td>
    <td rowspan='2'><a href='freezing.php?sortcol=avglow32day'>Below 32&deg;F</a></td>
    <td rowspan='2'><a href='freezing.php?sortcol=avglow28day'>Below 28&deg;F</a></td>
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
