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
 * @see Zend_Gdata_Extension_Comments
 */
require_once 'Zend/Gdata/Extension/Comments.php';

/**
 * @see Zend_Gdata_Extension_FeedLink
 */
require_once 'Zend/Gdata/Extension/FeedLink.php';

/**
 * @see Zend_Gdata_YouTube_MediaEntry
 */
require_once 'Zend/Gdata/YouTube/MediaEntry.php';

/**
 * @see Zend_Gdata_YouTube_Extension_NoEmbed
 */
require_once 'Zend/Gdata/YouTube/Extension/NoEmbed.php';

/**
 * @see Zend_Gdata_YouTube_Extension_Statistics
 */
require_once 'Zend/Gdata/YouTube/Extension/Statistics.php';

/**
 * @see Zend_Gdata_YouTube_Extension_Racy
 */
require_once 'Zend/Gdata/YouTube/Extension/Racy.php';

/**
 * @see Zend_Gdata_Extension_Rating
 */
require_once 'Zend/Gdata/Extension/Rating.php';

/**
 * Represents the YouTube video flavor of an Atom entry
 *
 * @category   Zend
 * @package    Zend_Gdata
 * @copyright  Copyright (c) 2005-2007 Zend Technologies USA Inc. (http://www.zend.com)
 * @license    http://framework.zend.com/license/new-bsd     New BSD License
 */
class Zend_Gdata_YouTube_VideoEntry extends Zend_Gdata_YouTube_MediaEntry
{

    protected $_entryClassName = 'Zend_Gdata_YouTube_VideoEntry';

    /**
     * If null, the video can be embedded
     *
     * @var Zend_Gdata_YouTube_Extension_NoEmbed
     */
    protected $_noEmbed = null;

    /**
     * Specifies the statistics relating to the video.
     *
     * @var Zend_Gdata_YouTube_Extension_Statistics
     */
    protected $_statistics = null;

    /**
     * If not null, specifies that the video has racy content. 
     *
     * @var Zend_Gdata_YouTube_Extension_Racy
     */
    protected $_racy = null;

    /**
     * Specifies the video's rating.
     *
     * @var Zend_Gdata_Extension_Rating
     */
    protected $_rating = null;

    /**
     * Specifies the comments associated with a video.
     *
     * @var Zend_Gdata_Extensions_Comments
     */
    protected $_comments = null;

    /**
     * Nested feed links
     *
     * @var array
     */
    protected $_feedLink = array();

    /**
     * Creates a Video entry, representing an individual video
     *
     * @param DOMElement $element (optional) DOMElement from which this
     *          object should be constructed.
     */
    public function __construct($element = null)
    {
        foreach (Zend_Gdata_YouTube::$namespaces as $nsPrefix => $nsUri) {
            $this->registerNamespace($nsPrefix, $nsUri); 
        }
        parent::__construct($element);
    }

    /**
     * Retrieves a DOMElement which corresponds to this element and all 
     * child properties.  This is used to build an entry back into a DOM
     * and eventually XML text for sending to the server upon updates, or
     * for application storage/persistence.   
     *
     * @param DOMDocument $doc The DOMDocument used to construct DOMElements
     * @return DOMElement The DOMElement representing this element and all 
     * child properties. 
     */
    public function getDOM($doc = null)
    {
        $element = parent::getDOM($doc);
        if ($this->_noEmbed != null) {
            $element->appendChild($this->_noEmbed->getDOM($element->ownerDocument));
        }
        if ($this->_statistics != null) {
            $element->appendChild($this->_statistics->getDOM($element->ownerDocument));
        }
        if ($this->_racy != null) {
            $element->appendChild($this->_racy->getDOM($element->ownerDocument));
        }
        if ($this->_rating != null) {
            $element->appendChild($this->_rating->getDOM($element->ownerDocument));
        }
        if ($this->_comments != null) {
            $element->appendChild($this->_comments->getDOM($element->ownerDocument));
        }
        if ($this->_feedLink != null) {
            foreach ($this->_feedLink as $feedLink) {
                $element->appendChild($feedLink->getDOM($element->ownerDocument));
            }
        }
        return $element;
    }

