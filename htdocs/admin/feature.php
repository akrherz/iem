<?php
/* Web based feature publisher */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/facebook-platform/php/facebook.php");
include("$rootpath/include/facebook-platform/php/facebook_desktop.php");
$facebook = new Facebook($fb_feature_key, $fb_feature_secret);
$user_id = $facebook->require_login();

$story = isset($_REQUEST["story"]) ? $_REQUEST["story"] : null;
$title = isset($_REQUEST["title"]) ? $_REQUEST["title"] : null;
$caption = isset($_REQUEST["caption"]) ? $_REQUEST["caption"] : null;
$tags = isset($_REQUEST["tags"]) ? $_REQUEST["tags"] : null;
$voting = (isset($_REQUEST["voting"]) && $_REQUEST["voting"] == "yes") ?
          true : false;

$mesosite = iemdb("mesosite");
pg_prepare($mesosite, "INJECTOR", "INSERT into feature 
  (title, story, caption, voting, tags) VALUES 
  ($1   , $2   , $3   , $4     , $5   )");

if ($story != null && $title != null){
  pg_query($mesosite, "DELETE from feature WHERE date(valid) = 'TODAY'");
  pg_execute($mesosite, "INJECTOR", Array($title, $story, $caption,
             $voting, $tags) );
}

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
  $facebook->api_client->stream_publish($_REQUEST["story"],$attachment,
             $action_links,157789644737, $user_id);
}


include("$rootpath/include/header.php");
?>
<h3>IEM Feature Publisher</h3>
<form method="POST">

<p>Feature Title:
<br /><input type="text" name="title" size="80" />

<p>Enter Story:
<br /><textarea NAME='story' wrap="hard" ROWS="20" COLS="70"></textarea>

<p>Caption:
<br /><input type="text" name="caption" size="80" />

<p>Tags:
<br /><input type="text" name="tags" size="80" />

<p>Publish Facebook?
<br /><input type="checkbox" name="facebook" value="yes" />Yes

<p>Allow Voting:
<br /><input type="checkbox" name="voting" value="yes" checked="checked" />Yes

<p><input type="submit" value="Go!" />
</form>

<?php include("$rootpath/include/footer.php"); ?>
