<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Contacts";

$t->content = <<<EOM

<h3>IEM Contacts</h3>

<p><div class="alert alert-info">We are very responsive to emails!  Please
 consider emailing us before calling!</div>

<div class="row">
<div class="col-md-5 well">
<h3>For Data &amp; Technical Issues:</h3>

<h4>IEM Systems Analyst: Daryl Herzmann</h4>

<br>716 Farm House Ln
<br>Iowa State University
<br>Ames, IA 50011
<br><i>Email:</i> <a href="mailto:akrherz@iastate.edu">akrherz@iastate.edu</a>
<br><i>Office Phone:</i> 515.294.5978
<br /><i>Jabber:</i> akrherz@jabber.org
<br /><i>Google Talk</i> akrherz@gmail.com
<br /><i>Twitter</i> <a href="https://twitter.com/akrherz">@akrherz</a> 

<p>If all those fail you, try <i>Daryl's Cell Phone!</i> 515.639.0164

</div>
<div class="col-md-2">&nbsp;</div>
<div class="col-md-5 well">

After the death of <a href="/onsite/news.phtml?id=1378">Dr Ray Arritt</a>, a
new project coordinator has yet to be named.  Please address all questions to
daryl.

<!--
<h3>For Administrative Questions:</h3>

<h4>IEM Coordinator: Dr Raymond Arritt</h4>
		
<br>716 Farm House Ln
<br>Iowa State University
<br>Ames, IA 50011
<br><i>Email:</i> <a href="mailto:rwarritt&#064;bruce&#046;agron&#046;iastate&#046;edu">rwarritt&#064;bruce&#046;agron&#046;iastate&#046;edu</a>
-->

</div>
</div>

<a href="http://www.nsf.gov"><img src="/images/nsf.gif" border="0"></a>
<br clear="all" />This website is based upon work supported by grants from the National Science
Foundation. Opinions, findings, and conclusions or recommendations
expressed in this material are those of the author(s) and do not necessarily
reflect the views of the National Science Foundation.

EOM;
$t->render('single.phtml');
?>