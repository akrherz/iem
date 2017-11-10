<?php
require_once '../../config/settings.inc.php';
require_once '../../include/myview.php';

$t = new MyView();
$t->title = "File Not Found (404)";
$t->content = <<<EOF
<h3>Requested file was not found</h3>
<img src="/images/cow404.jpg" class="img img-responsive" alt="404 Cow" />
EOF;
$t->render('single.phtml');
$ref = isset($_SERVER["HTTP_REFERER"]) ? $_SERVER["HTTP_REFERER"] : 'none';

// Since we are now running with php-fpm, we don't have access to Apache's
// errorlog, so we now send to syslog, so that we get some denoted error logged
// of 404s
openlog("iem", LOG_PID | LOG_PERROR, LOG_LOCAL1);
syslog(LOG_WARNING, "404 ". $_SERVER["REQUEST_URI"] .
		' remote: '. $_SERVER["REMOTE_ADDR"] .
		' referer: '. $ref);
closelog();
?>