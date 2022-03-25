<?php
// Need session to track state
session_start();
/* Web based feature publisher */
require_once "../config/settings.inc.php";
require_once "../include/database.inc.php";
require_once "../include/myview.php";
require_once "../include/forms.php";
require_once "../include/Facebook/autoload.php";

$msgs = Array();

define("TOKEN_NAME", "iem_facebook_access_token");
$mesosite = iemdb("mesosite", TRUE, TRUE);
pg_prepare($mesosite, "DELETOR", "DELETE from feature WHERE ".
    "date(valid) = $1");
pg_prepare($mesosite, "INJECTOR", "INSERT into feature ".
    "(valid, title, story, caption, voting, tags, fbid, appurl, ".
    "javascripturl, mediasuffix, media_height, media_width) VALUES ".
    "($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)");
pg_prepare($mesosite, "UPDATOR", "UPDATE feature SET fbid = $1 WHERE ".
    "date(valid) = $2");
pg_prepare($mesosite, "GET_AT", "SELECT propvalue from properties WHERE ".
    "propname = $1");
pg_prepare($mesosite, "INSERT_AT", "INSERT into properties(propname, ".
    "propvalue) VALUES ($1, $2)");
pg_prepare($mesosite, "DELETE_AT", "DELETE from properties WHERE ".
    "propname = $1");

$fb = new \Facebook\Facebook([
  'app_id' => '148705700931',
  'app_secret' => $fb_feature_secret,
  'default_graph_version' => 'v5.0'
]);
$helper = $fb->getRedirectLoginHelper();
// https://developers.facebook.com/docs/permissions/reference/pages_manage_posts
$permissions = ['pages_manage_posts'];
$callback = 'https://mesonet.agron.iastate.edu/admin/feature.php';
$loginUrl = $helper->getLoginUrl($callback, $permissions);

// Do we have a token in the database?
$rs = pg_execute($mesosite, "GET_AT", Array(TOKEN_NAME));
if (pg_num_rows($rs) == 0) {
  $accessToken = null;
} else {
  $accessToken = pg_fetch_result($rs, 0, 0);
  $msgs[] = "Found access_token within the database.";
}

// If we have a token, try to use it
if ($accessToken) {
  try {
    $fb->setDefaultAccessToken($accessToken);
    $msgs[] = "Set access_token for facebook client.";
} catch (Exception $e) {
      $msgs[] = "Error: " . $e->getMessage();
  }
}

// If we got a response with a token to save, save it
try {
	$res = $helper->getAccessToken();
	if ($res){
        $accessToken = $res;
        $msgs[] = "Saving acccess_token to database.";
        pg_execute($mesosite, "INSERT_AT", Array(TOKEN_NAME, $accessToken));
        $fb->setDefaultAccessToken($accessToken);
    }
} catch(Facebook\Exceptions\FacebookSDKException $e) {
	// There was an error communicating with Graph
    $msgs[] = "Error: " . $e->getMessage();
}

$javascripturl = isset($_REQUEST["javascripturl"]) ? $_REQUEST["javascripturl"] : null;
$appurl = isset($_REQUEST["appurl"]) ? $_REQUEST["appurl"] : null;
$story = isset($_REQUEST["story"]) ? $_REQUEST["story"] : null;
$title = isset($_REQUEST["title"]) ? $_REQUEST["title"] : null;
$caption = isset($_REQUEST["caption"]) ? $_REQUEST["caption"] : null;
$tags = isset($_REQUEST["tags"]) ? $_REQUEST["tags"] : null;
$voting = (isset($_REQUEST["voting"]) && $_REQUEST["voting"] == "yes") ? 't' : 'f';
$mediasuffix = isset($_REQUEST["mediasuffix"]) ? $_REQUEST["mediasuffix"]: "png";
$media_height = get_int404("media_height", null);
$media_width = get_int404("media_width", null);

// Want appurl inserted as null if empty
if (empty($appurl)) $appurl = null;

$app = "";

