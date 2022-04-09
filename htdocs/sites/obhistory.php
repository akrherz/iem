<?php 
require_once "setup.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";
require_once "../../include/myview.php";
/*
 * Rip off weather bureau website, but do it better
 */
function wind_formatter($row){
	if (is_null($row["drct"]) && ($row["sknt"] > 0) && ($row["sknt"] < 10)) {
		return sprintf("VRB %.0f", $row["sknt"] * 1.15);
	}
	if (($row["drct"] == 0) && ($row["sknt"] == 0)) {
		return "Calm";
	}
	if (is_null($row["drct"])){
		return "M";
	} 
	$gust_text = "";
	if ($row["gust"] > 0){
		$gust_text = sprintf("G %.0f", $row["gust"] * 1.15);
	}
	return sprintf("%s %.0f%s", drct2txt($row["drct"]), $row["sknt"] * 1.15,
	$gust_text );
}
function indy_sky_formatter($skyc, $skyl){
	if (intval($skyl) > 0){ $skyl = sprintf("%03d", $skyl/100); }
	else { $skyl = "";}	
	if (is_null($skyc) || trim($skyc) == "") return "";
	return sprintf("%s%s<br />", $skyc,$skyl);
}
function sky_formatter($row){
	return sprintf("%s%s%s%s", 
	indy_sky_formatter($row["skyc1"], $row["skyl1"]),
	indy_sky_formatter($row["skyc2"], $row["skyl2"]),
	indy_sky_formatter($row["skyc3"], $row["skyl3"]),
	indy_sky_formatter($row["skyc4"], $row["skyl4"])
	);
}
function temp_formatter($val){
	if (is_null($val)) return "";
	return sprintf("%.0f", $val);
}
function vis_formatter($val){
	if (is_null($val)) return "";
	return round($val, 2);
}
function precip_formatter($val){
    if (is_null($val)) return "";
    if ($val == 0.0001) return "T";
    return round($val, 2);
}
function asos_formatter($i, $row){
	$ts = strtotime(substr($row["local_valid"], 0, 16));
	$relh = relh(f2c($row["tmpf"]), f2c($row["dwpf"]) );
	$relh = (! is_null($relh)) ? intval($relh): "";
	$ismadis = (strpos($row["raw"], "MADISHF") > 0); 
	return sprintf("<tr style=\"background: %s;\" class=\"%sob\" data-madis=\"%s\">" .
	"</div><td>%s</td><td>%s</td><td>%s</td>
	<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
	<td><span class=\"high\">%s</span></td>
	<td><span class=\"low\">%s</span></td>
	<td>%s%%</td>
	<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
	<tr style=\"background: %s;\" class=\"%smetar\">" .
	"<td colspan=\"17\">%s</td></tr>", 
	($i % 2 == 0)? "#FFF": "#EEE",
	$ismadis ? "hf": "",
	$ismadis ? "1": "0",
	date("g:i A", $ts), wind_formatter($row) , vis_formatter($row["vsby"]),
	sky_formatter($row), $row["wxcodes"], temp_formatter($row["tmpf"]), 
	temp_formatter($row["dwpf"]),
	temp_formatter($row["feel"]),
	temp_formatter($row["max_tmpf_6hr"]), temp_formatter($row["min_tmpf_6hr"]), 
	relh(f2c($row["tmpf"]), f2c($row["dwpf"])),
    $row["alti"], $row["mslp"],
    $row["snowdepth"],
    precip_formatter($row["p01i"]),
    precip_formatter($row["p03i"]),
    precip_formatter($row["p06i"]),
	($i % 2 == 0)? "#FFF": "#EEE",
	$ismadis ? " hf": "", $row["raw"]
	);
}
function formatter($i, $row){
	$ts = strtotime(substr($row["local_valid"], 0, 16));
	$relh = relh(f2c($row["tmpf"]), f2c($row["dwpf"]) );
	$relh = (! is_null($relh)) ? intval($relh): "";
	return sprintf("<tr style=\"background: %s;\">" .
	"<td>%s</td><td>%s</td><td>%s</td>
	<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>",
	($i % 2 == 0)? "#FFF": "#EEE",
	date("g:i A", $ts), wind_formatter($row) , temp_formatter($row["tmpf"]), 
	temp_formatter($row["dwpf"]),
	temp_formatter($row["feel"]),
	relh(f2c($row["tmpf"]), f2c($row["dwpf"])),
    precip_formatter($row["phour"]),
	);
}
function hads_formatter($i, $row, $shefcols){
	$ts = strtotime(substr($row["local_valid"], 0, 16));
	$relh = relh(f2c($row["tmpf"]), f2c($row["dwpf"]) );
	$relh = (! is_null($relh)) ? intval($relh): "";
    $html = "";
    foreach ($shefcols as $bogus => $name){
        $html .= sprintf("<td>%s</td>", $row["$name"]);
    }
    return sprintf("<tr style=\"background: %s;\">" .
	"<td>%s</td><td>%s</td><td>%s</td>
	<td>%s</td><td>%s</td><td>%s</td><td>%s</td>%s</tr>",
	($i % 2 == 0)? "#FFF": "#EEE",
	date("g:i A", $ts), wind_formatter($row) , temp_formatter($row["tmpf"]), 
	temp_formatter($row["dwpf"]),
	temp_formatter($row["feel"]),
	relh(f2c($row["tmpf"]), f2c($row["dwpf"])),
    precip_formatter($row["phour"]), $html
	);
}
$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$metar = (isset($_GET["metar"]) && $_GET["metar"] == "1") ? "1": "0";
$madis = (isset($_GET["madis"]) && $_GET["madis"] == "1") ? "1": "0";
$sortdir = isset($_GET["sortdir"]) ? xssafe($_GET["sortdir"]) : "asc";
$date = mktime(0,0,0,$month, $day, $year);
$yesterday = $date - 86400;
$tomorrow = $date + 86400;
if ($tomorrow > time()){
	$tomorrow = null;
}

