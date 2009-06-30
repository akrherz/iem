/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

Ext.onReady(function(){
    var p = new Ext.Panel({
        title: 'My Panel',
        collapsible:true,
        renderTo: 'panel-basic',
        width:400,
        html: Ext.example.bogusMarkup
    });

	// resetBodyCss: true
	new Ext.Panel({
		title: 'A Panel with W3C-suggested body-html styling',
		resetBodyCss: true,
		renderTo: 'panel-reset-true',
		width: 400,
		html: html.join('')
	});

	// resetBodyCss: false
	new Ext.Panel({
		title: 'Same panel as above with resetBodyCss: false',
		normal: false,
		renderTo: 'panel-reset-false',
		width: 400,
		html: html.join('')
	});
});

// Some sample html
var html = [
	'<h1>Heading One</h1>',
	'<h2>Heading Two</h2>',
	'<p>This is a paragraph with <strong>STRONG</strong>, <em>EMPHASIS</em> and a <a href="#">Link</a></p>',
	'<table>',
		'<tr>',
			'<td>Table Column One</td>',
			'<td>Table Column Two</td>',
		'</tr>',
	'</table>',
	'<ul>',
		'<li>Un-ordered List-item One</li>',
		'<li>Un-ordered List-item One</li>',
	'</ul>',
	'<ol>',
		'<li>Ordered List-item One</li>',
		'<li>Ordered List-item Two</li>',
	'</ol>',
	'<blockquote>This is a blockquote</blockquote>'
];