    /**
     * Creates individual Entry objects of the appropriate type and
     * stores them in the $_entry array based upon DOM data.
     *
     * @param DOMNode $child The DOMNode to process
     */
    protected function takeChildFromDOM($child)
    {
        $absoluteNodeName = $child->namespaceURI . ':' . $child->localName;
        switch ($absoluteNodeName) {
        case $this->lookupNamespace('yt') . ':' . 'statistics':
            $statistics = new Zend_Gdata_YouTube_Extension_Statistics();
            $statistics->transferFromDOM($child);
            $this->_statistics = $statistics;
            break;
        case $this->lookupNamespace('yt') . ':' . 'racy':
            $racy = new Zend_Gdata_YouTube_Extension_Racy();
            $racy->transferFromDOM($child);
            $this->_racy = $racy;
            break;
        case $this->lookupNamespace('gd') . ':' . 'rating':
            $rating = new Zend_Gdata_Extension_Rating();
            $rating->transferFromDOM($child);
            $this->_rating = $rating;
            break;
        case $this->lookupNamespace('gd') . ':' . 'comments':
            $comments = new Zend_Gdata_Extension_Comments();
            $comments->transferFromDOM($child);
            $this->_comments = $comments;
            break;
        case $this->lookupNamespace('yt') . ':' . 'noembed':
            $noEmbed = new Zend_Gdata_YouTube_Extension_NoEmbed();
            $noEmbed->transferFromDOM($child);
            $this->_noEmbed = $noEmbed;
            break;
        case $this->lookupNamespace('gd') . ':' . 'feedLink':
            $feedLink = new Zend_Gdata_Extension_FeedLink();
            $feedLink->transferFromDOM($child);
            $this->_feedLink[] = $feedLink;
            break;
        default:
            parent::takeChildFromDOM($child);
            break;
        }
    }

    /**
     * Sets when the video was recorded.
     *
     * @param Zend_Gdata_YouTube_Extension_RecordingDate $recordingDate When the video was recorded
     * @return Zend_Gdata_YouTube_VideoEntry Provides a fluent interface
     */ 
    public function setRecordingDate($recordingDate = null) 
    {
        $this->_recordingDate = $recordingDate;
        return $this;
    } 

    /**
     * If an instance of Zend_Gdata_YouTube_Extension_NoEmbed is passed in, 
     * the video cannot be embedded.  Otherwise, if null is passsed in, the
     * video is able to be embedded
     * TODO: Make it easier to get/set this data
     *
     * @param Zend_Gdata_YouTube_Extension_NoEmbed $noEmbed Whether or not the video can be embedded 
     * @return Zend_Gdata_YouTube_VideoEntry Provides a fluent interface
     */ 
    public function setNoEmbed($noEmbed = null) 
    {
        $this->_noEmbed = $noEmbed;
        return $this;
    } 

    /**
     * If the return value is an instance of 
     * Zend_Gdata_YouTube_Extension_NoEmbed, this video cannot be embedded.
     * TODO: Make it easier to get/set this data
     *
     * @return Zend_Gdata_YouTube_Extension_NoEmbed Whether or not the video can be embedded 
     */
    public function getNoEmbed()
    {
        return $this->_noEmbed;
    }

    /**
     * Sets the statistics relating to the video.
     *
     * @param Zend_Gdata_YouTube_Extension_Statistics $statistics The statistics relating to the video
     * @return Zend_Gdata_YouTube_VideoEntry Provides a fluent interface
     */ 
    public function setStatistics($statistics = null) 
    {
        $this->_statistics = $statistics;
        return $this;
    } 

    /**
     * Returns the statistics relating to the video.
     *
     * @return Zend_Gdata_YouTube_Extension_Statistics  The statistics relating to the video 
     */
    public function getStatistics()
    {
        return $this->_statistics;
    }

