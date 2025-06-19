<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 77);
putenv("TZ=UTC");
date_default_timezone_set('UTC');
require_once "../../include/myview.php";
require_once "../../include/forms.php";

$t = new MyView();

$year = get_int404("year", date("Y"));
$wfo = isset($_REQUEST["wfo"]) ? xssafe($_REQUEST["wfo"]) : "DMX";
$opt = isset($_REQUEST["opt"]) ? xssafe($_REQUEST["opt"]) : "bywfo";
$damagetag = isset($_REQUEST["damagetag"]) ? xssafe($_REQUEST["damagetag"]) : "considerable";

$damagetags = array(
    "considerable" => "Considerable",
    "destructive" => "Destructive (SVR Only)",
    "catastrophic" => "Catastrophic",
);
if (!array_key_exists($damagetag, $damagetags)) {
    $damagetag = "considerable";
}

$bywfochecked = "";
$bydamagetagchecked = "";
if ($opt == "bywfo") {
    $bywfochecked = "checked";
    $jsonuri = sprintf(
        "%s/json/ibw_tags.py?wfo=%s&year=%s",
        $INTERNAL_BASEURL,
        $wfo,
        $year
    );
    $title = "NWS $wfo issued Impact Based Warning Tags for $year";
} else {
    $bydamagetagchecked = "checked";
    $jsonuri = sprintf(
        "%s/json/ibw_tags.py?damagetag=%s&year=%s",
        $INTERNAL_BASEURL,
        $damagetag,
        $year
    );
    $title = "NWS Damage Tags of $damagetag for $year";
}
$publicjsonuri = str_replace($INTERNAL_BASEURL, $EXTERNAL_BASEURL, $jsonuri);

$t->title = $title;
$t->headextra = <<<EOM
<link href="https://unpkg.com/tabulator-tables@6.2.1/dist/css/tabulator.min.css" rel="stylesheet">
<link href="list_tags.css" rel="stylesheet">
EOM;

$t->jsextra = <<<EOM
<script src="list_tags.module.js" type="module"></script>
EOM;


function do_text($row)
{
    if (is_null($row["product_id"])) {
        return "";
    }
    return sprintf(
        "<a href=\"%s\" target=\"_new\">Text</a>",
        $row["product_href"],
    );
}
function do_col1($row)
{
    if ($row["status"] == 'NEW') {
        return sprintf("<a href=\"%s\">%s</a>", $row['href'], $row["eventid"]);
    }
    $ptype = 'SVS';
    if ($row["phenomena"] == 'MA') $ptype = "MWS";
    elseif ($row["phenomena"] == 'FF') $ptype = "FFS";
    return sprintf("<a href=\"%s\">%s.%s</a>", $row['href'], $row["eventid"], $ptype);
}
function do_col2($row)
{
    if ($row["status"] == 'NEW') {
        return date("Y/m/d Hi", strtotime($row["issue"]));
    }
    return date("Y/m/d Hi", strtotime($row["polygon_begin"]));
}
function do_col3($row)
{
    if ($row["status"] == 'NEW') {
        return date("Hi", strtotime($row["expire"]));
    }
    return date("Hi", strtotime($row["polygon_end"]));
}
function do_row($row)
{
    return sprintf(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td nowrap>%s</td><td>%s</td><td>%s</td>"
            . "<td>%02.0f</td><td>%4.2f</td><td>%s</td><td>%s</td><td>%02.0f</td></tr>",
        do_col1($row),
        do_text($row),
        $row["wfo"],
        do_col2($row),
        do_col3($row),
        $row["locations"],
        $row["windtag"],
        $row["hailtag"],
        $row["tornadotag"],
        $row["damagetag"],
        $row["tml_sknt"]
    );
}
function do_row_ma($row)
{
    return sprintf(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td nowrap>%s</td><td>%s</td><td>%s</td>"
            . "<td>%02.0f</td><td>%4.2f</td><td>%s</td><td>%02.0f</td></tr>",
        do_col1($row),
        do_text($row),
        $row["wfo"],
        do_col2($row),
        do_col3($row),
        $row["locations"],
        $row["windtag"],
        $row["hailtag"],
        $row["waterspouttag"],
        $row["tml_sknt"]
    );
}

