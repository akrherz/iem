/*
 jQuery Plugin: Table Filter v0.2.3

 LICENSE: http://hail2u.mit-license.org/2009
*/
(function(a){a.fn.addTableFilter=function(d){var b=a.extend({},a.fn.addTableFilter.defaults,d),c,e;this.is("table")&&(this.attr("id")||this.attr({id:"t-"+Math.floor(99999999*Math.random())}),c=this.attr("id"),d=c+"-filtering",e=a("<label/>").attr({"for":d}).append(b.labelText),b=a('<input type="search"/>').attr({id:d,size:b.size}).on("click",function(){a(this).keyup()}),a("<p/>").addClass("formTableFilter").append(e).append(b).insertBefore(this),a("#"+d).delayBind("keyup",function(b){var d=a(this).val().toLowerCase().split(" ");
a("#"+c+" tbody tr").each(function(){var b=a(this).html().toLowerCase().replace(/<.+?>/g,"").replace(/\s+/g," "),c=0;a.each(d,function(){if(0>b.indexOf(this))return c=1,!1});c?a(this).hide():a(this).show()})},300));return this};a.fn.addTableFilter.defaults={labelText:"Keyword(s): ",size:32};a.fn.delayBind=function(d,b,c,e){a.isFunction(b)&&(e=c,c=b,b=void 0);var g=this,f=null;return this.bind(d,b,function(b){clearTimeout(f);f=setTimeout(function(){c.apply(g,[a.extend({},b)])},e)})}})(jQuery);