$sortopts = Array(
    "asc" => "Ascending",
    "desc" => "Descending",
);
$sortform = make_select("sortdir", $sortdir, $sortopts);

if (! is_null($metadata["archive_begin"])){
	$startyear = intval($metadata["archive_begin"]->format("Y"));
} else {
	$startyear = 2010;
}

$t = new MyView();

$t->title = "Observation History";
$t->sites_current = 'obhistory';

$savevars = Array("year"=>date("Y", $date),
 "month"=>date("m", $date), "day"=>date("d", $date)); 
$madis_show = ($madis == "1") ? "true" : "false";
$metar_show = ($metar == "1") ? "true" : "false";
 $t->jsextra = <<<EOF
<script type="text/javascript">
var metar_show = {$metar_show};
var madis_show = {$madis_show};
var station = "{$station}";
var network = "{$network}";
var month = "{$month}";
var day = "{$day}";
var year = "{$year}";
function updateButton(label){
    var btn = $("#" + label);
    var uri = window.location.origin + window.location.pathname + "?station=" +
    station + "&network=" + network  + "&year=" + btn.data("year")
    + "&month=" + btn.data("month")  + "&day=" + btn.data("day");
    if (metar_show){
        uri += "&metar=1";
    }
    if (madis_show){
        uri += "&madis=1";
    }
    btn.attr("href", uri);
}
function updateURI(){
    // Add CGI vars that control the METAR and MADIS show buttons
    var uri = window.location.origin + window.location.pathname + "?station=" +
        station + "&network=" + network  + "&year=" + year
        + "&month=" + month  + "&day=" + day;
    if (metar_show){
        uri += "&metar=1";
    }
    if (madis_show){
        uri += "&madis=1";
    }
    window.history.pushState({}, "", uri);
    updateButton("prevbutton");
    updateButton("nextbutton");
}
function showMETAR(){
    $(".metar").css("display", "table-row");
    if (madis_show){
        $(".hfmetar").css("display", "table-row");
    }
    $("#metar_toggle").html("<i class=\"fa fa-minus\"></i> Hide METARs");
}
function toggleMETAR(){
	if (metar_show){
		// Hide both METARs and HFMETARs
		$(".metar").css("display", "none");
		$(".hfmetar").css("display", "none");
        $("#metar_toggle").html("<i class=\"fa fa-plus\"></i> Show METARs");
        $("#hmetar").val("0");
	} else{
        // show
        showMETAR();
        $("#hmetar").val("1");
	}
    metar_show = !metar_show;
    updateURI();
}
function showMADIS(){
    $("tr[data-madis=1]").css("display", "table-row");
    if (metar_show){
        $(".hfmetar").css("display", "table-row");
    }
    $("#madis_toggle").html("<i class=\"fa fa-minus\"></i> Hide High Frequency MADIS");
}
function toggleMADIS(){
	if (madis_show){
		// Hide MADIS
		$("tr[data-madis=1]").css("display", "none");
		$(".hfmetar").css("display", "none");
		$("#madis_toggle").html("<i class=\"fa fa-plus\"></i> Show High Frequency MADIS");
        $("#hmadis").val("0");
	} else {
        // Show
        showMADIS();
        $("#hmadis").val("1");
	}
	madis_show = !madis_show;
    updateURI();
}
$(document).ready(function(){
    if (metar_show) {
        showMETAR();
    }
    if (madis_show) {
        showMADIS();
    }
});
</script>
EOF;
$dstr = date("d F Y", $date);
$tzname =  $metadata["tzname"];

