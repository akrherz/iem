<?php 
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "Contacts";

$t->content = <<<EOM

<div class="row">
<div class="col-md-6">

<h3>IEM Contacts</h3>

<p><div class="alert alert-info">We are very responsive to emails!  Please
 consider emailing us before calling!</div>
		
<p><h3>IEM Coordinator:</h3><br>
		
<p>Dr Raymond Arritt
<br>3010 Agronomy Hall
<br>Iowa State University
<br>Ames, IA 50011
<br><i>Email:</i> <a href="mailto:rwarritt&#064;bruce&#046;agron&#046;iastate&#046;edu">rwarritt&#064;bruce&#046;agron&#046;iastate&#046;edu</a>

<h3>IEM Systems Analyst:</h3><br>
		
<p>Daryl Herzmann
<br>3010 Agronomy Hall
<br>Iowa State University
<br>Ames, IA 50011
<br><i>Email:</i> <a href="mailto:akrherz@iastate.edu">akrherz@iastate.edu</a>
<br><i>Office Phone:</i> 515.294.5978
<br /><i>Jabber:</i> akrherz@jabber.org
<br /><i>Google Talk</i> akrherz@gmail.com
<br /><i>Twitter</i> <a href="https://twitter.com/akrherz">@akrherz</a> 

<p>If all those fail you, try <i>Daryl's Cell Phone!</i> 515.451.9249

</div>
<div class="col-md-6">

<a href="http://www.nsf.gov"><img src="/images/nsf.gif" border="0"></a>
<br clear="all" />This website is based upon work supported by grants from the National Science
Foundation. Opinions, findings, and conclusions or recommendations
expressed in this material are those of the author(s) and do not necessarily
reflect the views of the National Science Foundation.

</div></div>

EOM;
$t->render('single.phtml');
?>