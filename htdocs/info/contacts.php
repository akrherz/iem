<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Contacts";

$t->content = <<<EOM

<h3>IEM Contacts</h3>

<p>After the death of <a href="/onsite/news.phtml?id=1378">Dr Ray Arritt</a>, a
new project coordinator has yet to be named. Please address all questions to
daryl.</p>

<div class="alert alert-danger">
Please send daryl an email before calling him!  Daryl rapidly turns around emails
and can provide you web links to the resources you are looking for!
</div>

<h4>IEM Website Developer: daryl herzmann</h4>

<br>716 Farm House Ln
<br>Iowa State University
<br>Ames, IA 50011
<br><i>Email:</i> <a href="mailto:akrherz@iastate.edu">akrherz@iastate.edu</a>
<br><i>Phone:</i> 515.451.9249 (Please email before calling, please!)
<br /><i>Blue Sky</i>
<a href="https://bsky.app/profile/akrherz.bsky.social">akrherz.bsky.social</a> 

EOM;
$t->render('single.phtml');
