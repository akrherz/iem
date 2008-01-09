<?php

/**
 * Zend Framework
 *
 * LICENSE
 *
 * This source file is subject to the new BSD license that is bundled
 * with this package in the file LICENSE.txt.
 * It is also available through the world-wide-web at this URL:
 * http://framework.zend.com/license/new-bsd
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@zend.com so we can send you a copy immediately.
 *
 * @category   Zend
 * @package    Zend_Gdata
 * @copyright  Copyright (c) 2005-2007 Zend Technologies USA Inc. (http://www.zend.com)
 * @license    http://framework.zend.com/license/new-bsd     New BSD License
 */

/**
 * @see Zend_Gdata_Media
 */
require_once 'Zend/Gdata/Media.php';

/**
 * @see Zend_Gdata_YouTube_VideoEntry
 */
require_once 'Zend/Gdata/YouTube/VideoEntry.php';

/**
 * @see Zend_Gdata_YouTube_VideoFeed
 */
require_once 'Zend/Gdata/YouTube/VideoFeed.php';

/**
 * @see Zend_Gdata_YouTube_CommentFeed
 */
require_once 'Zend/Gdata/YouTube/CommentFeed.php';

/**
 * @see Zend_Gdata_YouTube_PlaylistListFeed
 */
require_once 'Zend/Gdata/YouTube/PlaylistListFeed.php';

/**
 * @see Zend_Gdata_YouTube_SubscriptionFeed
 */
require_once 'Zend/Gdata/YouTube/SubscriptionFeed.php';

/**
 * @see Zend_Gdata_YouTube_ContactFeed
 */
require_once 'Zend/Gdata/YouTube/ContactFeed.php';

/**
 * @see Zend_Gdata_YouTube_PlaylistVideoFeed
 */
require_once 'Zend/Gdata/YouTube/PlaylistVideoFeed.php';

/**
 * Service class for interacting with the services which use the media extensions
 * @link http://code.google.com/apis/gdata/calendar.html
 *
 * @category   Zend
 * @package    Zend_Gdata
 * @copyright  Copyright (c) 2005-2007 Zend Technologies USA Inc. (http://www.zend.com)
 * @license    http://framework.zend.com/license/new-bsd     New BSD License
 */
class Zend_Gdata_YouTube extends Zend_Gdata_Media
{

    const STANDARD_TOP_RATED_URI = 'http://gdata.youtube.com/feeds/standardfeeds/top_rated';
    const STANDARD_MOST_VIEWED_URI = 'http://gdata.youtube.com/feeds/standardfeeds/most_viewed';
    const STANDARD_RECENTLY_FEATURED_URI = 'http://gdata.youtube.com/feeds/standardfeeds/recently_featured';
    const STANDARD_WATCH_ON_MOBILE_URI = 'http://gdata.youtube.com/feeds/standardfeeds/watch_on_mobile';

    const VIDEO_URI = 'http://gdata.youtube.com/feeds/videos';
    const PLAYLIST_REL = 'http://gdata.youtube.com/schemas/2007#playlist';
    const USER_UPLOADS_REL = 'http://gdata.youtube.com/schemas/2007#user.uploads';
    const USER_PLAYLISTS_REL = 'http://gdata.youtube.com/schemas/2007#user.playlists';
    const USER_SUBSCRIPTIONS_REL = 'http://gdata.youtube.com/schemas/2007#user.subscriptions';
    const USER_CONTACTS_REL = 'http://gdata.youtube.com/schemas/2007#user.contacts';
    const USER_FAVORITES_REL = 'http://gdata.youtube.com/schemas/2007#user.favorites';
    const VIDEO_RESPONSES_REL = 'http://gdata.youtube.com/schemas/2007#video.responses';
    const VIDEO_RATINGS_REL = 'http://gdata.youtube.com/schemas/2007#video.ratings';
    const VIDEO_COMPLAINTS_REL = 'http://gdata.youtube.com/schemas/2007#video.complaints';

