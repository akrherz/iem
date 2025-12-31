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

<h3>Looking for low latency ASOS data? Read this first!</h3>

<p>The IEM LDM feed offers no magic in this space and you are not going to get
live ASOS data via this feed.  You likely want to read this news item about
<a href="https://mesonet.agron.iastate.edu/onsite/news.phtml?id=1469">Wagering
on ASOS temperatures</a> before contacting daryl about your "research" needs
for this data via LDM.</p>

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