function do_row_ffw($row)
{
    return sprintf(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td nowrap>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td></tr>",
        do_col1($row),
        do_text($row),
        $row["wfo"],
        do_col2($row),
        do_col3($row),
        $row["locations"],
        $row["floodtag_flashflood"],
        $row["floodtag_damage"],
        $row["floodtag_heavyrain"],
        $row["floodtag_dam"],
        $row["floodtag_leeve"]
    );
}

$svrtable = <<<EOM
 <table id='svr-table' class="table table-sm table-striped table-bordered">
 <thead class="sticky"><tr><th>Eventid</th><th>Product</th><th>WFO</th><th>Start (UTC)</th><th>End</th>
 <th>Counties/Parishes</th>
 <th>Wind Tag</th><th>Hail Tag</th><th>Tornado Tag</th><th>Damage Tag</th>
 <th>Storm Speed (kts)</th></tr></thead>
 <tbody>
EOM;
$tortable = str_replace('svr-table', 'tor-table', $svrtable);
$smwtable = <<<EOM
 <table id='smw-table' class="table table-sm table-striped table-bordered">
 <thead class="sticky"><tr><th>Eventid</th><th>Product</th><th>WFO</th><th>Start (UTC)</th><th>End</th>
 <th>Counties/Parishes</th>
 <th>Wind Tag</th><th>Hail Tag</th><th>Waterspout Tag</th>
 <th>Storm Speed (kts)</th></tr></thead>
 <tbody>
EOM;
$ffwtable = <<<EOM
 <table id='ffw-table' class="table table-sm table-striped table-bordered">
 <thead class="sticky"><tr><th>Eventid</th><th>Product</th><th>WFO</th><th>Start (UTC)</th><th>End</th>
 <th>Counties/Parishes</th>
 <th>Flash Flood Tag</th><th>Damage Tag</th>
 <th>Heavy Rain Tag</th><th>Dam Tag</th>
 <th>Leeve Tag</th></tr></thead>
 <tbody>
EOM;

$data = file_get_contents($jsonuri);
$json = json_decode($data, $assoc = TRUE);

// Enhanced bean counting to track all tag types and prevent double counting
$counts = [
    "SV" => [
        "events" => [],
        "tags" => [
            "windtag" => [],
            "hailtag" => [],
            "tornadotag" => [],
            "damagetag" => []
        ]
    ],
    "TO" => [
        "events" => [],
        "tags" => [
            "windtag" => [],
            "hailtag" => [],
            "tornadotag" => [],
            "damagetag" => []
        ]
    ],
    "MA" => [
        "events" => [],  
        "tags" => [
            "windtag" => [],
            "hailtag" => [],
            "waterspouttag" => []
        ]
    ],
    "FF" => [
        "events" => [],
        "tags" => [
            "floodtag_flashflood" => [],
            "floodtag_damage" => [],
            "floodtag_heavyrain" => [],
            "floodtag_dam" => [],
            "floodtag_leeve" => []
        ]
    ]
];

// Process each warning record
foreach ($json['results'] as $key => $val) {
    $ph = $val["phenomena"];
    $eventid = $val["eventid"];
    
    // Track unique events per phenomena type
    $counts[$ph]["events"][$eventid] = 1;
    
    // Track tag usage per event (prevents double counting when same event has multiple records)
    foreach ($counts[$ph]["tags"] as $tagName => $tagCounts) {
        if (isset($val[$tagName]) && $val[$tagName] !== null && $val[$tagName] !== '') {
            $tagValue = (string)$val[$tagName];
            // Initialize tag value array if doesn't exist
            if (!isset($counts[$ph]["tags"][$tagName][$tagValue])) {
                $counts[$ph]["tags"][$tagName][$tagValue] = [];
            }
            
            // Only count once per event (prevents double counting)
            $counts[$ph]["tags"][$tagName][$tagValue][$eventid] = 1;
        }
    }

    // Build the table rows
    if ($ph == 'SV') {
        $svrtable .= do_row($val);
    } elseif ($ph == 'TO') {
        $tortable .= do_row($val);
    } elseif ($ph == 'MA') {
        $smwtable .= do_row_ma($val);
    } else {
        $ffwtable .= do_row_ffw($val);
    }
}

