<?php
/*
 * NWS CCOOP currents lister
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 159);
require_once "../../include/network.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/database.inc.php";
require_once "../../include/mlib.php";

$t = new MyView();

$sortcol = isset($_GET['sortcol']) ? xssafe($_GET['sortcol']) : 'ts';
$sortdir = isset($_GET['sortdir']) ? xssafe($_GET['sortdir']) : 'desc';
if ($sortdir != "asc" && $sortdir != "desc") $sortdir = "desc";

function precip_formatter($val)
{
    if ($val === '') return '';
    if ($val === 0.0001) return 'T';
    if ($val < 0) return 'M';
    return $val;
}

function make_row($dict, $oddrow)
{
    $s = "<tr";
    if ($oddrow) $s .= ' bgcolor="#EEEEEE"';
    $s .= ">";

    $sitesurl = sprintf(
        "%s/sites/site.php?station=%s&network=%s",
        BASEURL,
        $dict["sid"],
        $dict["network"]
    );

    $s .= <<<EOF
    <td><input type="checkbox" name="st[]" value="{$dict["sid"]}"/></td>
    <td><a href="/p.php?pid={$dict["raw"]}" class="btn btn-small"><i class="fa fa-paperclip"></i></a>
    </td>
EOF;
    $s .= "<td><a href=\"$sitesurl\">{$dict['sid']}</a></td>";
    $s .= "<td>{$dict['name']}, {$dict['state']}</a></td>";

    $bgcolor = (date("Ymd") != date("Ymd", $dict["ts"])) ? '#F00' : 'inherit';
    $fmt = (date("Ymd") != date("Ymd", $dict["ts"])) ? 'd M Y h:i A' : 'h:i A';
    $s .= "<td style=\"background: $bgcolor;\">" . date($fmt, $dict["lts"]) . "</td>";

    $s .= sprintf(
        "<td>%s</td><td><span style=\"color: #F00;\">%s</span></td>
    <td><span style=\"color: #00F;\">%s</span></td>",
        $dict["tmpf"] != "" ? $dict["tmpf"] : "M",
        $dict["max_tmpf"] != "" ? $dict["max_tmpf"] : "M",
        $dict["min_tmpf"] != "" ? $dict["min_tmpf"] : "M"
    );

    $s .= sprintf(
        "<td>%s</td>",
        precip_formatter($dict["pday"]),
    );

    $s .= "</tr>\n";
    return $s;
}

$jobj = iemws_json("currents.json", array("network" => "CCOOP"));

$db = array();
foreach ($jobj["data"] as $bogus => $iemob) {
    $site = $iemob["station"];
    $db[$site] = array(
        'pday' => "", 'min_tmpf' => "", 'max_tmpf' => "", 'tmpf' => ""
    );
    $db[$site]['ts'] = strtotime($iemob["local_valid"]);
    $db[$site]['lts'] = strtotime($iemob["local_valid"]);
    $db[$site]['sid'] = $site;
    $db[$site]['name'] = $iemob["name"];
    $db[$site]['raw'] = $iemob["raw"];
    $db[$site]['state'] = $iemob["state"];
    $db[$site]['network'] = $iemob["network"];
    $db[$site]['county'] = $iemob["county"];
    if ($iemob["tmpf"] > -100) {
        $db[$site]['tmpf'] = $iemob["tmpf"];
    }
    if ($iemob["max_tmpf"] > -100) {
        $db[$site]['max_tmpf'] = $iemob["max_tmpf"];
    }

    if ($iemob["min_tmpf"] < 99) {
        $db[$site]['min_tmpf'] = $iemob["min_tmpf"];
    }

    $db[$site]['pday'] = $iemob["pday"];
}

$db = aSortBySecondIndex($db, $sortcol, $sortdir);

$oddrow = true;
$firstsection = "";
$lastsection = "";
foreach ($db as $site => $value) {
    $oddrow = !$oddrow;
    if (date("Ymd", $value["ts"]) == date("Ymd")) {
        $firstsection .= make_row($value, $oddrow);
    } else {
        $value["tmpf"] = "";
        $lastsection .= make_row($value, $oddrow);
    }
}

function get_sortdir($baseurl, $column, $sortCol, $sortDir)
{
    $newSort = ($sortDir == "asc") ? "desc" : "asc";
    if ($column == $sortCol) return "{$baseurl}&sortcol=$column&sortdir=$newSort";
    return "{$baseurl}&sortcol=$column&sortdir=$sortDir";
}

$t->title = "NWS CCOOP Current Sortables";
$t->headextra = <<<EOF
 <script language="JavaScript" type="text/javascript">
    <!--//BEGIN Script
    function new_window(url) {
     link = window.open(url,"_new","toolbar=0,location=0,directories=0,status=0,menubar=no,scrollbars=yes,resizable=yes,width=800,height=600");
    }
    //END Script-->
    </script>
EOF;

$cols = array(
    "ts" => "Valid", "county" => "County",
    "sid" => "Site ID", "name" => "Station Name",
    "ratio" => "Snow to Water Ratio",
    "tmpf" => "Ob Temperature", "max_tmpf" => "24 hour High",
    "min_tmpf" => "24 hour Low", "snow" => "24 hour Snowfall",
    "snowd" => "Snowfall Depth", "pday" => "24 hour rainfall",
    "phour" => "Rainfall One Hour", "snoww" => "Snow Water Equivalent"
);
$t->current_network = "Cellular COOP";


$sorts = array("asc" => "Ascending", "desc" => "Descending");
$baseurl = "/nws/ccoop_current.php?";
$one = get_sortdir($baseurl, "sid", $sortcol, $sortdir);
$two = get_sortdir($baseurl, "name", $sortcol, $sortdir);
$three = get_sortdir($baseurl, "county", $sortcol, $sortdir);
$four = get_sortdir($baseurl, "ts", $sortcol, $sortdir);
$five = get_sortdir($baseurl, "tmpf", $sortcol, $sortdir);
$six = get_sortdir($baseurl, "max_tmpf", $sortcol, $sortdir);
$seven = get_sortdir($baseurl, "min_tmpf", $sortcol, $sortdir);
$eight = get_sortdir($baseurl, "pday", $sortcol, $sortdir);

$content = <<<EOF

<p>Sorted by: <strong>{$cols[$sortcol]} {$sorts[$sortdir]}</strong>. 
Times are presented in the local time of the site. Click on the identifier to
get all daily observations for the site.  Click on the site name to get more
information on the site. Click on the column heading to sort the column, clicking
again will reverse the sort.
 
<form name="st" action="/my/current.phtml" method="GET">
<table class="table table-striped table-condensed table-bordered">
<thead>
<tr>
  <th rowspan=2>Add:</th><th rowspan=2>Raw:</th>
  <th rowspan=2><a href="{$one}">SiteID:</a></th>
  <th rowspan=2><a href="{$two}">Station Name:</a></th>
  <th rowspan=2><a href="{$four}">Valid:</a></th>
  <th colspan=3>Temperatures [F]</th>
  <th colspan="1">Hydro</th></tr>

<tr>
  <th><a href="{$five}">At Ob</a></th>
  <th><a href="{$six}">24h High</a></th>
  <th><a href="{$seven}">24h Low</a></th>
  <th><a href="{$eight}">24hour Rain</a></th>
</tr></thead>
<tbody>
EOF;


$content .= <<<EOF
{$firstsection}
{$lastsection}
</tbody>
</table>
<input type="submit" value="Add to Favorites">
</form>
EOF;
$t->content = $content;
$t->render('sortables.phtml');
