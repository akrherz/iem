<?php
/*
 * Called back from facebook social app when new comment is made
 * http://stackoverflow.com/questions/5331165/fb-is-not-defined-problem
 * http://stackoverflow.com/questions/8594048/getting-notification-when-someone-comments-using-comments-plugin
 */
$admin_email = 'akrherz@iastate.edu';
require_once "../include/forms.php";
require_once "../include/database.inc.php";

$commentID = isset($_REQUEST['id_of_comment_object']) ?
    xssafe($_REQUEST['id_of_comment_object']) : die();
$page_href = $_REQUEST['url_of_page_comment_leaved_on'];
$message = "comment #{$commentID} was left on page {$page_href}";

mail($admin_email, "You have a new comment", $message);

// Log
$pgconn = iemdb("mesosite");
$rs = pg_prepare(
    $pgconn,
    "INSERT",
    "INSERT into weblog(client_addr, uri, referer, http_status) " .
        "VALUES ($1, $2, $3, $4)"
);
for ($i = 0; $i < 10; $i++) {
    pg_execute(
        $pgconn,
        "INSERT",
        array(
            $_SERVER["REMOTE_ADDR"],
            "/fbcomments.php",
            $_SERVER["HTTP_REFERER"],
            404
        )
    );
}
pg_close($pgconn);