// Function to generate statistics summary
function generateStatsSummary($counts) {
    $phenomena_names = [
        "SV" => "Severe Thunderstorm",
        "TO" => "Tornado", 
        "MA" => "Marine",
        "FF" => "Flash Flood"
    ];
    
    $tag_labels = [
        "windtag" => "Wind Tag",
        "hailtag" => "Hail Tag", 
        "tornadotag" => "Tornado Tag",
        "damagetag" => "Damage Tag",
        "waterspouttag" => "Waterspout Tag",
        "floodtag_flashflood" => "Flash Flood Tag",
        "floodtag_damage" => "Flood Damage Tag",
        "floodtag_heavyrain" => "Heavy Rain Tag",
        "floodtag_dam" => "Dam Tag",
        "floodtag_leeve" => "Levee Tag"
    ];
    
    $summary = [];
    
    foreach ($counts as $phenomena => $data) {
        $totalEvents = count($data["events"]);
        $phenName = $phenomena_names[$phenomena] ?? $phenomena;
        
        if ($totalEvents > 0) {
            $summary[$phenomena] = [
                "name" => $phenName,
                "total_events" => $totalEvents,
                "tags" => []
            ];
            
            foreach ($data["tags"] as $tagName => $tagValues) {
                if (!empty($tagValues)) {
                    $tagLabel = $tag_labels[$tagName] ?? $tagName;
                    $tagStats = [];
                    
                    // Calculate percentage for each individual tag value
                    foreach ($tagValues as $tagValue => $events) {
                        $eventCount = count($events);
                        $percentage = round(($eventCount / $totalEvents) * 100, 1);
                        $tagStats[$tagValue] = [
                            "count" => $eventCount,
                            "percentage" => $percentage
                        ];
                    }
                    
                    $summary[$phenomena]["tags"][$tagName] = [
                        "label" => $tagLabel,
                        "values" => $tagStats
                    ];
                }
            }
        }
    }
    
    return $summary;
}

$statsummary = generateStatsSummary($counts);

$svrtable .= "</tbody></table>";
$tortable .= "</tbody></table>";
$ffwtable .= "</tbody></table>";
$smwtable .= "</tbody></table>";

$tselect = make_select("damagetag", $damagetag, $damagetags);

$yselect = yearSelect(2002, $year, 'year');
$wselect = networkSelect("WFO", $wfo, array(), "wfo");
$gentime = $json["gentime"];

