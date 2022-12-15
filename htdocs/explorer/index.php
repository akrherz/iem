<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 138);
require_once "../../include/myview.php";
$OL = "7.1.0";
$t = new MyView();
$t->title = "IEM Explorer";
$t->headextra = <<<EOM
<link rel='stylesheet' href="/vendor/openlayers/${OL}/ol.css" type='text/css'>
<link rel='stylesheet' href="/vendor/openlayers/${OL}/ol-layerswitcher.css" type='text/css'>
<link rel="stylesheet" href="/vendor/jquery-ui/1.13.2/jquery-ui.css">
<link rel="stylesheet" type="text/css" href="explorer.css" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script src='/vendor/openlayers/${OL}/ol.js'></script>
<script src='/vendor/openlayers/${OL}/ol-layerswitcher.js'></script>
<script src="/vendor/jquery-ui/1.13.2/jquery-ui.js"></script>
<script src="/vendor/highcharts/10.1.0/highcharts.js"></script>
<script src="/vendor/highcharts/10.1.0/highcharts-more.js"></script>
<script src="/vendor/highcharts/10.1.0/modules/accessibility.js"></script>
<script src="/vendor/highcharts/10.1.0/modules/exporting.js"></script>
<script src="/vendor/highcharts/10.1.0/modules/heatmap.js"></script>
<script src="app.js"></script>
<script src="dialog.js"></script>
EOM;

