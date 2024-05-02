<?php
define("IEM_APPID", 160);

// Pest DD Maps
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";
require_once "../../../include/imagemaps.php";

// Get things set via CGI
$state = isset($_GET["state"]) ? substr(xssafe($_GET["state"]), 0, 2) : "IA";


$sselect = stateSelect($state, "state");

$t = new MyView();
$t->title = "Winter Hardiness Maps";
$t->jsextra = <<<EOM
EOM;
$t->headextra = <<<EOM
EOM;

$img32 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:32.png", $state);
$img10 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:10.png", $state);
$img0 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:0.png", $state);
$imgn10 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:-10.png", $state);


$t->content = <<<EOM
<ol class="breadcrumb">
 <li><a href="/agweather/">Ag Weather</a></li>
 <li class="active">State Hardiness Maps</li>
 </ol>

<p>This page generates maps showing yearly frequency of having at least one
day with a low temperature below a given threshold.  These types of maps
drive hardiness recommendations.  The frequencies are based on period of record
data, which generally is 50-70 years or more for the sites used within the map.
The IEM plotting backend is <a href="/plotting/auto/?q=252">autoplot 252</a>.</p>

<form method="GET" name="sswitch">
<p>$sselect <input type="submit" value="Switch State"></p>
</form>


<h3>Low Temperature below 32&deg;F</h3>

<img src="$img32" class="img img-responsive" alt="Low Temperature below 32F" />

<h3>Low Temperature below 10&deg;F</h3>

<img src="$img10" class="img img-responsive" alt="Low Temperature below 10F" />

<h3>Low Temperature below 0&deg;F</h3>

<img src="$img0" class="img img-responsive" alt="Low Temperature below 0F" />

<h3>Low Temperature below -10&deg;F</h3>

<img src="$imgn10" class="img img-responsive" alt="Low Temperature below -10F" />

EOM;
$t->render("full.phtml");