$t->content = <<<EOM
 <div class="container-fluid">
     <nav aria-label="breadcrumb">
         <ol class="breadcrumb">
             <li class="breadcrumb-item"><a href="/nws/">NWS Resources</a></li>
             <li class="breadcrumb-item active" aria-current="page">List Warning Tags Issued</li>
         </ol>
     </nav>
     
     <div class="row">
         <div class="col-12">
             <div class="alert alert-info d-flex align-items-start" role="alert">
                 <i class="bi bi-info-circle-fill me-2 flex-shrink-0" style="font-size: 1.2rem;"></i>
                 <div>
                     <strong>About This Application:</strong> This tool lists Flash Flood, Marine, Severe Thunderstorm,
                     and Tornado Warnings issued by the National Weather Service for a given year, including metadata tags 
                     from initial warnings or followup statements.
                     <br><strong>Important:</strong> Not all offices include these tags in their warnings! 
                     Data goes back to 2002, though tags weren't used until recent years.
                 </div>
             </div>
         </div>
     </div>
     
     <form method="GET" name="one" class="mb-4">
         <div class="card">
             <div class="card-header bg-light">
                 <h5 class="card-title mb-0">
                     <i class="bi bi-funnel-fill me-2"></i>Filter Options
                 </h5>
             </div>
             <div class="card-body">
                 <div class="row g-3">
                     <div class="col-lg-4">
                         <fieldset class="border rounded p-3 h-100">
                             <legend class="fs-6 fw-bold text-primary">Search Criteria</legend>
                             
                             <div class="form-check mb-3">
                                 <input type="radio" name="opt" value="bywfo" id="bywfo" 
                                        class="form-check-input" {$bywfochecked}> 
                                 <label for="bywfo" class="form-check-label fw-medium">
                                     <i class="bi bi-geo-alt-fill me-1"></i>By Weather Forecast Office (WFO)
                                 </label>
                             </div>
                             <div class="mb-3 ms-4">
                                 <label for="wfo" class="form-label visually-hidden">Select WFO</label>
                                 {$wselect}
                             </div>

                             <div class="form-check mb-3">
                                 <input type="radio" name="opt" value="bydamagetag" id="bydamagetag" 
                                        class="form-check-input" {$bydamagetagchecked}> 
                                 <label for="bydamagetag" class="form-check-label fw-medium">
                                     <i class="bi bi-exclamation-triangle-fill me-1"></i>By Damage Tag Level
                                 </label>
                             </div>
                             <div class="mb-3 ms-4">
                                 <label for="damagetag" class="form-label visually-hidden">Select Damage Tag</label>
                                 {$tselect}
                             </div>
                         </fieldset>
                     </div>
                     
                     <div class="col-lg-3">
                         <fieldset class="border rounded p-3 h-100">
                             <legend class="fs-6 fw-bold text-primary">Time Period</legend>
                             <label for="year" class="form-label fw-medium">
                                 <i class="bi bi-calendar3 me-1"></i>Select Year:
                             </label>
                             {$yselect}
                         </fieldset>
                     </div>
                     
                     <div class="col-lg-2 d-flex align-items-end">
                         <button type="submit" class="btn btn-primary btn-lg w-100">
                             <i class="bi bi-search me-2"></i>Generate Report
                         </button>
                     </div>
                     
                     <div class="col-lg-3">
                         <div class="card bg-light h-100">
                             <div class="card-body">
                                 <h6 class="card-title">
                                     <i class="bi bi-download me-1"></i>Data Access
                                 </h6>
                                 <p class="card-text small mb-2">
                                     JSON webservice available at:
                                 </p>
                                 <code class="small text-break">{$publicjsonuri}</code>
                                 <div class="mt-2">
                                     <a href="/json/" class="btn btn-outline-secondary btn-sm">
                                         <i class="bi bi-info-circle me-1"></i>API Docs
                                     </a>
                                 </div>
                             </div>
                         </div>
                     </div>
                 </div>
             </div>
         </div>
     </form>
     
     <div class="alert alert-warning d-flex align-items-center mb-4" role="alert">
         <i class="bi bi-clock-fill me-2 flex-shrink-0"></i>
         <div>
             <strong>Data Generation:</strong> Based on data generated at <code>{$json["generated_at"]}</code>. 
             Tables are cached for approximately one hour - check back later for updated values.
         </div>
     </div>

     <!-- Statistics Summary -->
     <div class="row mb-4">
         <div class="col-12">
             <div class="card">
                 <div class="card-header bg-light">
                     <h5 class="card-title mb-0">
                         <i class="bi bi-bar-chart-fill me-2"></i>Warning Tag Statistics Summary
                     </h5>
                 </div>
                 <div class="card-body">
                     <div class="row g-3">
    <p>This table summarizes the tag counts by considering each warning's lifecycle
    and tries to avoid double counting.  For example, a CONSIDERABLE damage tag
    used anywhere in the lifecycle would count as 1 event for that tag. This
    also means that the shown percentages will sometimes add up to a value
    greater than 100%, since tags update with the product lifecycle.</p>
EOM;

