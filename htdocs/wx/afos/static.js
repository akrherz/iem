Ext.BLANK_IMAGE_URL = '../../ext/resources/images/default/s.gif';
Ext.onReady(function(){

/**
 * Prints the contents of an Ext.Panel
 */
Ext.ux.Printer.PanelRenderer = Ext.extend(Ext.ux.Printer.BaseRenderer, {

 /**
  * Generates the HTML fragment that will be rendered inside the <html> element of the printing window
  */
 generateBody: function(panel) {
   return String.format("<div class='x-panel-print'>{0}</div>", panel.body.dom.innerHTML);
 }
});

Ext.ux.Printer.registerRenderer("panel", Ext.ux.Printer.PanelRenderer);
Ext.ux.Printer.BaseRenderer.prototype.stylesheetPath = 'print.css';


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
                Ext.ux.Printer.print(Ext.getCmp("tabPanel").getActiveTab());
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
