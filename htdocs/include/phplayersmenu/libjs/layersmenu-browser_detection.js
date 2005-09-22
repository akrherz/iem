<script language="JavaScript" type="text/javascript">
<!--
// PHP Layers Menu 3.1.0 (C) 2001-2003 Marco Pratesi (marco at telug dot it)

DOM = (document.getElementById) ? 1 : 0;
NS4 = (document.layers) ? 1 : 0;
// We need to explicitly detect Konqueror
// because Konqueror 3 sets IE = 1 ... AAAAAAAAAARGHHH!!!
Konqueror = (navigator.userAgent.indexOf("Konqueror") > -1) ? 1 : 0;
// We need to detect Konqueror 2.2 as it does not handle the window.onresize event
Konqueror22 = (navigator.userAgent.indexOf("Konqueror 2.2") > -1 || navigator.userAgent.indexOf("Konqueror/2.2") > -1) ? 1 : 0;
Opera = (navigator.userAgent.indexOf("Opera") > -1) ? 1 : 0;
Opera5 = (navigator.userAgent.indexOf("Opera 5") > -1 || navigator.userAgent.indexOf("Opera/5") > -1) ? 1 : 0;
Opera6 = (navigator.userAgent.indexOf("Opera 6") > -1 || navigator.userAgent.indexOf("Opera/6") > -1) ? 1 : 0;
Opera56 = Opera5 || Opera6;
IE = (navigator.userAgent.indexOf("MSIE") > -1) ? 1 : 0;
IE = IE && !Opera;
IE5 = IE && DOM;
IE4 = (document.all) ? 1 : 0;
IE4 = IE4 && IE && !DOM;

// -->
</script>