foreach ($statsummary as $phenomena => $stats) {
    $t->content .= <<<EOM
                         <div class="col-md-6 col-lg-3">
                             <div class="card h-100 border-secondary">
                                 <div class="card-header bg-secondary text-white">
                                     <h6 class="card-title mb-0">{$stats['name']} Warnings</h6>
                                 </div>
                                 <div class="card-body">
                                     <div class="mb-2">
                                         <strong>Total Events:</strong> <span class="badge bg-primary">{$stats['total_events']}</span>
                                     </div>
EOM;
    
    foreach ($stats['tags'] as $tagName => $tagData) {
        $t->content .= <<<EOM
                                     <div class="mb-3">
                                         <small class="text-muted fw-bold">{$tagData['label']}:</small>
                                         <table class="table table-sm table-striped mt-1">
                                             <thead>
                                                 <tr>
                                                     <th>Value</th>
                                                     <th>Count</th>
                                                     <th>%</th>
                                                 </tr>
                                             </thead>
                                             <tbody>
EOM;
        
        // Show individual tag values with their counts and percentages in table rows
        foreach ($tagData['values'] as $value => $valueData) {
            $t->content .= <<<EOM
                                                 <tr>
                                                     <td><code>{$value}</code></td>
                                                     <td>{$valueData['count']}</td>
                                                     <td>{$valueData['percentage']}%</td>
                                                 </tr>
EOM;
        }
        
        $t->content .= <<<EOM
                                             </tbody>
                                         </table>
                                     </div>
EOM;
    }
    
    $t->content .= <<<EOM
                                 </div>
                             </div>
                         </div>
EOM;
}

$t->content .= <<<EOM
                     </div>
                 </div>
             </div>
         </div>
     </div>

 <div class="warning-tables">
     <div class="row g-4">
         <div class="col-lg-6">
             <div class="card h-100">
                 <div class="card-header bg-danger text-white d-flex align-items-center">
                     <i class="bi bi-tornado me-2" style="font-size: 1.5rem;"></i>
                     <h4 class="mb-0">Tornado Warnings</h4>
                 </div>
                 <div class="card-body">
                     <p class="card-text text-muted mb-3">
                         Tornado warnings with associated impact-based warning tags and damage assessments.
                     </p>
                     <button id="create-grid-tor" class="btn btn-danger mb-3" type="button">
                         <i class="bi bi-table me-2"></i>Enable Interactive Table
                     </button>
                     <div class="table-responsive">
                         {$tortable}
                     </div>
                 </div>
             </div>
         </div>
         
         <div class="col-lg-6">
             <div class="card h-100">
                 <div class="card-header bg-warning text-dark d-flex align-items-center">
                     <i class="bi bi-lightning-fill me-2" style="font-size: 1.5rem;"></i>
                     <h4 class="mb-0">Severe Thunderstorm Warnings</h4>
                 </div>
                 <div class="card-body">
                     <p class="card-text text-muted mb-3">
                         Severe thunderstorm warnings including wind, hail, and tornado tags with storm speed data.
                     </p>
                     <button id="create-grid-svr" class="btn btn-warning mb-3" type="button">
                         <i class="bi bi-table me-2"></i>Enable Interactive Table
                     </button>
                     <div class="table-responsive">
                         {$svrtable}
                     </div>
                 </div>
             </div>
         </div>
         
         <div class="col-lg-6">
             <div class="card h-100">
                 <div class="card-header bg-info text-white d-flex align-items-center">
                     <i class="bi bi-water me-2" style="font-size: 1.5rem;"></i>
                     <h4 class="mb-0">Flash Flood Warnings</h4>
                 </div>
                 <div class="card-body">
                     <p class="card-text text-muted mb-3">
                         Flash flood warnings with flood impact tags, heavy rain indicators, and infrastructure threats.
                     </p>
                     <button id="create-grid-ffw" class="btn btn-info mb-3" type="button">
                         <i class="bi bi-table me-2"></i>Enable Interactive Table
                     </button>
                     <div class="table-responsive">
                         {$ffwtable}
                     </div>
                 </div>
             </div>
         </div>
         
         <div class="col-lg-6">
             <div class="card h-100">
                 <div class="card-header bg-primary text-white d-flex align-items-center">
                     <i class="bi bi-water me-2" style="font-size: 1.5rem;"></i>
                     <h4 class="mb-0">Marine Warnings</h4>
                 </div>
                 <div class="card-body">
                     <p class="card-text text-muted mb-3">
                         Marine weather warnings including wind, hail, and waterspout tags for coastal and offshore areas.
                     </p>
                     <button id="create-grid-smw" class="btn btn-primary mb-3" type="button">
                         <i class="bi bi-table me-2"></i>Enable Interactive Table
                     </button>
                     <div class="table-responsive">
                         {$smwtable}
                     </div>
                 </div>
             </div>
         </div>
     </div>
 </div>
 </div>

EOM;
$t->render('full.phtml');
