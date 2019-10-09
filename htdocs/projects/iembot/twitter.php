<?php 
session_start();
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 102);
include_once "../../../include/myview.php";
require_once "../../../include/twitteroauth/twitteroauth.php";
require_once "../../../include/iemprop.php";
require_once "../../../include/forms.php";

define("TWITTER_KEY", get_iemprop('bot.twitter.consumerkey'));
define("TWITTER_SECRET", get_iemprop('bot.twitter.consumersecret'));

$pgconn = pg_connect('host=iemdb-mesosite.local user=ldm dbname=mesosite');
$user_id = isset($_SESSION["user_id"]) ? $_SESSION["user_id"]: '';
$screen_name = isset($_SESSION["screen_name"]) ? $_SESSION["screen_name"]: '';
$channel = isset($_REQUEST["channel"]) ? strtoupper(xssafe($_REQUEST["channel"])) : '';
$channel = trim($channel);

$rs = pg_prepare($pgconn, "SAVEAUTH", "INSERT into ".
  "iembot_twitter_oauth ".
  "(user_id, screen_name, access_token, access_token_secret) ".
  "VALUES ($1,$2,$3,$4)");
$rs = pg_prepare($pgconn, "UPDATEAUTH", "UPDATE iembot_twitter_oauth ".
  "SET access_token = $1, access_token_secret = $2, updated = now() ".
  "WHERE user_id = $3 RETURNING screen_name");
$rs = pg_prepare($pgconn, "SELECTSUBS", "SELECT * from ".
  "iembot_twitter_subs  WHERE user_id = $1 ORDER by channel ASC");
$rs = pg_prepare($pgconn, "ADDSUB", "INSERT into ".
  "iembot_twitter_subs(user_id, screen_name, channel) VALUES ($1, $2, $3)");
$rs = pg_prepare($pgconn, "DELSUB", "DELETE from ".
  "iembot_twitter_subs WHERE user_id = $1 and channel = $2");

function reloadbot(){
	return file_get_contents("http://iembot:9003/reload");
}

$msg = Array();
//------------------------------------------------------------
if (isset($_REQUEST['add']) && $channel != '' && $screen_name != ''){
	pg_execute($pgconn, 'ADDSUB', Array($_SESSION["user_id"],
		strtolower($_SESSION["screen_name"]), $channel));
	reloadbot();
	$msg[] = sprintf("Added channel subscription %s for user %s, reloaded bot",
			$channel, $_SESSION["screen_name"]);
}
if (isset($_REQUEST['del']) && $channel != '' && $screen_name != ''){
	pg_execute($pgconn, 'DELSUB', Array(strtolower($_SESSION["user_id"]),
			$channel));
	reloadbot();
	$msg[] = sprintf("Deleted channel subscription %s for user %s, reloaded bot",
			$channel, $_SESSION["screen_name"]);
}
if (isset($_REQUEST['cb'])){
	$to = new TwitterOAuth(TWITTER_KEY, TWITTER_SECRET,
						   $_SESSION['token'], $_SESSION['token_secret']);
	$tok = $to->getAccessToken($_REQUEST['oauth_verifier']);
	unset($_SESSION['token']);
	unset($_SESSION['token_secret']);
	$user_id = $tok['user_id'];
	$screen_name = $tok['screen_name'];
	$access_token 	= $tok['oauth_token'];
	$access_token_secret = $tok['oauth_token_secret'];
	if ($screen_name != ''){
		$_SESSION['user_id'] = $user_id;
		$_SESSION['screen_name'] = $screen_name;
		$rs = pg_execute($pgconn, "UPDATEAUTH",
			Array($access_token, $access_token_secret, $user_id));
		if (pg_num_rows($rs) == 0) {
			pg_execute($pgconn, "SAVEAUTH", Array($user_id, strtolower($screen_name),
				$access_token, $access_token_secret));
		}
		reloadbot();
	}
	$msg[] = sprintf("Saved authorization for user %s", $screen_name);
}
if ($screen_name == ''){
	$connection = new TwitterOAuth(TWITTER_KEY, TWITTER_SECRET);
	$request_token = $connection->getRequestToken("https://mesonet.agron.iastate.edu/projects/iembot/twitter.php?cb");
	$_SESSION['token'] = $token = $request_token['oauth_token'];
	$_SESSION['token_secret'] = $request_token['oauth_token_secret'];
	$authenticateUrl = $connection->getAuthorizeURL($token);
	header("Location: $authenticateUrl");
	exit;
}

$sselect2 = "";
$rs = pg_execute($pgconn, "SELECTSUBS", Array($user_id));
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
	$sselect2 .= sprintf('<tr><th>%s</th><td>%s</td>
    	<td><a href="?del&amp;channel=%s">Unsubscribe</a></tr>',
				$screen_name, $row['channel'],
				 $row['channel']);
}

$msghtml = "";
while (list($key, $val)=each($msg)){
	$msghtml .= "<div class='alert alert-info'>". $val ."</div>";
}

$t = new MyView();
$t->title = "IEMBot Twitter Configuration Page";

$t->content = <<<EOL

<ol class="breadcrumb">
 <li><a href="/projects/iembot/">IEMBot Homepage</a></li>
 <li class="active">Twitter Configuration Page</li>
</ol>

{$msghtml}

<h3>IEMBOT + Twitter Integration</h3>
		
<p>This page allows for the subscription of a Twitter Account to one or more
"IEMBot channels".  The automated processing of National Weather Service text
products converts each product into a tweet sized message and is associated
with one or more channels.  These channels are then used to route the messages
to subscribed twitter pages.</p>

<div class="alert alert-warning">This service is provided as-is and without
warranty.  <strong>The service could fail</strong> with an EF-5 tornado approaching your
city, so you have been warned!</div>

<h4>Add Channel Subscription</h4>
 <form method="POST" action="twitter.php">
 <input type="hidden" name="add" value="yes"/>
 <table class="table">
 <tr><td>Page</td><td>Channel</td></tr>
 <tr><th>{$screen_name}</th>
  <td><input type="text" name="channel" /></tr>
 </table>
 <input type="submit" name="Subscribe Channel" />
 </form>

<h4>Current Subscriptions</h4>
 <table class="table table-striped">
 <thead><tr><th>Page</th><th>Channel</th><th></th></tr></thead>
{$sselect2}
 </table>
 		

EOL;

$t->render('single.phtml');
?>
