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
 * @package    Zend_Translate
 * @copyright  Copyright (c) 2005-2007 Zend Technologies USA Inc. (http://www.zend.com)
 * @version    $Id: Date.php 2498 2006-12-23 22:13:38Z thomas $
 * @license    http://framework.zend.com/license/new-bsd     New BSD License
 */


/** Zend_Locale */
require_once 'Zend/Locale.php';

/** Zend_Translate_Exception */
require_once 'Zend/Translate/Exception.php';

/**
 * @category   Zend
 * @package    Zend_Translate
 * @copyright  Copyright (c) 2005-2007 Zend Technologies USA Inc. (http://www.zend.com)
 * @license    http://framework.zend.com/license/new-bsd     New BSD License
 */
abstract class Zend_Translate_Adapter {
    /**
     * Current locale/language
     *
     * @var string|null
     */
    protected $_locale;
    private   $_automatic = true;

    /**
     * Table of all supported languages
     *
     * @var array
     */
    protected $_languages = array();

    // Scan options
    const LOCALE_DIRECTORY = 1;
    const LOCALE_FILENAME  = 2;

    /**
     * Array with all options, each adapter can have own additional options
     *
     * @var array
     */
    protected $_options = array(
        'clear' => false, // clear previous loaded translation data
        'scan'  => null   // where to find the locale
    );

    /**
     * Translation table
     *
     * @var array
     */
    protected $_translate = array();


    /**
     * Generates the adapter
     *
     * @param  string|array        $data      Translation data for this adapter
     * @param  string|Zend_Locale  $locale    OPTIONAL Locale/Language to set, identical with Locale identifiers
     *                                        see Zend_Locale for more information
     * @param  string|array        $options   Options for the adaptor
     * @throws Zend_Translate_Exception
     */
    public function __construct($data, $locale = null, array $options = array())
    {
        if ($locale === null) {
            $locale = new Zend_Locale();
        }
        if ($locale instanceof Zend_Locale) { 
            $locale = $locale->toString(); 
        } 

        $options = array_merge($this->_options, $options);
        if (is_string($data) and is_dir($data)) {
            foreach (new RecursiveIteratorIterator(
                     new RecursiveDirectoryIterator($data, RecursiveDirectoryIterator::KEY_AS_PATHNAME), 
                     RecursiveIteratorIterator::SELF_FIRST) as $file => $info) {
                if ($info->isDir()) {

                    $directory = $info->getPath();
                    // pathname as locale
                    if (($options['scan'] === self::LOCALE_DIRECTORY) and (Zend_Locale::isLocale((string) $info))) {
                        $locale = (string) $info;
                    }

                } else if ($info->isFile()) {

                    // filename as locale
                    if ($options['scan'] === self::LOCALE_FILENAME) {
                        if (Zend_Locale::isLocale((string) $info)) {
                            $locale = (string) $info;
                        } else {
                            $found = false;
                            $parts = explode('.', (string) $info);
                            foreach($parts as $token) {
                                $parts = array_merge(explode('_', $token), $parts);
                            }
                            foreach($parts as $token) {
                                $parts = array_merge(explode('-', $token), $parts);
                            }
                            $parts = array_unique($parts);
                            foreach($parts as $token) {
                                if (Zend_Locale::isLocale($token)) {
                                    $locale = $token;
                                }
                            }
                        }
                    }
                    try {
                        $this->addTranslation((string) $info->getPathname(), $locale, $options);
                        if ((array_key_exists($locale, $this->_translate)) and (count($this->_translate[$locale]) > 0)) {
                            $this->setLocale($locale);
                        }
                    } catch (Zend_Translate_Exception $e) {
                        // ignore failed sources while scanning
                    }
                }
            }
        } else {
            $this->addTranslation($data, $locale, $options);
            if ((array_key_exists($locale, $this->_translate)) and (count($this->_translate[$locale]) > 0)) {
                $this->setLocale($locale);
            }
        } 
        $this->_automatic = true;
    }


    /**
     * Sets new adapter options
     *
     * @param  array  $options  Adapter options
     * @throws Zend_Translate_Exception
     */
    public function setOptions(array $options = array())
    {
        foreach ($options as $key => $option) {
            $this->_options[strtolower($key)] = $option;
        }
    }

    /**
     * Returns the adapters name and it's options
     *
     * @param  string|null  $optionKey  String returns this option
     *                                  null returns all options
     * @return integer|string|array
     */
    public function getOptions($optionKey = null)
    {
        if ($optionKey === null) {
            return $this->_options;
        }
        if (array_key_exists(strtolower($optionKey), $this->_options)) {
            return $this->_options[strtolower($optionKey)];
        }
        return null;
    }


    /**
     * Gets locale
     *
     * @return Zend_Locale|null
     */
    public function getLocale()
    {
        return $this->_locale;
    }


    /**
     * Sets locale
     *
     * @param  string|Zend_Locale  $locale  Locale to set
     * @throws Zend_Translate_Exception
     */
    public function setLocale($locale)
    {
        if ($locale instanceof Zend_Locale) {
            $locale = $locale->toString();
        } else if (!$locale = Zend_Locale::isLocale($locale)) {
            throw new Zend_Translate_Exception("The given Language ({$locale}) does not exist");
        }

        if (!in_array($locale, $this->_languages)) {
            $temp = explode('_', $locale);
            if (!in_array($temp[0], $this->_languages)) {
                throw new Zend_Translate_Exception("Language ({$locale}) has to be added before it can be used.");
            }
            $locale = $temp[0];
        }

        $this->_locale = $locale;
        if ($locale == "auto") {
            $this->_automatic = true;
        } else {
            $this->_automatic = false;
        }
    }


    /**
     * Returns the avaiable languages from this adapter
     *
     * @return array
     */
    public function getList()
    {
        return $this->_languages;
    }


    /**
     * Returns all avaiable message ids from this adapter
     * If no locale is given, the actual language will be used
     *
     * @param  $locale  String|Zend_Locale  Language to return the message ids from
     * @return array
     */
    public function getMessageIds($locale = null)
    {
        if (empty($locale) or !$this->isAvaiable($locale)) {
            $locale = $this->_locale;
        }
        return array_keys($this->_translate[$locale]);
    }


    /**
     * Returns all avaiable translations from this adapter
     * If no locale is given, the actual language will be used
     * If 'all' is given the complete translation dictionary will be returned
     *
     * @param  $locale  String|Zend_Locale  Language to return the messages from
     * @return array
     */
    public function getMessages($locale = null)
    {
        if ($locale == 'all') { 
            return $this->_translate; 
        } 
        if (empty($locale) or !$this->isAvaiable($locale)) { 
            $locale = $this->_locale; 
        } 
        return $this->_translate[$locale];
    }


    /**
     * Is the wished language avaiable ?
     *
     * @param  string|Zend_Locale  $locale  Language to search for, identical with locale identifier,
     *                                      see Zend_Locale for more information
     * @return boolean
     */
    public function isAvailable($locale)
    {
        if ($locale instanceof Zend_Locale) {
            $locale = $locale->toString();
        }

        return in_array($locale, $this->_languages);
    }

    /**
     * Load translation data
     *
     * @param  mixed               $data
     * @param  string|Zend_Locale  $locale
     * @param  array               $options
     */
    abstract protected function _loadTranslationData($data, $locale, array $options = array());

    /**
     * Add translation data
     *
     * It may be a new language or additional data for existing language
     * If $clear parameter is true, then translation data for specified
     * language is replaced and added otherwise
     *
     * @param  array|string          $data    Translation data
     * @param  string|Zend_Locale    $locale  Locale/Language to add data for, identical with locale identifier,
     *                                        see Zend_Locale for more information
     * @param  array                 $options OPTIONAL Option for this Adapter
     * @throws Zend_Translate_Exception
     */
    public function addTranslation($data, $locale, array $options = array())
    {
        if (!$locale = Zend_Locale::isLocale($locale)) {
            throw new Zend_Translate_Exception("The given Language ({$locale}) does not exist");
        }

        if (!in_array($locale, $this->_languages)) {
            $this->_languages[$locale] = $locale;
        }

        $this->_loadTranslationData($data, $locale, $options);
        if ($this->_automatic === true) {
            $find = new Zend_Locale($locale);
            $browser = $find->getBrowser() + $find->getEnvironment();
            arsort($browser);
            foreach($browser as $language => $quality) {
                if (in_array($language, $this->_languages)) {
                    $this->_locale = $language;
                    break;
                }
            }
        }
    }


    /**
     * Translates the given string
     * returns the translation
     *
     * @param  string              $messageId  Translation string
     * @param  string|Zend_Locale  $locale     OPTIONAL Locale/Language to use, identical with locale identifier,
     *                                         see Zend_Locale for more information
     * @return string
     */
    public function translate($messageId, $locale = null)
    {
        if ($locale === null) {
            $locale = $this->_locale;
        } else {
            if (!$locale = Zend_Locale::isLocale($locale)) {
                // language does not exist, return original string
                return $messageId;
            }
        }

        if ((array_key_exists($locale, $this->_translate)) and
            (array_key_exists($messageId, $this->_translate[$locale]))) {
            // return original translation
            return $this->_translate[$locale][$messageId];
        } else if (strlen($locale) != 2) {
            // faster than creating a new locale and separate the leading part
            $locale = substr($locale, 0, -strlen(strrchr($locale, '_')));

            if ((array_key_exists($locale, $this->_translate)) and
                (array_key_exists($messageId, $this->_translate[$locale]))) {
                // return regionless translation (en_US -> en)
                return $this->_translate[$locale][$messageId];
            }
        }

        // no translation found, return original
        return $messageId;
    }


    /**
     * Translates the given string
     * returns the translation
     *
     * @param  string              $messageId  Translation string
     * @param  string|Zend_Locale  $locale     OPTIONAL Locale/Language to use, identical with locale identifier,
     *                                         see Zend_Locale for more information
     * @return string
     */
    public function _($messageId, $locale = null)
    {
        return $this->translate($messageId, $locale);
    }


    /**
     * Checks if a string is translated within the source or not
     * returns boolean
     *
     * @param  string              $messageId  Translation string
     * @param  boolean             $original   OPTIONAL Allow translation only for original language
     *                                         when true, a translation for 'en_US' would give false when it can
     *                                         be translated with 'en' only
     * @param  string|Zend_Locale  $locale     OPTIONAL Locale/Language to use, identical with locale identifier,
     *                                         see Zend_Locale for more information
     * @return boolean
     */
    public function isTranslated($messageId, $original = false, $locale = null)
    {
        if (($original !== false) and ($original !== true)) {
            $locale = $original;
            $original = false;
        }
        if ($locale === null) {
            $locale = $this->_locale;
        } else {
            if (!$locale = Zend_Locale::isLocale($locale)) {
                // language does not exist, return original string
                return false;
            }
        }

        if ((array_key_exists($locale, $this->_translate)) and
            (array_key_exists($messageId, $this->_translate[$locale]))) {
            // return original translation
            return true;
        } else if ((strlen($locale) != 2) and ($original === false)) {
            // faster than creating a new locale and separate the leading part
            $locale = substr($locale, 0, -strlen(strrchr($locale, '_')));

            if ((array_key_exists($locale, $this->_translate)) and
                (array_key_exists($messageId, $this->_translate[$locale]))) {
                // return regionless translation (en_US -> en)
                return true;
            }
        }

        // no translation found, return original
        return false;
    }


    /**
     * Returns the adapter name
     *
     * @return string
     */
    abstract public function toString();
}
