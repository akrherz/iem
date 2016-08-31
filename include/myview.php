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
    public function __construct($template_dir = null) {
            $this->template_dir =  dirname(__FILE__).'/templates/';
            $this->headextra = '';
            $this->jsextra = '';
    }
    public function render($template_file) {
        if (file_exists($this->template_dir.$template_file)) {
            include $this->template_dir.$template_file;
        } else {
            throw new Exception('no template file ' . $template_file . ' present in directory ' . $this->template_dir);
        }
    }
    public function __set($name, $value) {
        $this->vars[$name] = $value;
    }
    public function __get($name) {
        return $this->vars[$name];
    }
}
?>