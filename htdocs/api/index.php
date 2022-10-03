<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 123);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "API Documentation";

$t->content = <<< EOF

<h2>IEM API</h2>

<p><a class="btn btn-default" href="/api/1/docs"><i class="fa fa-info"></i> IEM API v1 Docs</a></p>

<p>The primary goal of this website is to make data freely available in an
open manner. This page presents details the IEM's Application Programming
Interface (API).</p>

<h3>But first, perhaps there are better alternatives!</h3>

<blockquote>
<p>The following is a list of other web service providers.  They all do a better
job than this website does.  Some of these are commercial and this listing should
not be implied as an endorsement. Of course, you can just search google for
<a href="https://www.google.com/search?q=weather+api">Weather API</a> :)</p>

<ul>
 <li><a href="https://www.aerisweather.com/develop/">Aeris Weather</a></li>
 <li><a href="https://developer.baronweather.com/">Baron Weather</a></li>
 <li><a href="https://realearth.ssec.wisc.edu/doc/api.php">SSEC RealEarth API</a></li>
 <li><a href="https://www.visualcrossing.com/weather-api">Visual Crossing Weather</a></li>
 <li><a href="https://www.weatherbit.io/api/">Weatherbit API</a></li>
</ul>
</blockquote>

<p>But you are here wondering about the IEM's API services?  Presently, there are
two portals with information about IEM APIs:

<ol>
 <li><a href="/json/">Legacy ad-hoc/legacy (Geo)JSON services</a>
  <br />These have been around for a while and while they work, they are generally
  somewhat brittle.</li>
 <li><a href="/api/1/docs">IEM API v1 Documentation</a>
  <br />Work is ongoing now to migrate the services found in #1 above into a more
  robust and self-documenting API system.  This is the future and will see
  significant expansion during 2020.</li> 
</ol>

<h3>API Stability?</h3>

<p>In general, we do not try to break things but bugs happen.  The plan is to
auto-redirect any of the legacy services into the more modern API system.  As always,
please <a href="/info/contacts.php">email us</a> with any concerns you have.  We
are extremely responsive to email :)

<h3>Service Changes</h3>

<ul>
 <li><strong>24 April 2020:</strong> Update this page to reflect the new API services
 and migrate the backend to use it!</li>
</ul>

EOF;

$t->render('single.phtml');
