<?php
/* Web based feature publisher */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/facebook.php");

$facebook = new Facebook(Array(
  'appId' => '148705700931',
  'secret' => $fb_feature_secret,
  'cookie' => true,
));
$session = $facebook->getSession();
$me = null;
// Session based API call.
if ($session) {
  try {
    $uid = $facebook->getUser();
    $me = $facebook->api('/me');
  } catch (FacebookApiException $e) {
    error_log($e);
  } 
} 

$loginurl = $facebook->getLoginUrl();

$story = isset($_REQUEST["story"]) ? $_REQUEST["story"] : null;
$title = isset($_REQUEST["title"]) ? $_REQUEST["title"] : null;
$caption = isset($_REQUEST["caption"]) ? $_REQUEST["caption"] : null;
$tags = isset($_REQUEST["tags"]) ? $_REQUEST["tags"] : null;
$voting = (isset($_REQUEST["voting"]) && $_REQUEST["voting"] == "yes") ?
          true : false;

$mesosite = iemdb("mesosite");
pg_prepare($mesosite, "INJECTOR", "INSERT into feature 
  (title, story, caption, voting, tags, fbid) VALUES 
  ($1   , $2   , $3   , $4     , $5  , $6)");



$rooturl = "http://mesonet.agron.iastate.edu";
$permalink = sprintf('%s/onsite/features/cat.php?day=%s', $rooturl, date("Y-m-d") );
$thumbnail = sprintf('%s/onsite/features/%s_s.png', $rooturl, 
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
       "target_id" => null,
       "uid" => 157789644737));
  echo $fbid; print_r($fbid); die();
  $story_fbid = explode("_", $fbid);
  $story_fbid = str_replace('"', '', $story_fbid[1]);
}
if ($story != null && $title != null &&
    isset($_REQUEST['iemdb']) && $_REQUEST['iemdb'] == 'yes'){
  pg_query($mesosite, "DELETE from feature WHERE date(valid) = 'TODAY'");
  pg_execute($mesosite, "INJECTOR", Array($title, $story, $caption,
             $voting, $tags, $story_fbid) );
}

include("$rootpath/include/header.php");

if (! $me){
	?>
	<a href="<?php echo $loginurl; ?>">Login</a>
<?php
}
?>
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

<p>Publish Facebook?
<br /><input type="checkbox" name="facebook" value="yes" />Yes</p>

<p>Allow Voting:
<br /><input type="checkbox" name="voting" value="yes" checked="checked" />Yes</p>

<p>Publish to iemdb?:
<br /><input type="checkbox" name="iemdb" value="yes" checked="checked" />Yes</p>

<p><input type="submit" value="Go!" /></p>
</form>

<?php include("$rootpath/include/footer.php"); ?>