$t->content = <<<EOM
    <div id="popover">
        <span id="info-name"></span>
    </div>

    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <div class="row">
        <div class="col-md-2" style="padding-left: 30px; height: 700px;">
            <strong>Symbol Legend:</strong>
            <br /><input type="checkbox" id="isusm" checked="checked" onclick="changeStations(this);">
              <label for="isusm"><img src="img/isu.svg" style="height: 30px;"> ISU Soil Moisture</label>
            <br /><input type="checkbox" id="asos" checked="checked" onclick="changeStations(this);">
              <label for="asos"><img src="img/airport.svg" style="height: 30px;"> Airports</label>
            <br /><input type="checkbox" id="coop" checked="checked" onclick="changeStations(this);">
              <label for="coop"><img src="img/green_dot.svg" style="height: 30px;"> Climate Stations</label>
            <br /><input type="checkbox" id="cd" checked="checked" onclick="changeStations(this);">
              <label for="cd"><img src="img/blue_square.svg" style="height: 30px;"> Climate Districts </label>
            <br /><input type="checkbox" id="state" checked="checked" onclick="changeStations(this);">
              <label for="state"><img src="img/red_square.svg" style="height: 30px;"> State Averages</label>

            <br /><div id="overviewmap"></div>
        </div>
        <div class="col-md-8" style="padding-left: 25px;">
            <strong>Click symbol on map to view available plots:</strong><br />
            <div id="olmap"></div>
        </div>
        <div class="col-md-2 maprow">
            <strong>4 inch Soil Temperatures</strong>
            <img src="/data/soilt_day1.png" role="button" title="4in Soil Temperatures"
             data-target="https://mesonet.agron.iastate.edu/agclimate/soilt.php">

             <br /><strong>Today's Precipitation</strong>
             <img src="/data/iowa_ifc_1d.png" role="button" title="Iowa Flood Center Rainfall"
            data-target="https://mesonet.agron.iastate.edu">

            <br /><strong>Precipitation Departure</strong>
            <img src="/plotting/auto/plot/84/sector:IA::src:mrms::opt:dep::usdm:yes::ptype:g::sdate:2022-08-01::cmap:BrBG::_r:43.png"
            role="button" title="Precip Departure Aug 1"
            data-target="https://mesonet.agron.iastate.edu">

            <br /><strong>Days to Accum 2 inches</strong>
            <img src="/plotting/auto/plot/185/sector:IA::threshold:2.0::cmap:terrain::_r:43.png" role="button"
            title="Days to Accumulate 2 inches"
            data-target="https://mesonet.agron.iastate.edu">

            <br /><strong>Iowa Drought Coverage</strong>
            <img src="/plotting/auto/plot/183/s:state::state:IA::sdate:2021-01-01::_r:43.png" role="button"
            title="Iowa Drought Coverage"
            data-target="https://mesonet.agron.iastate.edu">

            <br /><strong>NASS Corn Denting Progress</strong>
            <img src="/plotting/auto/plot/127/state:IA::short_desc:CD::cmap:jet::_r:43.png" role="button"
            title="USDA NASS Corn Denting Progress"
            data-target="https://mesonet.agron.iastate.edu/plotting/auto/?_wait=no&q=127&state=IA&short_desc=CD&cmap=jet&_r=43&dpi=100&_fmt=png">

            <br /><strong>Climate District Ranks</strong>
            <img src="/plotting/auto/plot/24/csector:midwest::var:precip::p:month::year:2022::month:summer::cmap:RdBu_r::_r:43.png" role="button"
            title="Climate District Precip Ranks"
            data-target="https://mesonet.agron.iastate.edu/plotting/auto/?_wait=no&q=24&csector=midwest&var=precip&p=month&year=2022&month=summer&sdate=2022%2F04%2F05&edate=2022%2F05%2F03&cmap=RdBu&cmap_r=on&_r=t&dpi=100&_fmt=png">

        </div>
    </div>

    <div class="row isusm-data-template ddisplay"
    style="display:none; min-height: 0px; height: 100%; width: 100%;">
       <div class="col-md-4" style="overflow-y: scroll; height: 100%;">
            <a class="btn btn-default" target="_blank" href="/sites/site.php?station={station}&amp;network={network}"><i class="fa fa-sign-out"></i> Site Mainpage</a>

           <button role="button" onClick="loaderClicked(this);" class="autoload"
            data-url-template="/plotting/auto/plot/145/network:ISUSM::station:{station}::var:tsoil::year:2022::_r:86.png"><i class="fa fa-thermometer-quarter"></i> 4in Soil Temps</button>
            <button role="button" onClick="loaderClicked(this);"
            data-url-template="/plotting/auto/plot/177/network:ISUSM::station:{station}::opt:sm::sts:2022-05-01%200000::_r:86.png"><i class="fa fa-tint"></i> Soil Moisture</button>
            <button role="button" onClick="loaderClicked(this);"
            data-url-template="/plotting/auto/plot/177/network:ISUSM::station:{station}::opt:7::sts:2022-05-01%200000::_r:86.png"><i class="fa fa-battery-half"></i> Available Soil Water</button>
           <button role="button" onClick="loaderClicked(this);"
            data-url-template="/plotting/auto/plot/177/network:ISUSM::station:{station}::opt:4::sts:2022-05-01%200000::_r:43.png"><i class="fa fa-sun-o"></i> Daily Solar Radiation</i></button>

       </div>
       <div class="col-md-8 data-display" style="overflow-y: auto;"></div>
   </div><!-- ./isuag-data-template -->

    <div class="row asos-data-template ddisplay"
     style="display:none; min-height: 0px; height: 100%; width: 100%;">
        <div class="col-md-4" style="overflow-y: scroll; height: 100%;">
            <a class="btn btn-default" target="_blank" href="/sites/site.php?station={station}&amp;network={network}"><i class="fa fa-sign-out"></i> Site Mainpage</a>

            <button role="button" onClick="loaderClicked(this);" class="autoload"
            data-url-template="/plotting/auto/plot/140/network:{network}::station:{station}::syear:1973::month:4::day:1::days:30::varname:avg_wind_speed::year:2022::_r:86.png">
            <i class="fa fa-leaf"></i> April Wind Speed</button>
            
            <button role="button" onClick="loaderClicked(this);"
            data-url-template="/plotting/auto/plot/140/network:{network}::station:{station}::syear:1973::month:6::day:1::days:92::varname:avg_dewp::year:2022::_r:43.png">
            <i class="fa fa-fire"></i> Summer Dew Points</button>
            
            <button role="button" onClick="loaderClicked(this);"
            data-url-template="/plotting/auto/plot/93/network:{network}::zstation:{station}::syear:1973::year:2022::var:heatindex::ytd:yes::inc:no::_r:43.png">
            <i class="fa fa-table"></i> 2022 Heat Index Hrs</button>

            <button role="button" onClick="loaderClicked(this);"
            data-url-template="/plotting/auto/plot/82/network:{network}::station:{station}::var:high_departure::sdate:2022-05-01::edate:2022-08-31::_r:43.png">
            <i class="fa fa-calendar"></i> 2022 Highs Calendar</button>

            <button role="button" onClick="loaderClicked(this);"
            data-url-template="/plotting/auto/plot/51/network:{network}::station:{station}::sdate:2022-05-01::base:50::ceil:86::year2:2021::year3:2019::which:gdd::_r:43.png">
            <i class="fa fa-fire"></i> 2022 GS Accum GDD</button>

            <button role="button" onClick="loaderClicked(this);"
            data-url-template="/plotting/auto/plot/51/network:{network}::station:{station}::sdate:2022-05-01::base:50::ceil:86::year2:2021::year3:2019::which:precip::_r:43.png">
            <i class="fa fa-tint"></i> 2022 GS Accum Precip</button>


            <h3>Wind Roses</h3>
            <strong>Month/Season:</strong>
            <select name="month">
                <option value="yearly">Calendar Year</option>
                <option value="jan">January</option>
                <option value="feb">February</option>
                <option value="mar">March</option>
                <option value="apr">April</option>
                <option value="may">May</option>
                <option value="jun">June</option>
                <option value="jul">July</option>
                <option value="aug" selected="selected">August</option>
                <option value="sep">September</option>
                <option value="oct">October</option>
                <option value="nov">November</option>
                <option value="dec">December</option>
            </select>
            <button role="button" onClick="loaderClicked(this);"
            data-url-template="/onsite/windrose/{network}/{station}/{station}_{month}.png">
            <i class="fa fa-pie-chart"></i> View Windrose</button>

        </div>
        <div class="col-md-8 data-display" style="overflow-y: auto;"></div>
    </div><!-- ./asos-data-template -->

    <div class="row coop-data-template ddisplay"
     style="display:none; min-height: 0px; height: 100%; width: 100%;">
        <div class="col-md-4" style="overflow-y: scroll; height: 100%;">
            <a class="btn btn-default" target="_blank" href="/sites/site.php?station={station}&amp;network={network}"><i class="fa fa-sign-out"></i> Site Mainpage</a>

            <button role="button" onClick="loaderClicked(this)" class="autoload"
            data-url-template="/plotting/auto/plot/3/network:{network}::station:{station}::month:year::type:avg-temp::_e:{elem}.js"
            ><i class="fa fa-thermometer-half"></i> Average Temperature</button>

            <br /><button role="button" onClick="loaderClicked(this)"
            data-url-template="/plotting/auto/plot/32/network:{network}::station:{station}::year:2022::var:high::gddbase:50::gddceil:86::how:diff::cmap:jet::_r:43.png"
            ><i class="fa fa-thermometer-quarter"></i> 2022 High Departures</button>

            <br /><button role="button" onClick="loaderClicked(this)"
            data-url-template="/plotting/auto/plot/3/network:{network}::station:{station}::month:year::type:max-precip::_e:{elem}.js"
            ><i class="fa fa-tint"></i> Daily Max Precip</button>

            <br /><button role="button" onClick="loaderClicked(this)"
            data-url-template="/plotting/auto/plot/3/network:{network}::station:{station}::month:spring::type:sum-precip::_e:{elem}.js"
            ><i class="fa fa-tint"></i> Spring Season Precip</button>

            <br /><button role="button" onClick="loaderClicked(this)"
            data-url-template="/plotting/auto/plot/10/network:{network}::station:{station}::direction:below::varname:low::threshold:32::year:1893::_r:86::dpi:100.png"
            ><i class="fa fa-tree"></i> Growing Season Days</button>

            <br /><button role="button" onClick="loaderClicked(this)"
            data-url-template="/plotting/auto/plot/142/network:{network}::station:{station}::p1:31::p2:91::p3:365::pvar:precip::how:diff::_r:86.png"
            ><i class="fa fa-star-half-o"></i> Drought Monitoring</button>

            <br /><button role="button" onClick="loaderClicked(this)"
            data-url-template="/plotting/auto/plot/215/network:{network}::station:{station}::v:high::month:all::sy1:1930::ey1:1939::sy2:2012::ey2:2021::_r:43.png"
            ><i class="fa fa-arrows-h"></i> 1930s vs 2010s</button>

            <br /><button role="button" onClick="loaderClicked(this)"
            data-url-template="/plotting/auto/plot/28/network:{network}::station:{station}::opt:rank::_r:43.png"
            ><i class="fa fa-refresh"></i> Precip Status</button>

            <br /><button role="button" onClick="loaderClicked(this)"
            data-url-template="/plotting/auto/plot/176/network:{network}::station:{station}::opt:0::w:daily::_e:{elem}.js"
            ><i class="fa fa-plus-circle"></i> Records Set by Year</button>

            <h3>Trends</h3>
            <strong>Variable:</strong>
            <select name="type">
                <option value="max-high">Maximum High</option>
                <option value="avg-high">Average High</option>
                <option value="min-high">Minimum High</option>
                <option value="max-low">Maximum Low</option>
                <option value="avg-low">Average Low</option>
                <option value="min-low">Minimum Low</option>
                <option value="avg-temp">Average Temp</option>
                <option value="range-avghi-avglo">Ave High + Low Range</option>
                <option value="max-precip">Maximum Daily Precip</option>
                <option value="sum-precip">Total Precipitation</option>
            </select>
            <br /><strong>Month/Season:</strong>
            <select name="month">
                <option value="year">Calendar Year</option>
                <option value="spring">Spring (MAM)</option>
                <option value="fall">Fall (SON)</option>
                <option value="winter">Winter (DJF)</option>
                <option value="summer">Summer (JJA)</option>
                <option value="1">January</option>
                <option value="2">February</option>
                <option value="3">March</option>
                <option value="4">April</option>
                <option value="5">May</option>
                <option value="6">June</option>
                <option value="7">July</option>
                <option value="8" selected="selected">August</option>
                <option value="9">September</option>
                <option value="10">October</option>
                <option value="11">November</option>
                <option value="12">December</option>
            </select>

            <button role="button" onClick="loaderClicked(this);"
             data-url-template="/plotting/auto/plot/3/network:{network}::station:{station}::month:{month}::type:{type}::_e:{elem}.js"><i class="fa fa-line-chart"></i> Create Chart</button>

        </div>
        <div class="col-md-8 data-display" style="overflow-y: auto;"></div>
    </div><!-- ./coop-data-template -->


EOM;
$t->render("full.phtml");
