<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "LDM Request HOWTO";

$t->content = <<<EOM
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/info.php">IEM Information</a></li>
        <li class="breadcrumb-item active" aria-current="page">Real-time IEM data feeds with LDM HOWTO</li>
    </ol>
</nav>

<p>The IEM uses <a href="https://www.unidata.ucar.edu">Unidata LDM</a> to move
data around within the computing infrastructure.  Anybody is eligable to request
a LDM feed, so to get products pushed to you without any fuss!  This page details
the setup of the LDM feed.</p>

<div class="alert alert-warning" role="alert">

<h3>Looking for low latency ASOS data? Read this first!</h3>

<p>
<strong>TL;DR There is no latency magic with the IEM LDM Feed.</strong>
</p>

<p>
The IEM continues to get incessant emails believing that the IEM offers some
magic feed of ASOS data with reduced latency allowing for gambling edge. Please
see <a href="https://mesonet.agron.iastate.edu/onsite/news.phtml?id=1469">Wagering
on ASOS temperatures</a> for related info on this topic.  While LDM is a push
technology that does offer products faster than what you could see off of government
websites with CDN / caching, it is also sourced from a data stream that bounces
off of geostationary satellites, which will have many seconds more of latency vs
folks that have a direct from FAA Internet feed.  Again no IEM LDM magic here,
but you insist there so, so we continue...
</p>

<p>
MADIS processes a stream of data from the FAA with reduced latency, but has
a major quick with temperatures reported in
<a href="https://mesonet.agron.iastate.edu/onsite/news.phtml?id=1290">Whole
degree Celsius</a> and without two minute averaging, which makes the data
very problematic to figure out high temperatures, but people don't believe this
again and demand the feed of this data from the IEM.  The IEM does not have
anything lower latency than what you find from the <a href="https://madis-data.cprk.ncep.noaa.gov/madisPublic1/data/LDAD/hfmetar/">
MADIS website of netcdf files</a>.  So again, we continue...
</p>

<p>
Folks still think the IEM LDM feed of NOAAPort/NWS data containining METAR/SPECIs/
CLIs/DSMs/CF6s will have lower latency and one minute updates, but it does not.
These are the legacy products with much latency, on the order of minutes for the METARs
to roundtrip the FAA / NWS to satellite broadcast. But the data is there and some
folks think it is going to provide some magic money making scheme, so we continue...
</p>

<p>
So what the IEM has is a <code>IDS|DDPLUS</code> feed of METARs (<code>^S[AP]</code>), CLIs (<code>/pCLI</code>),
DSMs (<code>^CDUS27</code>), and CF6s (<code>/pCF6</code>).  The METARs and DSMs are typically found in
product collectives, so the LDM product name does not contain the airport ICAO
code within the name.  You have to process the collectives and find your airport of
choice within it.  The IEM website does a value add of splitting these products into
airport based identifiers, but this data is not sent over the LDM feed.
</p>

<p>
So then finally after the IEM explains all this, people then ask where to find
lower latency data.  Goodness, yes, if the IEM knew, the IEM would be doing it already.
Guess what, it does not exist.  Perhaps ASOS modernization will fix this, but
until then perhaps check out
<a href="https://demos.synopticdata.com/hf-asos-available/index.html">Synoptic Data</a>
for a feed of the FAA data that goes into the MADIS product mentioned above.
</p>

</div>

<div class="row">
    <div class="col-lg-8">
        <div class="card mb-4">
            <div class="card-header">
                <h4 class="card-title mb-0">STEP 1: Send an Email</h4>
            </div>
            <div class="card-body">
                <p>Send us an email requesting a LDM feed. You can send this email to me, Daryl
                Herzmann (<a href="mailto:akrherz@iastate.edu">akrherz@iastate.edu</a>). You should include contact information
                and the DNS/IP of the host that you will be using to connect to the IEM LDM.</p>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header">
                <h4 class="card-title mb-0">STEP 2: Configure LDM (ldmd.conf)</h4>
            </div>
            <div class="card-body">
                <p>All local products are generated within the <code>EXP</code> LDM feedtype. A
                nomenclature is used within the IEM to help with product routing. The general
                form is: <code>datatype routes timestamp archive_path current_path suffix</code></p>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header">
                <h4 class="card-title mb-0">STEP 3: Sign up for IEM bulletin (optional)</h4>
            </div>
            <div class="card-body">
                <p>You don't have to complete this step, but you can keep up-to-date with
                IEM news and events with the IEM Daily Bulletin. You can sign up for it
                <a href="https://groups.google.com/g/iem-dailyb" target="_blank">here</a>.
                If this service generates enough interest, I will set up a dedicated
                email list for it.</p>
            </div>
        </div>
    </div>

    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">Contact Information</h5>
            </div>
            <div class="card-body">
                <address>
                    <strong>Daryl Herzmann</strong><br>
                    Email: <a href="mailto:akrherz@iastate.edu">akrherz@iastate.edu</a><br>
                    <small class="text-muted">Rev: 26 Dec 2002</small>
                </address>
            </div>
        </div>
    </div>
</div>

EOM;
$t->render('single.phtml');
