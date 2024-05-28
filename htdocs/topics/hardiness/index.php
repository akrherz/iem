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
$img25 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:25.png", $state);
$img15 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:15.png", $state);
$img10 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:10.png", $state);
$img0 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:0.png", $state);
$imgn10 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:-10.png", $state);
$imgn15 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:-15.png", $state);
$imgn20 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:-20.png", $state);
$imgn30 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:-30.png", $state);
$imgn40 = sprintf(
    "/plotting/auto/plot/252/var:low::w:below::sector:%s::popt:contour::" .
    "sday:1001::eday:0331::threshold:-40.png", $state);
        

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

<p>Skip down to threshold:
<a href="#32">32&deg;F</a>,
<a href="#25">25&deg;F</a>,
<a href="#15">15&deg;F</a>,
<a href="#10">10&deg;F</a>,
<a href="#0">0&deg;F</a>,
<a href="#n10">-10&deg;F</a>,
<a href="#n15">-15&deg;F</a>,
<a href="#n20">-20&deg;F</a>,
<a href="#n30">-30&deg;F</a>,
<a href="#n40">-40&deg;F</a></p>

<form method="GET" name="sswitch">
<p>$sselect <input type="submit" value="Switch State"></p>
</form>

<h3>Low Temperature below 32&deg;F</h3>

<p>Buckwheat, Cowpea, Millets, Mungbean, Sorghum Forage, Sorghum-Sundangrass,
Sundangrass, Sunn Hemp, Teff</p>

<img src="$img32" class="img img-responsive" alt="Low Temperature below 32F" />

<!-- ................................. -->

<h3>Low Temperature below 25&deg;F</h3>

<p>Barley Spring, Flax, Oats, Sunflower, Wheat Spring</p>

<img src="$img25" class="img img-responsive" alt="Low Temperature below 32F" />

<!-- ................................. -->

<h3>Low Temperature below 15&deg;F</h3>

<pClover Berseem, Kale, Mustard, Radish</p>

<img src="$img15" class="img img-responsive" alt="Low Temperature below 32F" />

<!-- ................................. -->

<h3>Low Temperature below 10&deg;F</h3>

<p>Clover Crimson, Turnip, Vetch Common</p>

<img src="$img10" class="img img-responsive" alt="Low Temperature below 10F" />

<!-- ................................. -->

<h3>Low Temperature below 0&deg;F</h3>

<p>Barley Winter, Rapeseed, Ryegrass Annual</p>

<img src="$img0" class="img img-responsive" alt="Low Temperature below 0F" />

<!-- ................................. -->

<h3>Low Temperature below -10&deg;F</h3>

<p>Pea Winter/Field</p>

<img src="$imgn10" class="img img-responsive" alt="Low Temperature below -10F" />

<!-- ................................. -->

<h3>Low Temperature below -15&deg;F</h3>

<p>Vetch Hairy, Wheat Winter</p>

<img src="$imgn15" class="img img-responsive" alt="Low Temperature below -10F" />

<!-- ................................. -->

<h3>Low Temperature below -20&deg;F</h3>

<p>Camelina Winter, Triticale Winter</p>

<img src="$imgn20" class="img img-responsive" alt="Low Temperature below -10F" />


<!-- ................................. -->

<h3>Low Temperature below -30&deg;F</h3>

<p>Cereal Rye, Clover Red</p>

<img src="$imgn30" class="img img-responsive" alt="Low Temperature below -10F" />

<!-- ................................. -->

<h3>Low Temperature below -40&deg;F</h3>

<p>Clover White</p>

<img src="$imgn40" class="img img-responsive" alt="Low Temperature below -10F" />

EOM;
$t->render("full.phtml");
