<?php
/* Here lies the dead simple templating engine the IEM uses
 * 
 * For example
 *     $t = new MyView();
 *     $t->blah = "Hi";
 *     $t->render('single.phtml');
 *     
 *  http://coding.smashingmagazine.com/2011/10/17/getting-started-with-php-templating/
 */
class MyView {
    protected $vars = array();
    public ?string $bodyextra = null;
    public ?string $breadcrumbs = null;
    public ?string $content = null;
    public ?string $current_network = null;
    public ?string $headextra = null;
    public bool $iemss = FALSE;
    public ?string $jsextra = null;
    public int $refresh = -1;
    public ?string $sites_current = null;
    public ?string $template_dir = null;
    public ?string $title = null;
    public string $twitter_card = "summary";
    public string $twitter_description = "Iowa Environmental Mesonet of Iowa State University";
    public string $twitter_image = "/images/logo_large.png";
    public ?string $twitter_video = null;
    public int $twitter_video_width = 0;
    public int $twitter_video_height = 0;
    public ?string $iem_resource = null;

    public function __construct() {
            $this->template_dir =  dirname(__FILE__).'/templates/';  // skipcq
    }
    public function render($template_file) {
        if ($this->iem_resource != null) {
            require_once dirname(__FILE__) . "/generators.php";
            $this->content .= get_website_citations($this->iem_resource);
        }
        if (file_exists($this->template_dir.$template_file)) {
            include $this->template_dir.$template_file;
        } else {
            throw new Exception(
                'no template file ' .
                $template_file . ' present in directory ' .
                $this->template_dir
            );
        }
    }
    public function __set($name, $value) {
        $this->vars[$name] = $value;
    }
    public function __get($name) {
        return $this->vars[$name];
    }
}
