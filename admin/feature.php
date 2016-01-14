<?php
session_start();
/* Web based feature publisher */
include("../config/settings.inc.php");
include_once "../include/myview.php";
$t = new MyView();

include("../include/database.inc.php");
include("../include/facebook.php");

$facebook = new Facebook(Array(
  'appId' => '148705700931',
  'secret' => $fb_feature_secret,
  'cookie' => true,
));
$me = null;
$uid = $facebook->getUser();
if ($uid){    
	$me = $facebook->api('/me');
}
if ($me){
  $logouturl = $facebook->getLogoutUrl();
}else {
  $loginurl = $facebook->getLoginUrl(Array(
    'scope' => 'publish_actions',
  		'redirect_uri' => 'https://mesonet.agron.iastate.edu/admin/feature.php'
  ));
}

$javascripturl = isset($_REQUEST["javascripturl"]) ? $_REQUEST["javascripturl"] : null;
$appurl = isset($_REQUEST["appurl"]) ? $_REQUEST["appurl"] : null;
$story = isset($_REQUEST["story"]) ? $_REQUEST["story"] : null;
$title = isset($_REQUEST["title"]) ? $_REQUEST["title"] : null;
$caption = isset($_REQUEST["caption"]) ? $_REQUEST["caption"] : null;
$tags = isset($_REQUEST["tags"]) ? $_REQUEST["tags"] : null;
$voting = (isset($_REQUEST["voting"]) && $_REQUEST["voting"] == "yes") ?
          true : false;

$mesosite = iemdb("mesosite", TRUE, TRUE);
pg_prepare($mesosite, "INJECTOR", "INSERT into feature ".
  "(title, story, caption, voting, tags, fbid, appurl, javascripturl) VALUES ".
  "($1, $2, $3, $4, $5, $6, $7, $8)");



$rooturl = "http://mesonet.agron.iastate.edu";
$permalink = sprintf('%s/onsite/features/cat.php?day=%s', $rooturl, date("Y-m-d") );
$thumbnail = sprintf('%s/onsite/features/%s.png', $rooturl, 
             date("Y/m/ymd") );

$attachment = Array(
 'name' => 'IEM Feature',
 'href' => $permalink,
 'caption' => 'caption',
 'description' => 'Feature Image',
 'media' => array(array('type' => 'image',
    'src' => $thumbnail,
    'href' => $permalink)),
);
$action_links = array(
  array('text' => 'Permalink',
        'href' => $permalink));

if ( isset($_REQUEST["facebook"]) && $_REQUEST["facebook"] == "yes"){
  $fbid = $facebook->api(Array("method"=>'stream.publish', 
       "message" => $_REQUEST["story"],
       "attachment" => $attachment,
       "action_links" => $action_links,
    //   "target_id" => null,
       "uid" => 157789644737));
  $story_fbid = explode("_", $fbid);
  $story_fbid = str_replace('"', '', $story_fbid[1]);
}
if ($story != null && $title != null &&
    isset($_REQUEST['iemdb']) && $_REQUEST['iemdb'] == 'yes'){
  pg_query($mesosite, "DELETE from feature WHERE date(valid) = 'TODAY'");
  pg_execute($mesosite, "INJECTOR", Array($title, $story, $caption,
             $voting, $tags, $story_fbid, $appurl, $javascripturl) );
}

$app = "";
if ($me){ 
	$app .= "Hello, ". $me["name"] ."!<a href=\"$logouturl\">Logout</a>";
} else {
	$app .= "<a href=\"$loginurl\">Login</a>";
}
$t->content = <<<EOF

{$app}

<ul class="breadcrumb">
<li><a href="/admin/">Admin Mainpage</a></li>
</ul>
		
<h3>IEM Feature Publisher</h3>
<form method="POST">

<p>Feature Title:
<br /><input type="text" name="title" size="80" /></p>

<p>Enter Story:
<br /><textarea NAME='story' wrap="hard" ROWS="20" COLS="70"></textarea></p>

<p>Caption:
<br /><input type="text" name="caption" size="80" /></p>

<p>Tags:
<br /><input type="text" name="tags" size="80" /></p>

<p>AppURL:
<br /><input type="text" name="appurl" size="80" /></p>

<p>Javascript URI:
<br /><input type="text" name="javascripturl" size="80" /></p>

<p>Publish Facebook?
<br /><input type="checkbox" name="facebook" value="yes" />Yes</p>

<p>Allow Voting:
<br /><input type="checkbox" name="voting" value="yes" checked="checked" />Yes</p>

<p>Publish to iemdb?:
<br /><input type="checkbox" name="iemdb" value="yes" checked="checked" />Yes</p>

<p><input type="submit" value="Go!" /></p>
</form>
EOF;
$t->render('single.phtml');
?>
