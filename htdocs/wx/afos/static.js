Ext.BLANK_IMAGE_URL = '/ext/resources/images/default/s.gif';
Ext.Ajax.setTimeout(500000);
var tabs;

// http://druckit.wordpress.com/2014/02/15/ext-js-4-printing-the-contents-of-an-ext-panel/
Ext.define('MyApp.view.override.Panel', {
    override: 'Ext.panel.Panel',
 
    print: function(pnl) {
 
        if (!pnl) {
            pnl = this;
        }
 
        // instantiate hidden iframe
 
        var iFrameId = "printerFrame";
        var printFrame = Ext.get(iFrameId);
 
        if (printFrame == null) {
            printFrame = Ext.getBody().appendChild({
                id: iFrameId,
                tag: 'iframe',
                cls: 'x-hidden',
                style: {
                    display: "none"
                }
            });
        }
 
        var cw = printFrame.dom.contentWindow;
 
        // instantiate application stylesheets in the hidden iframe
 
        var stylesheets = "";
        for (var i = 0; i < document.styleSheets.length; i++) {
            stylesheets += Ext.String.format('<link rel="stylesheet" href="{0}" />', document.styleSheets[i].href);
        }
 
        // various style overrides
        stylesheets += ''.concat(
          "<style>", 
            ".x-panel-body {overflow: visible !important;}",
            // experimental - page break after embedded panels
            // .x-panel {page-break-after: always; margin-top: 10px}",
          "</style>"
         );
 
        // get the contents of the panel and remove hardcoded overflow properties
        var markup = pnl.getEl().dom.innerHTML;
        while (markup.indexOf('overflow: auto;') >= 0) {
            markup = markup.replace('overflow: auto;', '');
        }
 
        var str = Ext.String.format('<html><head>{0}</head><body>{1}</body></html>',stylesheets,markup);
 
        // output to the iframe
        cw.document.open();
        cw.document.write(str);
        cw.document.close();
 
        // remove style attrib that has hardcoded height property
        cw.document.getElementsByTagName('DIV')[0].removeAttribute('style');
 
        // print the iframe
        cw.print();
 
        // destroy the iframe
        Ext.fly(iFrameId).destroy();
 
    }
});

