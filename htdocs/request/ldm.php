<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "LDM Request HOWTO";

$t->content = <<<EOF
<ol class="breadcrumb">
  <li><a href="/info.php">IEM Information</a></li>
  <li class="active">Real-time IEM data feeds with LDM HOWTO</li>
</ol>

<p>The IEM uses <a href="https://www.unidata.ucar.edu">Unidata LDM</a> to move
data around within the computing infrastructure.  Anybody is eligable to request
a LDM feed, so to get products pushed to you without any fuss!  This page details
the setup of the LDM feed.</p>

<h4>STEP 1: Send an Email</h4>
<p>
Send us an email requesting a LDM feed.  You can send this email to me, Daryl
Herzmann (akrherz@iastate.edu) . You should include contact information
and the DNS/IP of the host that you will be using to connect to the IEM LDM. 
</p>

<h4>STEP 2: Configure LDM (ldmd.conf)</h4>
<p>
All local products are generated within the <code>EXP</code> LDM feedtype. A
nomenclature is used within the IEM to help with product routing.  The general
form is: <code>datatype routes timestamp archive_path current_path suffix</code>
</p>


<p><b>STEP 3: Sign up for IEM bulletin (optional)</b>
<br>You don't have to complete this step, but you can keep up-to-date with
IEM news and events with the IEM Daily Bulletin.  You can sign up for it
<a href="https://mailchi.mp/25e185228da8/iem-daily-bulletin">here</a>.
 If this service generates enough interest, I will set up a dedicated 
email
list for it.

<p>
Daryl Herzmann 
<br> (akrherz@iastate.edu)
<br> Rev: 26 Dec 2002

EOF;
$t->render('single.phtml');