$ys = yearSelect($startyear,date("Y", $date));
$ms = monthSelect(date("m", $date));
$ds = daySelect(date("d", $date));

$mbutton = (preg_match("/ASOS/", $network)) ? 
"<a onclick=\"javascript:toggleMETAR();\" class=\"btn btn-success\" id=\"metar_toggle\"><i class=\"fa fa-plus\"></i> Show METARs</a>" .
" &nbsp; <a onclick=\"javascript:toggleMADIS();\" class=\"btn btn-success\" id=\"madis_toggle\"><i class=\"fa fa-plus\"></i> Show High Frequency MADIS</a>"
: "";

$content = <<<EOF
<style>
.high {
  color: #F00;
}
.low {
  color: #00F;
}
.metar {
  display: none;
}
.hfob {
	display: none;
}
.hfmetar {
	display: none;
}
</style>

<h3>{$dstr} Observation History, [{$station}] {$metadata["name"]}, timezone: {$tzname}</h3>
<form name="theform" method="GET">
<strong>Select Date:</strong>
<input type="hidden" value="{$station}" name="station" />
<input type="hidden" value="{$network}" name="network" />
<input id="hmetar" type="hidden" value="{$metar}" name="metar" />
<input id="hmadis" type="hidden" value="{$madis}" name="madis" />
{$ys}
{$ms}
{$ds}
Time Order:{$sortform}
<input type="submit" value="Change Date" />
</form>
<p>{$mbutton}</p>
EOF;
$content .= sprintf("<a id=\"prevbutton\" ".
    "data-year=\"%s\" data-month=\"%s\" data-day=\"%s\" ".
    "href=\"obhistory.php?network=%s&station=%s&year=%s&month=%s&day=%s\" ".
    "class=\"btn btn-default\">Previous Day</a>",
    date("Y", $yesterday), date("m", $yesterday), date("d", $yesterday),
    $network, $station, date("Y", $yesterday),
    date("m", $yesterday), date("d", $yesterday));
  
if ($tomorrow){
  $content .= sprintf("<a id=\"nextbutton\" ". 
    "data-year=\"%s\" data-month=\"%s\" data-day=\"%s\" ".
    "href=\"obhistory.php?network=%s&station=%s&year=%s&month=%s&day=%s\" ".
    "class=\"btn btn-default\">Next Day</a>",
    date("Y", $tomorrow), date("m", $tomorrow), date("d", $tomorrow),
    $network, $station, date("Y", $tomorrow),
    date("m", $tomorrow), date("d", $tomorrow));
}
$notes = '';
if ($network == "ISUSM"){
	$notes .= "<li>Wind direction and wind speed are 10 minute averages at 10 feet above the ground.</li>";
}

// API endpoint
$errmsg = "";
$arr = Array(
    "station" => $station,
    "network" => $network,
    "date" => date("Y-m-d", $date),
    "full" => "1",
);
$wsuri = sprintf("/api/1/obhistory.json?%s", http_build_query($arr));
$jobj = iemws_json("obhistory.json", $arr);
if ($jobj === FALSE){
    $jobj = Array("data" => Array(), "schema" => Array("fields" => Array()));
    $errmsg = "Failed to fetch history from web service. No data was found.";
}

