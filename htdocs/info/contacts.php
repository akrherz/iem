<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Contacts";

$t->content = <<<EOM

<h3>IEM Contacts</h3>

<p>After the death of <a href="/onsite/news.phtml?id=1378">Dr Ray Arritt</a>, a
new project coordinator has yet to be named.  Please address all questions to
daryl.</p>


<div class="alert alert-danger">
Please send daryl an email before calling him!  Daryl rapidly turns around emails
and can provide you web links to the resources you are looking for!
</div>

<h4>IEM Systems Analyst: daryl herzmann</h4>

<br>716 Farm House Ln
<br>Iowa State University
<br>Ames, IA 50011
<br><i>Email:</i> <a href="mailto:akrherz@iastate.edu">akrherz@iastate.edu</a>
<br><i>Phone:</i> 515.451.9249 (Please email before calling, please!)
<br /><i>Twitter</i> <a href="https://twitter.com/akrherz">@akrherz</a> 

<hr>

<p><a href="http://www.nsf.gov"><img src="/images/nsf.gif" border="0"></a>
<br clear="all" />This website is based upon work supported by grants from the National Science
Foundation. Opinions, findings, and conclusions or recommendations
expressed in this material are those of the author(s) and do not necessarily
reflect the views of the National Science Foundation.</p>

EOM;
$t->render('single.phtml');
