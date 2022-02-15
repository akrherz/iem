<?php 
/*
 * Called back from facebook social app when new comment is made
 * http://stackoverflow.com/questions/5331165/fb-is-not-defined-problem
 * http://stackoverflow.com/questions/8594048/getting-notification-when-someone-comments-using-comments-plugin
 */
$admin_email = 'akrherz@iastate.edu';

$commentID = isset($_REQUEST['id_of_comment_object']) ? 
		$_REQUEST['id_of_comment_object']: die();
$page_href = $_REQUEST['url_of_page_comment_leaved_on'];
$message = "comment #{$commentID} was left on page {$page_href}";

mail($admin_email, "You have a new comment", $message);