if (preg_match("/ASOS/", $network)){
	$notes .= <<<EOM
<li>For recent years, this page also optionally shows observations from the
<a href="https://madis.ncep.noaa.gov/madis_OMO.shtml">MADIS High Frequency METAR</a>
dataset.  This dataset had a problem with temperatures detailed <a href="https://mesonet.agron.iastate.edu/onsite/news.phtml?id=1290">here</a>.</li>
EOM;
    $header = <<<EOM
    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="3">Time</th>
    <th rowspan="3">Wind<br>(mph)</th>
    <th rowspan="3">Vis.<br>(mi.)</th>
    <th rowspan="3">Sky Cond.<br />(100s ft)</th>
    <th rowspan="3">Present Wx</th>
    <th colspan="5">Temperature (&ordm;F)</th>
    <th rowspan="3">Relative<br>Humidity</th>
    <th colspan="2">Pressure</th>
    <th rowspan="3">Snow<br />Depth<br />(in)</th>
    <th colspan="3">Precipitation (in.)</th></tr>

    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="2">Air</th>
    <th rowspan="2">Dwpt</th>
    <th rowspan="2">Feels Like</th>
    <th colspan="2">6 hour</th>
    <th rowspan="2">altimeter<br>(in.)</th>
    <th rowspan="2">sea level<br>(mb)</th>
    <th rowspan="2">1 hr</th>
    <th rowspan="2">3 hr</th>
    <th rowspan="2">6 hr</th>
    </tr>
    
    <tr align="center" bgcolor="#b0c4de"><th>Max.</th><th>Min.</th></tr>    
EOM;
} else if (preg_match("/DCP|COOP/", $network)){
    // Figure out what extra columns we have here.
    $shefcols = Array();
    $shefextra = "";
    foreach($jobj["schema"]["fields"] as $bogus => $field){
        $name = $field["name"];
        if (preg_match("/^[A-Z]/", $name)){
            $shefcols[] = $name;
        }
    }
    asort($shefcols);
    $shefheader = sprintf(
        "<th colspan=\"%s\">RAW SHEF CODES</th>", sizeof($shefcols));
    foreach($shefcols as $bogus => $val){
        $shefextra .= sprintf("<th>%s</th>", $val);
    }
    $header = <<<EOM
    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="2">Time</th>
    <th rowspan="2">Wind<br>(mph)</th>
    <th colspan="3">Temperature (&ordm;F)</th>
    <th rowspan="3">Relative<br>Humidity</th>
    <th>Precipitation (in.)</th>
    {$shefheader}
    </tr>

    <tr align="center" bgcolor="#b0c4de">
    <th>Air</th>
    <th>Dwpt</th>
    <th>Feels Like</th>
    <th>1 hr</th>
    {$shefextra}
    </tr>
EOM;

} else {
    $header = <<<EOM
    <tr align="center" bgcolor="#b0c4de">
    <th rowspan="2">Time</th>
    <th rowspan="2">Wind<br>(mph)</th>
    <th colspan="3">Temperature (&ordm;F)</th>
    <th rowspan="3">Relative<br>Humidity</th>
    <th>Precipitation (in.)</th></tr>

    <tr align="center" bgcolor="#b0c4de">
    <th>Air</th>
    <th>Dwpt</th>
    <th>Feels Like</th>
    <th>1 hr</th>
    </tr>
EOM;
}


$table = "";
$i = 0;
$data = $jobj["data"];
if ($sortdir == "desc"){
    $data = array_reverse($data);
}
foreach($data as $bogus => $row)
{
    if (preg_match("/ASOS/", $network)){
        $table .= asos_formatter($i, $row);
    } else if (preg_match("/DCP|COOP/", $network)){
        $table .= hads_formatter($i, $row, $shefcols);
    } else {
        $table .= formatter($i, $row);
    }
    $i++;
}
$errdiv = "";
if ($errmsg != ""){
    $errdiv = <<<EOM
<div class="alert alert-warning">{$errmsg}</div>
EOM;
}

$content .= <<<EOF

{$errdiv}

<table class="table table-striped table-bordered" id="datatable">
<thead>
{$header}
</thead>
<tbody>
{$table}
</tbody>
</table>

<p>The <a href="{$wsuri}">IEM API webservice</a> that provided data to this
page.  For more details, see <a href="/api/1/docs#/default/service_obhistory__fmt__get">documentation</a>.</p>

<h4>Data Notes</h4>
<ul>
{$notes}
</ul>
EOF;
$t->content = $content;
$t->render('sites.phtml');
