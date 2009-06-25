Ext.BLANK_IMAGE_URL = '../ext/resources/images/default/s.gif';
Ext.onReady(function(){

/**
 * @version 0.4
 * @author nerdydude81
 */Ext.override(Ext.Element, {
    /**
     * @cfg {string} printCSS The file path of a CSS file for printout.
     */
    printCSS: null,
    /**
     * @cfg {Boolean} printStyle Copy the style attribute of this element to the print iframe.
     */
    printStyle: false,
    /**
     * @property {string} printTitle Page Title for printout. 
     */
    printTitle: document.title,
    /**
     * Prints this element.
     * 
     * @param config {object} (optional)
     */
    print: function(config) {
        Ext.apply(this, config);
        
        var el = Ext.get(this.id).dom;
        if (this.isGrid) 
            el = el.parentNode;
        
        var c = document.getElementById('printcontainer');
        var iFrame = document.getElementById('printframe');
        
        var strTemplate = '<HTML><HEAD>{0}<TITLE>{1}</TITLE></HEAD><BODY onload="{2}"><DIV {3}>{4}</DIV></BODY></HTML>';
        var strLinkTpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
        var strAttr = '';
        var strFormat;
        var strHTML;
    
        if (c) {
            if (iFrame)
                c.removeChild(iFrame);
            el.removeChild(c);
        }
        
        for (var i = 0; i < el.attributes.length; i++) {
            if (Ext.isEmpty(el.attributes[i].value) || el.attributes[i].value.toLowerCase() != 'null') {
                strFormat = Ext.isEmpty(el.attributes[i].value)? '{0}="true" ': '{0}="{1}" ';
                if (this.printStyle? this.printStyle: el.attributes[i].name.toLowerCase() != 'style')
                    strAttr += String.format(strFormat, el.attributes[i].name, el.attributes[i].value);
            }
        }
        
        var strLink ='';
        if(this.printCSS){
            if(!Ext.isArray(this.printCSS))
                this.printCSS = [this.printCSS];
            
            for(var i=0; i<this.printCSS.length; i++) {
                strLink += String.format(strLinkTpl, this.printCSS[i]);
            }
        }
        
        strHTML = String.format(
            strTemplate,
            strLink,
            this.printTitle,
            '',
            strAttr,
            el.innerHTML
        );
        
        c = document.createElement('div');
        c.setAttribute('style','width:0px;height:0px;' + (Ext.isSafari? 'display:none;': 'visibility:hidden;'));
        c.setAttribute('id', 'printcontainer');
        el.appendChild(c);
        if (Ext.isIE)
            c.style.display = 'none';
        
        iFrame = document.createElement('iframe');
        iFrame.setAttribute('id', 'printframe');
        iFrame.setAttribute('name', 'printframe');
        c.appendChild(iFrame);
        
        iFrame.contentWindow.document.open();        
        iFrame.contentWindow.document.write(strHTML);
        iFrame.contentWindow.document.close();
        
        if (this.isGrid) {
            var iframeBody = Ext.get(iFrame.contentWindow.document.body);
            var cc = Ext.get(iframeBody.first().dom.parentNode);
            cc.child('div.x-panel-body').setStyle('height', '');
            cc.child('div.x-grid3').setStyle('height', '');
            cc.child('div.x-grid3-scroller').setStyle('height', '');
        }
        if (Ext.isIE)
            iFrame.contentWindow.document.execCommand('print');
        else
            iFrame.contentWindow.print();
    }
});



var cp = new Ext.state.CookieProvider({
       expires: new Date(new Date().getTime()+(1000*60*60*24*300))
});
Ext.state.Manager.setProvider(cp);



var tp = new Ext.tree.TreePanel({
             loader: new Ext.tree.TreeLoader({dataUrl:'products.txt'}),
             containerScroll:true,
             autoScroll:true,
             title:'Popular Products',
             root:  new Ext.tree.AsyncTreeNode({
                text: 'Browse',
                draggable:false, // disable root node dragging
                id:'source'
             })
});

var refreshAction = new Ext.Action({
  text: 'Refresh',
  handler: function() {
    var id = tabs.getActiveTab().getId();
    var tokens= id.split("-");
    tabs.getActiveTab().getUpdater().update({
          url: 'retreive.php', 
         params: 'pil='+ tokens[0] +'&cnt='+ tokens[1],
         discardUrl:false
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
}

var addTab = function(id, cnt) {
    var tid = id+"-"+cnt;
    tid = tid.toUpperCase();
    var a = tabs.find("id", tid);
    if (a.length > 0){ tabs.setActiveTab(tid); return; }
    tabs.add({
        id: tid,
        title: id,
        closable:true,
        autoScroll:true,
        autoLoad: {url: 'retreive.php', 
                   params: 'pil='+id+'&cnt='+cnt,
                   discardUrl:false},
        tbar: [refreshAction,
        {
            text    : 'Print Text',
            icon    : 'print.png',
            cls     : 'x-btn-text-icon',
            handler : function(){
                Ext.getCmp("tabPanel").getActiveTab().getEl().print();
            }
          }]
     }).show().addListener('destroy', function() {
        saveConfig();
     });
    saveConfig();
}

tp.addListener('click', function(node, e){
  if(node.isLeaf()){
     e.stopEvent();
     addTab(node.id, 1);
  }
});

 var tabs =  new Ext.TabPanel({
                   id: 'tabPanel',
                    region:'center',
                    height:.75,
                    plain:true,
                    enableTabScroll:true,
                    defaults:{bodyStyle:'padding:5px'},
                    items:[
     new Ext.Panel({contentEl:'help', title: 'Help',autoScroll:true})
                    ],
                    activeTab:0

                });

 var myform = new Ext.FormPanel({
             frame:true,
             defaultType:'textfield',
             title:'Enter Product ID Manually',
             labelWidth:50,
             items:[{
                   fieldLabel:'PIL:',
                   name:'pil',
                   allowBlank:false,
                   width: 150,
                   emptyText:'(Example) AFDDMX'
                }, new Ext.form.NumberField({
                   allowBlank:false,
                   maxValue:99,
                   minValue:0,
                   name:'sz',
                   width: 100,
                   fieldLabel:'Entries:',
                   value:1
                })
             ],
             buttons: [{
                 text:'Add',
                 handler: function() {
                    var pil = myform.getForm().findField('pil').getRawValue();
                    var cnt = myform.getForm().findField('sz').getRawValue();
                    if (pil == "" || cnt == ""){ 
                      Ext.MessageBox.alert('Error', 'PIL or Entries Invalid');
                      return;
                    }
                   addTab(pil, cnt);
                 } // End of handler
             }]
  });

 var myform2 = new Ext.FormPanel({
     frame: true,
     title: 'Select by WFO & Product',
     buttons: [{
         text:'Add',
         handler: function() {
           var wfo = myform2.getForm().findField('wfo').getValue();
           var afos = myform2.getForm().findField('afos').getValue();
           var cnt = myform2.getForm().findField('sz').getRawValue();
           var pil = afos+wfo;
           addTab(pil, cnt);
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


 var viewport = new Ext.Viewport({
            layout:'border',
            items:[
                new Ext.BoxComponent({ // raw
                    region:'north',
                    el: 'iem-header',
                    height:130
                }),
                new Ext.BoxComponent({ // raw
                    region:'south',
                    el: 'iem-footer',
                    height:50
                }),
                new Ext.Panel({ // raw
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
                    height:500,
                    items:[myform,myform2,tp]
                }),
                tabs
             ]
        });

var a = cp.get("afospils", "");
var ar = a.split(",");
for (var i=0; i < ar.length; i++)
{
  if (ar[i] == ""){ continue; }
  var tokens= ar[i].split("-");
  addTab( tokens[0], tokens[1]);
}
    });