    const FAVORITES_URI_SUFFIX = 'favorites';
    const UPLAODS_URI_SUFFIX = 'uploads';
    const RESPONSES_URI_SUFFIX = 'responses';
    const RELATED_URI_SUFFIX = 'related';

    const AUTH_SERVICE_NAME = 'videoonline';

    public static $namespaces = array(
            'yt' => 'http://gdata.youtube.com/schemas/2007');

    /**
     * Create Zend_Gdata_YouTube object
     *
     * @param Zend_Http_Client $client (optional) The HTTP client to use when
     *          when communicating with the Google Apps servers.
     */
    public function __construct($client = null)
    {
        $this->registerPackage('Zend_Gdata_YouTube');
        $this->registerPackage('Zend_Gdata_YouTube_Extension');
        parent::__construct($client);
    }

    /**
     * Retrieves a feed of videos.
     *
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoFeed The feed of videos found at the 
     *         specified URL.
     */
    public function getVideoFeed($location = null)
    {
        if ($location == null) {
            $uri = self::VIDEO_URI;
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    /**
     * Retrieves a specific video entry.
     *
     * @param mixed $videoId The videoId of interest
     *         Zend_Gdata_Query object from which a URL can be determined
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoEntry The feed of videos found at the 
     *         specified URL.
     */
    public function getVideoEntry($videoId = null, $location = null)
    {
        if ($videoId !== null) {
            $uri = self::VIDEO_URI . "/" . $videoId;
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getEntry($uri, 'Zend_Gdata_YouTube_VideoEntry');
    }

    /**
     * Retrieves a feed of videos related to the specified video ID.
     *
     * @param string $videoId The videoId of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoFeed The feed of videos found at the 
     *         specified URL.
     */
    public function getRelatedVideoFeed($videoId = null, $location = null)
    {
        if ($videoId !== null) {
            $uri = self::VIDEO_URI . "/" . $videoId . "/" . self::RELATED_URI_SUFFIX;
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    /**
     * Retrieves a feed of video responses related to the specified video ID.
     *
     * @param string $videoId The videoId of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoFeed The feed of videos found at the 
     *         specified URL.
     */
    public function getVideoResponseFeed($videoId = null, $location = null)
    {
        if ($videoId !== null) {
            $uri = self::VIDEO_URI . "/" . $videoId . "/" . self::RESPONSES_URI_SUFFIX;
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    /**
     * Retrieves a feed of comments related to the specified video ID.
     *
     * @param string $videoId The videoId of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_CommentFeed The feed of videos found at the 
     *         specified URL.
     */
    public function getVideoCommentFeed($videoId = null, $location = null)
    {
        if ($videoId !== null) {
            $uri = self::VIDEO_URI . "/" . $videoId . "/comments";
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_CommentFeed');
    }

    /**
     * Retrieves a feed of comments related to the specified video ID.
     *
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_CommentFeed The feed of videos found at the 
     *         specified URL.
     */
    public function getTopRatedVideoFeed($location = null)
    {
        if ($location == null) {
            $uri = self::STANDARD_TOP_RATED_URI;
        } else if ($location instanceof Zend_Gdata_Query) {
            if ($location instanceof Zend_Gdata_YouTube_VideoQuery) {
                if (!isset($location->url)) {
                    $location->setFeedType('top rated');
                }
            }
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    
    /**
     * Retrieves a feed of the most viewed videos.
     *
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoFeed The feed of videos found at the 
     *         specified URL.
     */
    public function getMostViewedVideoFeed($location = null)
    {
        if ($location == null) {
            $uri = self::STANDARD_MOST_VIEWED_URI;
        } else if ($location instanceof Zend_Gdata_Query) {
            if ($location instanceof Zend_Gdata_YouTube_VideoQuery) {
                if (!isset($location->url)) {
                    $location->setFeedType('most viewed');
                }
            }
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    /**
     * Retrieves a feed of recently featured videos.
     *
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoFeed The feed of videos found at the 
     *         specified URL.
     */
    public function getRecentlyFeaturedVideoFeed($location = null)
    {
        if ($location == null) {
            $uri = self::STANDARD_RECENTLY_FEATURED_URI;
        } else if ($location instanceof Zend_Gdata_Query) {
            if ($location instanceof Zend_Gdata_YouTube_VideoQuery) {
                if (!isset($location->url)) {
                    $location->setFeedType('recently featured');
                }
            }
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    /**
     * Retrieves a feed of videos recently featured for mobile devices.
     * These videos will have RTSP links in the $entry->mediaGroup->content
     *
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoFeed The feed of videos found at the 
     *         specified URL.
     */
    public function getWatchOnMobileVideoFeed($location = null)
    {
        if ($location == null) {
            $uri = self::STANDARD_WATCH_ON_MOBILE_URI;
        } else if ($location instanceof Zend_Gdata_Query) {
            if ($location instanceof Zend_Gdata_YouTube_VideoQuery) {
                if (!isset($location->url)) {
                    $location->setFeedType('watch on mobile');
                }
            }
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    /**
     * Retrieves a feed which lists a user's playlist
     *
     * @param string $user (optional) The username of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_PlaylistListFeed The feed of playlists 
     */
    public function getPlaylistListFeed($user = null, $location = null)
    {
        if ($user !== null) {
            $uri = 'http://gdata.youtube.com/feeds/users/' . $user . '/playlists';
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_PlaylistListFeed');
    }

    /**
     * Retrieves a feed of videos in a particular playlist
     *
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_PlaylistVideoFeed The feed of videos found at
     *         the specified URL.
     */
    public function getPlaylistVideoFeed($location)
    {
        if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_PlaylistVideoFeed');
    }

    /**
     * Retrieves a feed of a user's subscriptions
     *
     * @param string $user (optional) The username of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_SubscriptionListFeed The feed of subscriptions 
     */
    public function getSubscriptionFeed($user = null, $location = null)
    {
        if ($user !== null) {
            $uri = 'http://gdata.youtube.com/feeds/users/' . $user . '/subscriptions';
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_SubscriptionFeed');
    }

    /**
     * Retrieves a feed of a user's contacts
     *
     * @param string $user (optional) The username of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_ContactFeed The feed of contacts 
     */
    public function getContactFeed($user = null, $location = null)
    {
        if ($user !== null) {
            $uri = 'http://gdata.youtube.com/feeds/users/' . $user . '/contacts';
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_ContactFeed');
    }

    /**
     * Retrieves a user's uploads
     *
     * @param string $user (optional) The username of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoFeed The videos uploaded by the user
     */
    public function getUserUploads($user = null, $location = null)
    {
        if ($user !== null) {
            $uri = 'http://gdata.youtube.com/feeds/users/' . $user . '/' .
                   self::UPLOADS_URI_SUFFIX;
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    /**
     * Retrieves a user's favorites
     *
     * @param string $user (optional) The username of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_VideoFeed The videos favorited by the user
     */
    public function getUserFavorites($user = null, $location = null)
    {
        if ($user !== null) {
            $uri = 'http://gdata.youtube.com/feeds/users/' . $user . '/' .
                   self::FAVORITES_URI_SUFFIX;
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getFeed($uri, 'Zend_Gdata_YouTube_VideoFeed');
    }

    /**
     * Retrieves a user's profile as an entry 
     *
     * @param string $user (optional) The username of interest
     * @param mixed $location (optional) The URL to query or a
     *         Zend_Gdata_Query object from which a URL can be determined
     * @return Zend_Gdata_YouTube_UserProfileEntry The user profile entry
     */
    public function getUserProfile($user = null, $location = null)
    {
        if ($user !== null) {
            $uri = 'http://gdata.youtube.com/feeds/users/' . $user;
        } else if ($location instanceof Zend_Gdata_Query) {
            $uri = $location->getQueryUrl();
        } else {
            $uri = $location;
        }
        return parent::getEntry($uri, 'Zend_Gdata_YouTube_UserProfileEntry');
    }

}
