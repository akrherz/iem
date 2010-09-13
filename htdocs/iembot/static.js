Ext.BLANK_IMAGE_URL = '../ext/resources/images/default/s.gif';

Ext.onReady(function(){

/*
 * Cookie support, to effectively bookmark the open tabs 
 */
var cp = new Ext.state.CookieProvider({
    expires: new Date(new Date().getTime()+(1000*60*60*24*300))
});
Ext.state.Manager.setProvider(cp);

/*
 * Save to cookie which tabs we are monitoring 
 */
var saveConfig = function() {
    // Update Cookie?!
    var n = "";
    for(var i=2;i< Ext.getCmp('tabs').items.length;i++){
        var q = Ext.getCmp('tabs').items.get(i);
        n = n +","+ q.getId();
    }
    cp.set("nwsbot_tabs", n);
}


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

var Base64 = (function() {
    // Private property
    	var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

    // Private method for UTF-8 encoding
	    function utf8Encode(string) {
	        string = string.replace(/\r\n/g,"\n");
	        var utftext = "";
	        for (var n = 0; n < string.length; n++) {
	            var c = string.charCodeAt(n);
	            if (c < 128) {
	                utftext += String.fromCharCode(c);
	            }
	            else if((c > 127) && (c < 2048)) {
	                utftext += String.fromCharCode((c >> 6) | 192);
	                utftext += String.fromCharCode((c & 63) | 128);
	            }
	            else {
	                utftext += String.fromCharCode((c >> 12) | 224);
	                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
	                utftext += String.fromCharCode((c & 63) | 128);
	            }
	        }
	        return utftext;
	    }

    // Public method for encoding
	    return {
	        encode : (typeof btoa == 'function') ? function(input) { return btoa(input); } : function (input) {
	            var output = "";
	            var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
	            var i = 0;
	            input = utf8Encode(input);
	            while (i < input.length) {
	                chr1 = input.charCodeAt(i++);
	                chr2 = input.charCodeAt(i++);
	                chr3 = input.charCodeAt(i++);
	                enc1 = chr1 >> 2;
	                enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
	                enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
	                enc4 = chr3 & 63;
	                if (isNaN(chr2)) {
	                    enc3 = enc4 = 64;
	                } else if (isNaN(chr3)) {
	                    enc4 = 64;
	                }
	                output = output +
	                keyStr.charAt(enc1) + keyStr.charAt(enc2) +
	                keyStr.charAt(enc3) + keyStr.charAt(enc4);
	            }
	            return output;
	        }
	    };
})();


Ext.ux.SliderTip = Ext.extend(Ext.Tip, {
    minWidth: 10,
    offsets : [0, -10],
    init : function(slider){
        slider.on('dragstart', this.onSlide, this);
        slider.on('drag', this.onSlide, this);
        slider.on('dragend', this.hide, this);
        slider.on('destroy', this.destroy, this);
    },

    onSlide : function(slider){
        this.show();
        this.body.update(this.getText(slider));
        this.doAutoWidth();
        this.el.alignTo(slider.thumb, 'b-t?', this.offsets);
    },

    getText : function(slider){
        return slider.getValue();
    }
});

/* 
 * Necessary to support changing the icon on the panel's tab
 */
Ext.override(Ext.Panel, {
    setIconCls: function(i) {
        Ext.fly(this.ownerCt.getTabEl(this)).child('.x-tab-strip-text').replaceClass(this.iconCls, i);
        this.setIconClass(i);
    }
});


Ext.override(Date, {
    toUTC : function() {
                        // Convert the date to the UTC date
        return this.add(Date.MINUTE, this.getTimezoneOffset());
    },
    
    fromUTC : function() {
                        // Convert the date from the UTC date
        return this.add(Date.MINUTE, -this.getTimezoneOffset());
    }    
}); 

var LinkInterceptor = {
    render: function(p){
        p.body.on({
            'mousedown': function(e, t){ // try to intercept the easy way
                t.target = '_blank';
            },
            'click': function(e, t){ // if they tab + enter a link, need to do it old fashioned way
                if(String(t.target).toLowerCase() != '_blank'){
                    e.stopEvent();
                    window.open(t.href);
                }
            },
            delegate:'a'
        });
    }
};



function UTCStringToDate(dtStr, format){
    var dt = Date.parseDate(dtStr, format);
    if (dt == undefined) return ''; // or whatever you want to do
    return dt.fromUTC();
} 

/*
 * Generate a html version of the active grid 
 */
function grid2html(){
    var ds = Ext.getCmp('tabs').getActiveTab().getStore();
    var roomname = Ext.getCmp('tabs').getActiveTab().getId();
    t = "<html><head></head><body>";
    t += "<table cellpadding='2' cellspacing='0' border='1'><tr><th>Roomname</th><th>Date</th><th>Author</th><th>Message</th></tr>";
    for (i=0;i<ds.getCount();i++){
       row = ds.getAt(i);
       t += String.format("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>\r\n", row.get('roomname') || roomname, row.get("ts").format('Y/m/d g:i A'), row.get("author"), row.get("message") );
               }
    t += "</table></body></html>";
    return t;
};

function htmlExport(){
    if (Ext.isIE6 || Ext.isIE7 || Ext.isSafari || Ext.isSafari2 || Ext.isSafari3) {
        Ext.Msg.alert('Status', 'Sorry, this tool does not work with this browser.');
    } else {
        t = grid2html();
        document.location='data:plain/html;base64,' + Base64.encode(t);
    }
};

function showHtmlVersion(){
    var win = new Ext.Window({
        title     : 'Text Version',
        closable  : true,
        width     : 600,
        height    : 350,
        plain     : true,
        autoScroll: true,
        html      : grid2html()
    });
    win.show();
};

/*
 * Important method to add tabs to our display
 */
function addTab(tabid, tabname) {
    /* Make sure we don't already have this tab open */
    var a = Ext.getCmp('tabs').find("id", tabid);
    if (a.length > 0){ 
        Ext.getCmp('tabs').setActiveTab(tabid); 
        return; 
    }

    var jsonurl = '/iembot-json/room/'+ tabid;
    if (cfg.server == "nwschat"){
        jsonurl = '/nwsbot-json/room/'+ tabid +'/'+ cfg.jid +'/'+ cfg.apikey;
    }

    st = new Ext.data.Store({
        roomname   : tabid,
        baseParams : {seqnum:0},
        seqnum     : 0,
        autoLoad   : true,
        proxy      : new Ext.data.HttpProxy({
        url        : jsonurl,
            method : 'GET'
        }),
        reader: new Ext.data.JsonReader({
            root : 'messages',
            id   :'seqnum'
            }, [
                {name: 'seqnum', type: 'int'},
                {name: 'ts', type: 'date', dateFormat: 'Y-m-d h:i:s',
      convert: function(v){ return UTCStringToDate(v, "Y-m-d h:i:s");} },
                {name: 'author'},
                {name: 'message'}
        ])
    });
    st.setDefaultSort('ts', 'DESC');
    /* Need to update the baseParams and turn on the busy sign */
    st.on('beforeload', function(self, options){
        self.baseParams = {'seqnum': self.seqnum};
        Ext.getCmp(self.roomname +"-status").showBusy();
    });
    /* Whew, we got new data to work with */
    st.on('load', function(self, records, idx){
        var nonNWSBot = false;
        for (i=0;i<records.length;i++){
          /* Always update the seqnum number, last is always greatest */
          self.seqnum = records[i].get("seqnum");
          if (records[i].get("author") != "nwsbot"){
             nonNWSBot = true;
          }
        }
        /* If we got new messages, we need to do stuff */
        if (records.length > 0){ 
           /* Resort the display */
           self.applySort(); 
           /* Play a noise! */
           if (audioAlerts.checked && (showNWSBot.checked || nonNWSBot) ){
             soundManager.play('message_new');
           }
           /* Make sure the display refreshes */
           self.fireEvent("datachanged", self);
           /* Change the tab icon, if not active tab */
           if (Ext.getCmp('tabs').getActiveTab() != Ext.getCmp(tabid)){
               Ext.getCmp(tabid).setIconCls('new-tab');
           }
           /* Make sure our requested filters still apply */
           if (showNWSBot.checked){
             self.clearFilter(false);
           } else {
             self.filterBy( myFilter );
           }
        }
        /* Clear the room busy status */
        Ext.getCmp(self.roomname +"-status").clearStatus();
    });

    gp = new Ext.grid.GridPanel({
        reloadable: true,
        viewConfig:{
            onLoad: Ext.emptyFn,
            listeners: {
                beforerefresh: function(v) {
                    v.scrollTop = v.scroller.dom.scrollTop;
                    v.scrollHeight = v.scroller.dom.scrollHeight;
                },
                refresh: function(v) {
                    v.scroller.dom.scrollTop = v.scrollTop + 
        (v.scrollTop == 0 ? 0 : v.scroller.dom.scrollHeight - v.scrollHeight);
                }
            }
        },
        id: tabid,
        title: tabname,
        listeners: LinkInterceptor,
        iconCls:'tabno',
        tbar:[
          new Ext.Button({
            text      :'Clear Room Log',
            cls: 'x-btn-text-icon',
            icon      : 'icons/close.png', 
            listeners : {
              click: function() {
                Ext.getCmp('tabs').getActiveTab().getStore().removeAll();
              }  // End of handler
            }
          }),
          {
            text: 'Export to HTML',
            cls     : 'x-btn-text-icon',
            icon    : 'icons/save.png', 
            handler : htmlExport
          },{
            text: 'Print Log',
            icon: 'icons/print.png',
            cls: 'x-btn-text-icon',
            handler: function(){
                Ext.getCmp("tabs").getActiveTab().getGridEl().print({isGrid: true});
            }
          },
          new Ext.Button({
            text: 'Save Selected',
            icon: 'icons/add.png',
            cls: 'x-btn-text-icon',
            handler: function(){
                ar = Ext.getCmp('tabs').getActiveTab().getSelectionModel().getSelections();
                for (i=0;i<ar.length;i++){
                  record = ar[i];
                  Ext.getCmp('saved').getStore().add(new Ext.data.Record({
                    roomname: Ext.getCmp('tabs').getActiveTab().getId(),
                    ts      : record.get("ts"),
                    author  : record.get("author"),
                    message : record.get("message")
                  })
                  );
                }
                if (ar.length > 0){
                  Ext.getCmp('tabs').setActiveTab(1);
                } else {
                  Ext.Msg.alert('status', 'Please select row(s) first');
                }
             }
          }),
          {
            text   : 'View As HTML',
            handler : showHtmlVersion,
            icon: 'icons/text.png',
            cls: 'x-btn-text-icon'
          },
          new Ext.ux.StatusBar({
            id: tabid+'-status',
            defaultText: ''
          })
        ],
                closable: true,
                store: st,
                columns: [
                  {header:'Timestamp', width: 100, sortable:false,
                   dataIndex: 'ts', renderer: Ext.util.Format.dateRenderer('m/d g:i A')},
                  {header:'Author', width: 100, sortable:false,
                   dataIndex: 'author'},
                  {header:'Message', sortable:false, width: 500,
                   dataIndex: 'message', id: 'message' }
                ],
                autoExpandColumn: 'message',
                stripeRows: true,
                autoScroll:true
    });
    gp.on('activate', function(self){
        self.setIconCls('tabno');
    });
    gp.on('destroy', function(){ saveConfig(); });
    Ext.getCmp('tabs').add(gp);
    Ext.getCmp('tabs').setActiveTab(tabid);
    saveConfig();
}


var roomSelector = new Ext.form.ComboBox({
          store: new Ext.data.SimpleStore({
                    fields: ['roomid', 'roomname'],
                    data : chatdata.rooms
          }),
          valueField:'roomid',
          displayField:'roomname',
  fieldLabel: 'Available Rooms',
  tpl: '<tpl for="."><div class="x-combo-list-item">[{roomid}] {roomname}</div></tpl>',
          typeAhead: true,
          mode: 'local',
          triggerAction: 'all',
          emptyText:'Select a Room...',
          selectOnFocus:true,
          listWidth:180,
          width:180
});
roomSelector.on("select", function(self, record, oldrecord){
  addTab( record.get("roomid"), record.get("roomname") );
});

function myFilter(record,id){
  if (record.get("author") == "nwsbot"){ return false;}
  return true;
};

var saved = new Ext.grid.GridPanel({
    reloadable       : false,
    id               : 'saved',
    title            : 'Saved Items',
    store            : new Ext.data.SimpleStore({
        fields: [
          {name:'roomname'},
          {name: 'ts', type: 'date', dateFormat: 'Y-m-d h:i:s',
           convert: function(v){ return UTCStringToDate(v, "Y-m-d h:i:s");} },
          {name:'author'},
          {name:'message'}
        ]
    }),
    tbar       : [
        new Ext.Button({
            text:'Clear Room Log',
            icon      : 'icons/close.png', 
            cls: 'x-btn-text-icon',
            listeners: {
              click: function() {
                Ext.getCmp('tabs').getActiveTab().getStore().removeAll();
              }  // End of handler
            }
          }),
          {
            text: 'Export to HTML',
            cls: 'x-btn-text-icon',
            icon    : 'icons/save.png', 
            handler: htmlExport
          },{
            text: 'Print Log',
            icon: 'icons/print.png',
            cls: 'x-btn-text-icon',
            handler: function(){
                Ext.getCmp("tabs").getActiveTab().getGridEl().print({isGrid: true});
            }
          },{
            text   : 'View As HTML',
            handler : showHtmlVersion,
            icon: 'icons/text.png',
            cls: 'x-btn-text-icon'
          }
    ],
    columns    : [
       {header: 'roomname', sortable: true, dataIndex: 'roomname'},
       {header:'Timestamp', width: 100, sortable:false,
        dataIndex: 'ts', renderer: Ext.util.Format.dateRenderer('m/d g:i A')},
       {header: 'author', sortable: true, dataIndex: 'author'},
       {header: 'message', sortable: true, dataIndex: 'message', width: 450}
    ],
    stripeRows: true,
    autoScroll:true
});

var tabPanel = new Ext.TabPanel({
    id:'tabs',
    region:'center',
    plain:true,
    enableTabScroll:true,
    height:.75,
    items:[
      {contentEl:'help', title: 'Help', reloadable: false},
      saved
    ],
    activeTab:0
});

var showNWSBot = new Ext.form.Checkbox({
  boxLabel  : 'Show NWSBot Messages',
  checked   : true,
  hideLabel : true,
  hidden    : (cfg.server == 'iem'),
  handler   : function(cb, checked){
    Ext.getCmp('tabs').items.each( function(c){ 
      if (c.reloadable) { 
        if (checked){
          c.getStore().clearFilter(false);
        } else {
          c.getStore().filterBy( myFilter );
        }
      }
    }); 
  }
});

var audioAlerts = new Ext.form.Checkbox({
  boxLabel: 'Enable Audio Alerts',
  checked: false,
  hideLabel: true
});

var volumeSlider = new Ext.Slider({
  isFormField: true,
  fieldLabel: 'Sound Volume',
  width: 180,
  value: 50,
  plugins: [new Ext.ux.SliderTip()]
});
volumeSlider.on('changecomplete', function(self, val){
  soundManager.setVolume('message_new', val);
  soundManager.play('message_new');
});

var configPanel = new Ext.FormPanel({
    frame      : true,
    labelAlign : 'top',
    items      : [
        roomSelector, 
        showNWSBot,
        audioAlerts,
        new Ext.Button({
            text      : 'Play Test Sound',
            listeners : {
                click: function(){
                    soundManager.play('message_new');
                }
            }
        }),
        volumeSlider
    ]
});



new Ext.Viewport({
    layout:'border',
    items:[
        { 
        region    : 'north',
        height    : 130,
        contentEl : cfg.banner
        },{
        region      : 'west',
        width       : 200,
        collapsible : true,
        margins     : '0 5 0 0',
        title       : 'Options',
        items       : [ configPanel ]
        }, 
        tabPanel
    ]
});

/* Load up tabs from cookie! */
var a = cp.get("nwsbot_tabs", "");
var ar = a.split(",");
for (var i=0; i < ar.length; i++)
{
  if (ar[i] == ""){ continue; }
  addTab( ar[i], roomSelector.getStore().getAt( roomSelector.getStore().find('roomid', ar[i]) ).get("roomname") );
}
/* Load up tables from URL! */
var tokens = window.location.href.split('#');
if (tokens.length == 2){
   var subtokens = tokens[1].split(",");
   for (i=0; i < subtokens.length; i++)
   {
       addTab( subtokens[i], roomSelector.getStore().getAt( roomSelector.getStore().find('roomid', subtokens[i]) ).get("roomname") );

   }
} 


var task = {
  run: function(){
    Ext.getCmp('tabs').items.each( function(c){ 
      if (c.reloadable) { 
       c.getStore().reload({add:true});
      } 
    });
  },
  interval: 7000
}
Ext.TaskMgr.start(task);

// End of static.js
});
