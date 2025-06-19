<?php 
require_once "../../../../config/settings.inc.php";

require_once "../../../../include/myview.php";
require_once "../../../../include/mlib.php";
force_https();
$OL = "10.6.1";
$t = new MyView();
$t->title = "Profitability Map";
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link type="text/css" href="index.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="index.js"></script>
EOM;

$t->content = <<<EOM
<div class="row">
  <div class="col-md-12">
    <h3><i class="fa fa-bar-chart"></i> Iowa Corn/Soybean Profitability Map</h3>
    <p class="lead">
      This interactive map shows estimates of profitability for corn and soybean production 
      across Iowa fields. Select a year to view profitability data for that growing season.
    </p>
  </div>
</div>

<div class="row">
  <div class="col-md-9">
    <div class="card">
      <div class="card-body p-0">
        <div id="map" style="height: 500px; width: 100%;"></div>
      </div>
    </div>
  </div>
  
  <div class="col-md-3">
    <!-- Year Selection Panel -->
    <div class="card mb-3">
      <div class="card-header">
        <h6 class="mb-0">Select Year</h6>
      </div>
      <div class="card-body">
        <div class="btn-group-vertical d-grid gap-1" role="group" aria-label="Year selection">
          <input type="radio" class="btn-check" name="whichyear" id="y2010" value="2010" checked>
          <label class="btn btn-outline-primary" for="y2010">2010</label>
          
          <input type="radio" class="btn-check" name="whichyear" id="y2011" value="2011">
          <label class="btn btn-outline-primary" for="y2011">2011</label>
          
          <input type="radio" class="btn-check" name="whichyear" id="y2012" value="2012">
          <label class="btn btn-outline-primary" for="y2012">2012</label>
          
          <input type="radio" class="btn-check" name="whichyear" id="y2013" value="2013">
          <label class="btn btn-outline-primary" for="y2013">2013</label>
          
          <input type="radio" class="btn-check" name="whichyear" id="y2015" value="2015">
          <label class="btn btn-outline-primary" for="y2015">2015</label>
        </div>
      </div>
    </div>

    <!-- Legend Panel -->
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">Legend</h6>
      </div>
      <div class="card-body text-center">
        <img src="profit_legend.png" alt="Profitability Legend" class="img-fluid" />
      </div>
    </div>
  </div>
</div>

<div class="row mt-3">
  <div class="col-md-12">
    <div class="card">
      <div class="card-header">
        <button class="btn btn-link p-0 text-decoration-none" type="button" id="disclaimer_btn" 
                data-bs-toggle="collapse" data-bs-target="#disclaimerContent" 
                aria-expanded="false" aria-controls="disclaimerContent">
          <i class="fa fa-info-circle"></i> View Disclaimer
        </button>
      </div>
      <div class="collapse" id="disclaimerContent">
        <div class="card-body">
          <p>
          This map shows estimates of profitability of fields in corn or
          soybean. This map is meant to provide insight into alternative land
          management to improve farm profitability using publically available
          (and funded) data, thus allowing access without purchase of a private
          farm data management plan. While useful for insight into relative
          performance of areas within fields, and representative of Iowa farm
          management, this map does not contain individual economic or
          management data, and actual profitability will depend on actual
          expenses, revenue and management. We present a snapshot of the
          current possibilities with the available data and hope to improve
          this map in the future to allow user-defined values for
          individualized results. Local variations of yields, management and
          marketing practices, land tenure, and inaccuracy of the underlying
          spatial data result in deviations from the estimates presented here.
          </p>

          <p>For a complete
          description of the underlying data and methods, please refer to the
          research article "Subfield profitability analysis reveals an
          economic case for cropland diversification," that can be freely
          accessed <a href="http://iopscience.iop.org/article/10.1088/1748-9326/11/1/014009/meta;jsessionid=0059946EA9A46A2380CB698ABA6BAA8C.c4.iopscience.cld.iop.org">online</a>.
          </p>

          <p>The analysis was
          performed for fields that were planted in corn or soybeans according
          to the <a href="http://nassgeodata.gmu.edu/CropScape/">cropland data
          layer</a> (CDL) for 2010-2013. The 2013 CDL was used for 2015.
          Patches of similar profitability are defined by <a href="http://websoilsurvey.sc.egov.usda.gov/">soil
          survey</a> (SSURGO) and <a href="http://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-products/common-land-unit-clu/index">common
          land unit</a> (CLU, 2008) delineations. Profitability was calculated
          by deducting cash rent and crop production cost estimates from the
          crop revenue (crop yield x grain price). Potential yields were taken
          from the <a href="http://www.extension.iastate.edu/soils/ispaid">Iowa
          soil properties and interpretations database (ISPAID)</a> and
          adjusted to <a href="http://quickstats.nass.usda.gov">average county
          yields</a> (NASS, 2010-2013) or to <a href="http://webapp.rma.usda.gov/apps/actuarialinformationbrowser/">trend
          county yields</a> (USDA RMA, 2015). Grain prices are the average
          monthly prices of each marketing year, and the forecast for 2015 from
          the <a href="http://usda.mannlib.cornell.edu/MannUsda/viewDocumentInfo.do?documentID=1194">USDA
          WASDE report</a> of May 2016. Cash rents are taken from <a href="https://www.extension.iastate.edu/agdm/wholefarm/html/c2-10.html">county
          surveys</a> (ISU extension, 2010-2013, 2015), adjusted to corn
          suitability rating (CSR). Crop production costs were taken from the
          <a href="http://www.extension.iastate.edu/agdm/crops/html/a1-20.html">ISU
          Ag Decision Maker cost estimates</a>.
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

EOM;

$t->render('full.phtml');
