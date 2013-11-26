<?php 
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "API Access";

$t->content = <<< EOF

<h3>IEM API</h3>
		
		<p>This is a lame and initial attempt at producing a usable API.</p>
		
<pre>
	/api/sql/database/dbname?sql=SELECT day from current WHERE
</pre>

EOF;

$t->render('single.phtml');

?>