    /**
     * Specifies that the video has racy content.
     *
     * @param Zend_Gdata_YouTube_Extension_Racy $racy The racy flag object
     * @return Zend_Gdata_YouTube_VideoEntry Provides a fluent interface
     */ 
    public function setRacy($racy = null) 
    {
        $this->_racy = $racy;
        return $this;
    } 

    /**
     * Returns the racy flag object.
     *
     * @return Zend_Gdata_YouTube_Extension_Racy  The racy flag object
     */
    public function getRacy()
    {
        return $this->_racy;
    }

    /**
     * Sets the rating relating to the video.
     *
     * @param Zend_Gdata_YouTube_Extension_Rating $rating The rating relating to the video
     * @return Zend_Gdata_YouTube_VideoEntry Provides a fluent interface
     */ 
    public function setRating($rating = null) 
    {
        $this->_rating = $rating;
        return $this;
    } 

    /**
     * Returns the rating relating to the video.
     *
     * @return Zend_Gdata_YouTube_Extension_Rating  The rating relating to the video 
     */
    public function getRating()
    {
        return $this->_rating;
    }

    /**
     * Sets the comments relating to the video.
     *
     * @param Zend_Gdata_Extension_Comments $comments The comments relating to the video
     * @return Zend_Gdata_YouTube_VideoEntry Provides a fluent interface
     */
    public function setComments($comments = null)
    {
        $this->_comments = $comments;
        return $this;
    }

    /**
     * Returns the comments relating to the video.
     *
     * @return Zend_Gdata_Extension_Comments  The comments relating to the video
     */
    public function getComments()
    {
        return $this->_comments;
    }

    /**
     * Sets the array of embedded feeds related to the video
     *
     * @param array $feedLink The array of embedded feeds relating to the video
     * @return Zend_Gdata_YouTube_VideoEntry Provides a fluent interface
     */
    public function setFeedLink($feedLink = null)
    {
        $this->_feedLink = $feedLink;
        return $this;
    }

    /**
     * Get the feed link property for this entry.
     *
     * @see setFeedLink
     * @param string $rel (optional) The rel value of the link to be found.
     *          If null, the array of links is returned.
     * @return mixed If $rel is specified, a Zend_Gdata_Extension_FeedLink
     *          object corresponding to the requested rel value is returned
     *          if found, or null if the requested value is not found. If
     *          $rel is null or not specified, an array of all available
     *          feed links for this entry is returned, or null if no feed
     *          links are set.
     */
    public function getFeedLink($rel = null)
    {
        if ($rel == null) {
            return $this->_feedLink;
        } else {
            foreach ($this->_feedLink as $feedLink) {
                if ($feedLink->rel == $rel) {
                    return $feedLink;
                }
            }
            return null;
        }
    }

    /**
     * Returns the link element relating to video responses.
     *
     * @return Zend_Gdata_App_Extension_Link
     */
    public function getVideoResponsesLink()
    {
        return $this->getLink(Zend_Gdata_YouTube::VIDEO_RESPONSES_REL);
    }

    /**
     * Returns the link element relating to video ratings.
     *
     * @return Zend_Gdata_App_Extension_Link
     */
    public function getVideoRatingsLink()
    {
        return $this->getLink(Zend_Gdata_YouTube::VIDEO_RATINGS_REL);
    }

    /**
     * Returns the link element relating to video complaints.
     *
     * @return Zend_Gdata_App_Extension_Link
     */
    public function getVideoComplaintsLink()
    {
        return $this->getLink(Zend_Gdata_YouTube::VIDEO_COMPLAINTS_REL);
    }

    /**
     * Gets the YouTube video ID based upon the atom:id value
     *
     * @return string The video ID
     */
    public function getVideoId()
    {
        $fullId = $this->getId();
        $position = strrpos($fullId, '/');
        if ($pos === false) {
            require_once 'Zend/Gdata/App/Exception.php';
            throw new Zend_Gdata_App_Exception('Slash not found in atom:id');
        } else {
            return substr($fullId, strrpos($fullId,'/') + 1);
        }
    }

}
