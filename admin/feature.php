<?php
session_start();
/* Web based feature publisher */
require_once "../config/settings.inc.php";
require_once "../include/database.inc.php";
require_once "../include/myview.php";
require_once "../include/Facebook/autoload.php";

$t = new MyView();

$fb = new \Facebook\Facebook([
  'app_id' => '148705700931',
  'app_secret' => $fb_feature_secret,
  'default_graph_version' => 'v5.0'
]);
$helper = $fb->getRedirectLoginHelper();
$permissions = ['publish_pages'];
$callback = 'https://mesonet.agron.iastate.edu/admin/feature.php';
$loginUrl = $helper->getLoginUrl($callback, $permissions);
$logoutUrl = $helper->getLogoutUrl($callback, $permissions);

try {
	$accessToken = $helper->getAccessToken();
	if ($accessToken) $_SESSION['facebook_access_token'] = (string) $accessToken;
} catch(Facebook\Exceptions\FacebookSDKException $e) {
	// There was an error communicating with Graph
	echo $e->getMessage();
	exit;
}
if (isset($_SESSION['facebook_access_token'])) {
	$accessToken = $_SESSION['facebook_access_token'];
	$fb->setDefaultAccessToken($accessToken);
}

$javascripturl = isset($_REQUEST["javascripturl"]) ? $_REQUEST["javascripturl"] : null;
$appurl = isset($_REQUEST["appurl"]) ? $_REQUEST["appurl"] : null;
$story = isset($_REQUEST["story"]) ? $_REQUEST["story"] : null;
$title = isset($_REQUEST["title"]) ? $_REQUEST["title"] : null;
$caption = isset($_REQUEST["caption"]) ? $_REQUEST["caption"] : null;
$tags = isset($_REQUEST["tags"]) ? $_REQUEST["tags"] : null;
$voting = (isset($_REQUEST["voting"]) && $_REQUEST["voting"] == "yes") ? 't' : 'f';
$mediasuffix = isset($_REQUEST["mediasuffix"]) ? $_REQUEST["mediasuffix"]: "png";

$mesosite = iemdb("mesosite", TRUE, TRUE);
pg_prepare($mesosite, "INJECTOR", "INSERT into feature ".
  "(title, story, caption, voting, tags, fbid, appurl, javascripturl, ".
  "mediasuffix) VALUES ".
  "($1, $2, $3, $4, $5, $6, $7, $8, $9)");

$app = "";
if ($accessToken){
	$response = $fb->get('/me');
	$userNode = $response->getGraphUser();
	$app .= "Hello, ". $userNode->getName() ."!<a href=\"$logoutUrl\">Logout</a>";
} else {
	$app .= "<a href=\"$loginUrl\">Login</a>";
}

$rooturl = "https://mesonet.agron.iastate.edu";
$permalink = sprintf('%s/onsite/features/cat.php?day=%s', $rooturl, date("Y-m-d") );
$thumbnail = sprintf('%s/onsite/features/%s.%s', $rooturl, 
             date("Y/m/ymd"), $mediasuffix);

// Here's the rub, Facebook wants to visit the permalink above to scrape content
// So we need to get this info into the database before we tell facebook about it
if ($story != null && $title != null &&
    isset($_REQUEST['iemdb']) && $_REQUEST['iemdb'] == 'yes'){
  pg_query($mesosite, "DELETE from feature WHERE date(valid) = 'TODAY'");
  pg_execute($mesosite, "INJECTOR", Array($title, $story, $caption,
			 $voting, $tags, null, $appurl, $javascripturl,
			 $mediasuffix) );
}

if ( isset($_REQUEST["facebook"]) && $_REQUEST["facebook"] == "yes"){

    // https://developers.facebook.com/docs/graph-api/reference/v2.12/page/feed#custom-image
	$data = [
		'link' => $permalink,
		'message' => $story,
	];
	try{
		// Get a page access token to use
		$response = $fb->get('/157789644737?fields=access_token');
        $fbid = $response->getGraphNode();
		$response = $fb->post('/157789644737/feed', $data, $fbid["access_token"]);
		$fbid = $response->getGraphNode();
	} catch(Facebook\Exceptions\FacebookSDKException $e) {
		// There was an error communicating with Graph
		echo $e->getMessage();
		exit;
	}
	$story_fbid = explode("_", $fbid['id']);
      $story_fbid = $story_fbid[1];
    $app .= sprintf("<br />Facebook <a href=\"https://www.facebook.com/". 
        "permalink.php?story_fbid=%s&id=157789644737\">post created</a>.",
        $story_fbid);
}
if ($story != null && $title != null &&
    isset($_REQUEST['iemdb']) && $_REQUEST['iemdb'] == 'yes'){
  pg_query($mesosite, "DELETE from feature WHERE date(valid) = 'TODAY'");
  pg_execute($mesosite, "INJECTOR", Array($title, $story, $caption,
			 $voting, $tags, $story_fbid, $appurl, $javascripturl,
			 $mediasuffix) );
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

<p>Media Suffix:
<br /><input type="text" name="mediasuffix" size="8" value="png" /></p>

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