Ext.onReady(function(){

	// Add the additional 'advanced' VTypes
	Ext.apply(Ext.form.VTypes, {
	    daterange : function(val, field) {
	        var date = field.parseDate(val);

	        if(!date){
	            return false;
	        }
	        if (field.startDateField) {
	            var start = Ext.getCmp(field.startDateField);
	            if (!start.maxValue || (date.getTime() != start.maxValue.getTime())) {
	                start.setMaxValue(date);
	                start.validate();
	            }
	        }
	        else if (field.endDateField) {
	            var end = Ext.getCmp(field.endDateField);
	            if (!end.minValue || (date.getTime() != end.minValue.getTime())) {
	                end.setMinValue(date);
	                end.validate();
	            }
	        }
	        /*
	         * Always return true since we're only using this vtype to set the
	         * min/max allowed values (these are tested for after the vtype test)
	         */
	        return true;
	    }
	});	
	
var cp = new Ext.state.CookieProvider({
       expires: new Date(new Date().getTime()+(1000*60*60*24*300))
});
Ext.state.Manager.setProvider(cp);


var refreshAction = new Ext.Action({
	text: 'Refresh',
	handler: function() {
		var id = tabs.getActiveTab().getId();
		var tokens= id.split("-");
		var uri;
		if (tokens.length == 2){
			uri = '/cgi-bin/afos/retrieve.py?fmt=html&pil='+ tokens[0] +'&limit='+ tokens[1];
		}
		if (tokens.length == 3){
			uri = '/cgi-bin/afos/retrieve.py?fmt=html&pil='+ tokens[0] +'&limit='+ tokens[1] +'&center='+ tokens[2];
		}
		tabs.getActiveTab().getLoader().load({
			url       : uri, 
			timeout	: 120,
			autoLoad : true,
			loadMask : true
		}); 
	}
});
var saveConfig = function() {
    // Update Cookie?!
    var n = "";
    for(var i=1;i< tabs.items.length;i++){
      var q = tabs.items.get(i);
      n = n +","+ q.getId();
    }
    cp.set("afospils", n);
};

var addTab = function(id, center, cnt, sdate, edate) {
	if (!sdate){
		sdate = new Date('11/26/2000');
	} 
	if (!edate){
		edate = Ext.Date.add(new Date(), Ext.Date.DAY, 1);
	}
    var tid = id+"-"+cnt;
    tid = tid.toUpperCase();
    var a = Ext.getCmp(tid);
    if (a !== undefined){ tabs.setActiveTab(tid); return; }
    var uri = '/cgi-bin/afos/retrieve.py?pil='+id+'&limit='+cnt+'&sdate='+Ext.Date.format(sdate, 'Y-m-d')
    		+'&edate='+ Ext.Date.format(edate, 'Y-m-d') +'&fmt=html';
    var title = id;
    if (center != null){
    	uri = uri +"&center="+center;
    	title = title +"-"+ center;
    	tid = tid +"-"+ center;
    }
    var newtab = tabs.add({
        id         : tid,
        title      : title,
        closable   : true,
        autoScroll : true,
        listeners : {
        	destroy: function(){
        		saveConfig();
        	}
        },
        loader  : {
        	url        : uri, 
            autoLoad   : false,
            timeout : 120,
            loadMask : {msg: 'Searching Database, Standby...'}
        },
        tbar: [refreshAction,
        {
            text    : 'Print Text',
            icon    : '/images/print.png',
            cls     : 'x-btn-text-icon',
            handler : function(){
                Ext.getCmp("tabPanel").getActiveTab().print();
            }
          }]
     });
    newtab.show();
    newtab.getLoader().load();
    saveConfig();
};

var tp = new Ext.tree.TreePanel({
	containerScroll:true,
	autoScroll:true,
	title:'Popular Products',
	listeners : {
		itemclick : function(node, record, item, idx, e){
				addTab(record.data.id, null, 1, null, null);
		}
	},
	root:  {
		text: 'Browse',
		draggable:false, // disable root node dragging
		id:'source',
		children:[{id:'SWOMCD', text: 'SPC Mesoscale Discussion', leaf: true},
		          {id:'SWODY1', text: 'SPC Day1 Outlook', leaf: true},
		          {id:'SWODY2', text: 'SPC Day2 Outlook', leaf: true},
		          {id:'PMDHMD', text: 'Model Diagnostic Discussion', leaf: true},
		          {
		           text: 'GFSX MOS',
		           children: [{
		                     id:'MEXDSM',
		                     text: 'Des Moines',
		                     leaf: true
		                 },{
		                     id:'MEXDVN',
		                     text: 'Davenport',
		                     leaf: true
		                 }]
		           },
		          {
		           text: 'NAM MOS',
		           children: [{
		                     id:'METDSM',
		                     text: 'Des Moines',
		                     leaf: true
		                 },{
		                     id:'METDVN',
		                     text: 'Davenport',
		                     leaf: true
		                 }]
		           },
		          {
		           text: 'GFS MOS',
		           children: [{
		                     id:'MAVDSM',
		                     text: 'Des Moines',
		                     leaf: true
		                 },{
		                     id:'MAVDVN',
		                     text: 'Davenport',
		                     leaf: true
		                 }]
		           }
		         ]
	}
});


	tabs = new Ext.TabPanel({
		id : 'tabPanel',
		region : 'center',
		height : .75,
		plain : true,
		enableTabScroll : true,
		defaults : {
			bodyStyle : 'padding:5px'
		},
		items : [{
			contentEl : 'help',
			title : 'Help',
			autoScroll : true
		}],
		activeTab : 0

	});

 var myform = new Ext.FormPanel({
             frame:true,
             defaultType:'textfield',
             title:'Enter Product ID Manually',
             labelWidth:50,
             border: false,
             bodyPadding: 10,
             autoScroll: true,
             fieldDefaults: {
                 labelAlign: 'top',
                 labelWidth: 100,
                 labelStyle: 'font-weight:bold'
             },
             items:[{
                   fieldLabel:'PIL:',
                   name:'pil',
                   allowBlank:false,
                   emptyText:'(Example) AFDDMX'
                },{
                    fieldLabel : 'Center:',
                    name       : 'center',
                    allowBlank : true,
                    width      : 150,
                    emptyText  : '(Optional)'
                }, new Ext.form.NumberField({
                   allowBlank:false,
                   maxValue:9999,
                   minValue:0,
                   name:'sz',
                   width: 100,
                   fieldLabel:'Entries:',
                   value:1
                }), {
                	xtype : 'datefield',
                	maxDate : Ext.Date.add(new Date(), Ext.Date.DAY, 1),
                	minDate : new Date('11/25/2000'),
                	name : 'sdate',
                	id : 'sdate',
                	value : new Date('11/26/2000'),
                	vtype : 'daterange',
                	width: 120,
                	endDateField : 'edate',
                	fieldLabel : 'Start Date'
                }, {
                	xtype : 'datefield',
                	maxDate : Ext.Date.add(new Date(), Ext.Date.DAY, 1),
                	minDate : new Date('11/25/2000'),
                	name : 'edate',
                	value : Ext.Date.add(new Date(), Ext.Date.DAY, 1),
                	width: 120,
                	vtype : 'daterange',
                	id : 'edate',
                	startDateField : 'sdate',
                	fieldLabel : 'End Date'
                }
             ],
             buttons: [{
                 text:'Add',
                 handler: function() {
                    var pil = myform.getForm().findField('pil').getRawValue();
                    var center = myform.getForm().findField('center').getRawValue();
                    var cnt = myform.getForm().findField('sz').getRawValue();
                    var sdate = myform.getForm().findField('sdate').getValue();
                    var edate = myform.getForm().findField('edate').getValue();
                    if (pil == "" || cnt == ""){ 
                      Ext.MessageBox.alert('Error', 'PIL or Entries Invalid');
                      return;
                    }
                   addTab(pil, center, cnt, sdate, edate);
                 } // End of handler
             }]
  });

 var myform2 = new Ext.FormPanel({
     frame: true,
     border: false,
     title: 'Select by WFO & Product',
     buttons: [{
         text:'Add',
         handler: function() {
           var wfo = myform2.getForm().findField('wfo').getValue();
           var afos = myform2.getForm().findField('afos').getValue();
           var cnt = myform2.getForm().findField('sz').getRawValue();
           var pil = afos+wfo;
           addTab(pil, null, cnt, null, null);
          } // End of handler
     }],
     items: [
       new Ext.form.ComboBox({
             hiddenName:'wfo',
             store: new Ext.data.SimpleStore({
                      fields: ['abbr', 'wfo'],
                      data : iemdata.wfos 
             }),
             valueField:'abbr',
             displayField:'wfo',
             typeAhead: true,
             mode: 'local',
             triggerAction: 'all',
             emptyText:'Select a WFO...',
             hideLabel:true,
             selectOnFocus:true,
             listWidth:180,
             width:180
        }), new Ext.form.ComboBox({
             hiddenName:'afos',
             store: new Ext.data.SimpleStore({
                      fields: ['id', 'product'],
                      data : iemdata.nws_products
             }),
             valueField:'id',
             displayField:'product',
             typeAhead: true,
             mode: 'local',
             triggerAction: 'all',
             emptyText:'Select Product...',
             hideLabel:true,
             selectOnFocus:true,
             listWidth:180,
             width:180
         }),new Ext.form.NumberField({
                   allowBlank:false,
                   maxValue:99,
                   minValue:0,
                   name:'sz',
                   width: 100,
                   fieldLabel:'Entries:',
                   value:1
        })
      ]
});


 Ext.create('Ext.Panel', {
	  renderTo : 'main',
	  height: Ext.getBody().getViewSize().height - 120,
	  layout   : {
	          type: 'border',
	          align: 'stretch'
	  },
	 items:[{ 
		 region:'west',
		 layout:'accordion',
		 layoutConfig: {
			 // layout-specific configs go here
			 titleCollapse: false,
			 animate: true,
			 activeOnTop: false,
			 fill:true
		 },
		 width:210,
		 items:[myform, myform2, tp]
	 },
	 tabs
	 ]
 });

var a = cp.get("afospils", "");
var ar = a.split(",");
for (var i=0; i < ar.length; i++){
  if (ar[i] == ""){ continue; }
  var tokens = ar[i].split("-");
  if (tokens.length == 2){
    addTab( tokens[0], null, tokens[1], null, null);
  }
  else if (tokens.length == 3){
	    addTab( tokens[0], tokens[2], tokens[1], null, null);
  }
}
    });
