<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->iem_resource = "NWSTEXT";
$t->title = "NWS Text Archives";

$d = date("Y/m/d");

$t->content = <<<EOM
<ol class="breadcrumb">
 <li><a href="/">IEM Homepage</a></li>
 <li><a href="/nws/">NWS Mainpage</a></li>
 <li class="active">NWS Text Archives</li>
</ol>

<p>The IEM attempts a robust processing and archival of National Weather
Service issued text products.  This page details the many ways that you can
access this data. Unless denoted otherwise, all of these resources update
in realtime.</p>

<p>A common nomenclature used by the IEM is to assign an identifier, that
unfortunately is not always unique because of lame NWS bugs, to each product.
These look like so <code>YYYYmmddHHMM-CCCC-TTAAII-AFOSID(-BBB:optional)</code>.
The timestamp is UTC, the CCCC is the issuance center, TTAAII is the WMO
header, the AFOSID is a 3 to 6 character identifier, sometimes called AWIPS ID,
and the final -BBB field is only used when that is included in the product.
This value is often available within various NWS data APIs within the IEM.</p>

<p><strong>Pro-tip</strong>. You can enter this identifier into the IEM website
search box to find the product quickly. The
<a href="/api/1/docs#/nws/nwstext_service_nwstext__product_id__get">nwstext API</a>
is the main place to use this identifier.</p>

<div class="row">
<div class="col-md-6">

<div class="panel panel-default">
  <div class="panel-heading">IEM News Items</div>
  <div class="panel-body">

  <ul>
<li>See this <a href="/onsite/news.phtml?id=1408">news item</a> for more details
on this archive and how it is made available.</li>
  </ul>

</div>
</div>

<div class="panel panel-default">
  <div class="panel-heading">User Somewhat-Friendly Frontends</div>
  <div class="panel-body">
<ul>
   <li><a href="/wx/afos/">AFOS Product Finder</a>
  <br />If you know what you are looking for, this app works great!</li>
   <li><a href="/wx/afos/list.phtml">List Products by WFO by Date</a>
  <br />View quick listings of issued products by forecast office and by date.</li>
</ul>

  </div>
</div>

<div class="panel panel-default">
  <div class="panel-heading">Raw Text / Scrapable Archives</div>
  <div class="panel-body">

<ul>
 <li><a href="https://mtarchive.geol.iastate.edu/{$d}/text/cap/">
 Common Alert Protocol (CAP) Hourly Files</a>
  <br />This mtarchive resource contains hourly files of CAP messages.</li>
 <li><a href="/archive/data/{$d}/text/noaaport/">Simple directory listing</a>
  <br />Certain warning type products can be found in the main IEM data archive
  directory structure in per UTC date directories.</li>
  <li><a href="/archive/rer/">NWS Record Event Reports</a>
  <br />Daily reports of record temperatures and precipitation for
   mostly <strong>Iowa</strong> since November 2001. <code>manually populated</code></li>
</ul>

  </div>
</div>

</div><div class="col-md-6">

<div class="panel panel-default">
  <div class="panel-heading">API / Bulk Downloads</div>
  <div class="panel-body">

<p>Many folks use the IEM as a near realtime data source.  This section details
some of the techniques used.</p>

<p>The primary service used is the
<a href="/cgi-bin/afos/retrieve.py?help">AFOS retrieve</a> service.  It supports
date range queries by AWIPS IDs (ie <code>TORDMX</code>, <code>AFDDMX</code>).
There is also a <a href="/api/1/docs#/nws/service_nws_afos_list__fmt__get">
metadata list</a> service which helps to find available products for a given
date and issuance center.</p>

<p>Another technique involves using the scrapable archives shown on this page,
with subsequent HTTP requests using HTTP-range headers to download the data
efficiently.</p>

  </div>
</div>


<div class="panel panel-default">
  <div class="panel-heading">Misc / Statistics</div>
  <div class="panel-body">
<ul>
  <li><a href="/plotting/auto/?q=210">Map of Text Product Issuance Counts</a>
  <br />Autoplot 210 will generate maps of how many text products are
  issued for a given product type. It will also plot the first and last
  usage of a product.</li>
</ul>
  </div>
</div>

</div>
</div><!-- ./row -->

EOM;
$t->render('single.phtml');