if ($accessToken){
	try {
        $response = $fb->get('/me');
        $userNode = $response->getGraphUser();
        $app .= "Hello, ". $userNode->getName();
	} catch(Facebook\Exceptions\FacebookSDKException $e) {
        $msgs[] = "Error: " . $e->getMessage();
    }
} else {
	$app .= "<a href=\"$loginUrl\">Login</a>";
}

if (! is_null($story) && ! is_null($title)){
    $at_str = isset($_REQUEST["at_on"])? $_REQUEST["at"]: ""; 
    $publish_at = new DateTime($_REQUEST["at"], new DateTimeZone("America/Chicago"));

    $permalink = sprintf(
        "https://mesonet.agron.iastate.edu/onsite/features/cat.php?day=%s",
        $publish_at->format("Y-m-d")
    );
    $thumbnail = sprintf(
        "https://mesonet.agron.iastate.edu/onsite/features/%s.%s",
        $publish_at->format("Y/m/ymd"),
        $mediasuffix
    );
    // Here's the rub, Facebook wants to visit the permalink above to scrape content
    // So we need to get this info into the database before we tell facebook about it
    pg_execute($mesosite, "DELETOR", Array($publish_at->format('Y-m-d')));
    pg_execute(
        $mesosite,
        "INJECTOR",
        Array($publish_at->format("Y-m-d H:i:s"), $title, $story, $caption,
			$voting, $tags, null, $appurl, $javascripturl,
			$mediasuffix, $media_height, $media_width),
    );

    if ( isset($_REQUEST["facebook"]) && $_REQUEST["facebook"] == "yes"){

        // https://developers.facebook.com/docs/graph-api/reference/v2.12/page/feed#custom-image
        $data = [
            'link' => $permalink,
            'message' => $story,
            "scheduled_publish_time" => $publish_at->getTimestamp(),
            "published" => false,
        ];
        try{
            // Get a page access token to use
            $response = $fb->get('/157789644737?fields=access_token');
            $fbid = $response->getGraphNode();
            $response = $fb->post('/157789644737/feed', $data, $fbid["access_token"]);
            $fbid = $response->getGraphNode();
        } catch(Facebook\Exceptions\FacebookSDKException $e) {
            // There was an error communicating with Graph
            $msgs[] = "Error: " . $e->getMessage();
        }
        $story_fbid = explode("_", $fbid['id']);
        $story_fbid = $story_fbid[1];
        $msgs[] = sprintf("Facebook <a href=\"https://www.facebook.com/". 
            "permalink.php?story_fbid=%s&id=157789644737\">post created</a>.",
            $story_fbid);

        pg_execute($mesosite, "UPDATOR", Array($story_fbid, $publish_at->format('Y-m-d')));
    }

}

$t = new MyView();

// Default timestamp is 5:30 AM tomorrow
$dt = new DateTime();
$dt->setTime(5, 30);
$dt->modify('+1 day');
$at = $dt->format('Y-m-d\\TH:i:s');

$logmsgs = "<ul>";
foreach($msgs as $msg){
    $logmsgs .= sprintf("<li>%s</li>", $msg);
}

$logmsgs .= "</ul>";

$t->content = <<<EOF

{$app}

<ul class="breadcrumb">
<li><a href="/admin/">Admin Mainpage</a></li>
</ul>

{$logmsgs}

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

<p>For MP4, what is the width x height?
<br /><input type="text" name="media_width" size="8" /> x
<input type="text" name="media_height" size="8" /></p>

<p>Javascript URI:
<br /><input type="text" name="javascripturl" size="80" /></p>

<p>Publish Facebook?
<br /><input id="fb" type="checkbox" name="facebook" value="yes" />
<label for="fb">Yes</label></p>

<p>Allow Voting:
<br /><input type="checkbox" name="voting" value="yes" checked="checked" id="voting" />
<label for="voting">Yes</label></p>

<p><input type="checkbox" id="at_on" name="at_on">
<label for="at_on">Publish at Iowa Timestamp</label>:
<br /><input type="text" name="at" value="{$at}" /></p>

<p><input type="submit" value="Go!" /></p>
</form>
EOF;

$t->render('single.phtml');
