<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/sites.php";
require_once "../../include/myview.php";

$ctx = get_sites_context();
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;

$station4 = (strlen($station) == 3) ? sprintf("K%s", $station) : $station;
$station3 = substr($station4, 1, 3);

$t = new MyView();
$t->title = "Terminal Aerodome Forecasts";
$t->sites_current = "taf";
$t->jsextra = <<<EOM
<script>
$(document).ready(function(){
    $.ajax({
        url: "/cgi-bin/afos/retrieve.py?pil=TAF{$station3}&fmt=html",
        success: function(data){
            $("#rawtext").html(data);
        }
    });

});
</script>
EOM;

$t->content = <<<EOF
<h3>Terminal Aerodome Forecasts</h3>

<p>The IEM processes the feed of Terminal Aerodome Forecasts from the NWS.  This
page presents some of the options available for this dataset. A
<a href="/request/taf.php">download option</a> exists as well.</p>

<h4>Raw Text</h4>

<div id="rawtext"></div>

<h4>IEM Visualization</h4>

<p>IEM <a href="/plotting/auto/?q=219&station={$station4}">Autoplot 219</a> produced
this visualization:</p>

<p><img src="/plotting/auto/plot/219/station:{$station4}.png" class="img img-responsive"></p>

EOF;
$t->render('sites.phtml');
