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
 * @category  Zend
 * @package   Zend_Text
 * @copyright Copyright (c) 2005-2008 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd     New BSD License
 * @version   $Id$
 */

/**
 * Zend_Text_MultiByte contains multibyte safe string methods
 *
 * @category  Zend
 * @package   Zend_Text
 * @copyright Copyright (c) 2005-2008 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd     New BSD License
 */
class Zend_Text_MultiByte
{
    /**
     * Word wrap
     *
     * @param  string  $string
     * @param  integer $width
     * @param  string  $break
     * @param  boolean $cut
     * @param  string  $charset
     * @return string
     */
    public static function wordWrap($string, $width = 75, $break = "\n", $cut = false, $charset = 'UTF-8')
    {
        if ($cut === false) {
            $regexp = '#^(?:[\x00-\x7F]|[\xC0-\xFF][\x80-\xBF]+){' . $width . ',}\b#U';
        } else {
            $regexp = '#^(?:[\x00-\x7F]|[\xC0-\xFF][\x80-\xBF]+){' . $width . '}#';
        }

        $lines  = explode($break, $string);
        $return = array();

        foreach ($lines as $line) {
            $whileWhat = ceil(iconv_strlen($line, $charset) / $width);
            $i         = 1;
            $result    = '';

            while ($i < $whileWhat) {
                preg_match($regexp, $line, $matches);

                $result .= $matches[0] . $break;
                $line    = substr($string, strlen($matches[0]));

                $i++;
            }

            $return[] = $result . $line;
        }

        return implode($break, $return);
    }

    /**
     * String padding
     *
     * @param  string  $input
     * @param  integer $padLength
     * @param  string  $padString
     * @param  integer $padType
     * @param  string  $charset
     * @return string
     */
    public static function strPad($input, $padLength, $padString = ' ', $padType = STR_PAD_RIGHT, $charset = 'UTF-8')
    {
        $return          = '';
        $lengthOfPadding = $padLength - iconv_strlen($input, $charset);
        $padStringLength = iconv_strlen($padString, $charset);

        if ($padStringLength === 0 || $lengthOfPadding === 0) {
            $return = $input;
        } else {
            $repeatCount = floor($lengthOfPadding / $padStringLength);

            if ($padType === STR_PAD_BOTH) {
                $lastStringLeft  = '';
                $lastStringRight = '';
                $repeatCountLeft = $repeatCountRight = ($repeatCount - $repeatCount % 2) / 2;

                $lastStringLength       = $lengthOfPadding - 2 * $repeatCountLeft * $padStringLength;
                $lastStringLeftLength   = $lastStringRightLength = floor($lastStringLength / 2);
                $lastStringRightLength += $lastStringLength % 2;

                $lastStringLeft  = iconv_substr($padString, 0, $lastStringLeftLength, $charset);
                $lastStringRight = iconv_substr($padString, 0, $lastStringRightLength, $charset);

                $return = str_repeat($padString, $repeatCountLeft) . $lastStringLeft
                        . $input
                        . str_repeat($padString, $repeatCountRight) . $lastStringRight;
            } else {
                $lastString = iconv_substr($padString, 0, $lengthOfPadding % $padStringLength, $charset);

                if ($padType === STR_PAD_LEFT) {
                    $return = str_repeat($padString, $repeatCount) . $lastString . $input;
                } else {
                    $return = $input . str_repeat($padString, $repeatCount) . $lastString;
                }
            }
        }

        return $return;
    }
}
