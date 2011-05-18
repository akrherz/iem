Ext.BLANK_IMAGE_URL = '../ext/resources/images/default/s.gif';

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


Ext.override(Ext.form.ComboBox, {
	doQuery : function(q, forceAll){
		if(q === undefined || q === null){
			q = '';
	}
	var qe = {
		query: q,
		forceAll: forceAll,
		combo: this,
		cancel:false
	};
	if(this.fireEvent('beforequery', qe)===false || qe.cancel){
		return false;
	}
	q = qe.query;
	forceAll = qe.forceAll;
	if(forceAll === true || (q.length >= this.minChars)){
	if(this.lastQuery !== q){
	this.lastQuery = q;
	if(this.mode == 'local'){
		this.selectedIndex = -1;
		if(forceAll){
			this.store.clearFilter();
		}else{
			this.store.filter(this.displayField, q, true);
		}
		this.onLoad();
	}else{
		this.store.baseParams[this.queryParam] = q;
		this.store.load({
			params: this.getParams(q)
		});
		this.expand();
	}
	}else{
		this.selectedIndex = -1;
		this.onLoad();
	}
	}
	}
});

states = [
 ["AL","Alabama"],
 ["AK","Alaska"],
 ["AZ","Arizona"],
 ["AR","Arkansas"],
 ["CA","California"],
 ["CO","Colorado"],
 ["CT","Connecticut"],
 ["DE","Delaware"],
 ["FL","Florida"],
 ["GA","Georgia"],
 ["HI","Hawaii"],
 ["ID","Idaho"],
 ["IL","Illinois"],
 ["IN","Indiana"],
 ["IA","Iowa"],
 ["KS","Kansas"],
 ["KY","Kentucky"],
 ["LA","Louisiana"],
 ["ME","Maine"],
 ["MD","Maryland"],
 ["MA","Massachusetts"],
 ["MI","Michigan"],
 ["MN","Minnesota"],
 ["MS","Mississippi"],
 ["MO","Missouri"],
 ["MT","Montana"],
 ["NE","Nebraska"],
 ["NV","Nevada"],
 ["NH","New Hampshire"],
 ["NJ","New Jersey"],
 ["NM","New Mexico"],
 ["NY","New York"],
 ["NC","North Carolina"],
 ["ND","North Dakota"],
 ["OH","Ohio"],
 ["OK","Oklahoma"],
 ["OR","Oregon"],
 ["PA","Pennsylvania"],
 ["RI","Rhode Island"],
 ["SC","South Carolina"],
 ["SD","South Dakota"],
 ["TN","Tennessee"],
 ["TX","Texas"],
 ["UT","Utah"],
 ["VT","Vermont"],
 ["VA","Virginia"],
 ["WA","Washington"],
 ["WV","West Virginia"],
 ["WI","Wisconsin"],
 ["WY","Wyoming"]
];

Ext.onReady(function(){
	var eventStore = new Ext.data.Store({
		autoLoad	: false,
        proxy	: new Ext.data.HttpProxy({
            url     : 'events.php'
        }),
        baseParams  : {'ugc': 'IAC001'},
        reader: new Ext.data.JsonReader({
            root: 'events',
            id: 'id'
        }, [
            {name: 'id', mapping: 'id'},
            {name: 'eventid', type:'float'},
            {name: 'phenomena'},
            {name: 'significance'},
            {name: 'expire', type:'date', dateFormat: 'Y-m-d H:i'},
            {name: 'issue',  type:'date', dateFormat: 'Y-m-d H:i'}
        ])
    });
    
	var ugcStore = new Ext.data.Store({
		autoLoad	: false,
        proxy	: new Ext.data.HttpProxy({
            url     : '../json/state_ugc.php'
        }),
        baseParams  : {'state': 'IA'},
        reader: new Ext.data.JsonReader({
            root: 'ugcs',
            id: 'ugc'
        }, [
            {name: 'ugc', mapping: 'ugc'},
            {name: 'name', mapping: 'name'}
        ])
    });
    
    var ugcCB = new Ext.form.ComboBox({
		store			: ugcStore,
		displayField	: 'combo',
		valueField		: 'ugc',
		width			: 300,
		mode			: 'local',
		triggerAction	: 'all',
		fieldLabel		: 'County/Zone',
		emptyText		: 'Select County/Zone...',
		tpl				: new Ext.XTemplate(
		        '<tpl for="."><div class="search-item">',
	            '<span>[{ugc}] {name}</span>',
	        '</div></tpl>'
	    ),
	    typeAhead		: false,
	    itemSelector	: 'div.search-item',
		hideTrigger		: false,
	    listeners		: {
			select: function(cb, record, idx){
				eventStore.load({add: false, params: {ugc: record.id}});
				return false;
      		}
		}
	});
	
		var stateCB = new Ext.form.ComboBox({
  		hiddenName	: 'state',
  		store		: new Ext.data.SimpleStore({
           fields: ['abbr', 'name'],
           data : states
  		}),
  		valueField	: 'abbr',
  		width		: 180,
  		fieldLabel	: 'Select State',
  		displayField: 'name',
  		typeAhead	: true,
  		tpl			: '<tpl for="."><div class="x-combo-list-item">[{abbr}] {name}</div></tpl>',
  		mode		: 'local',
  		triggerAction: 'all',
  		emptyText	:'Select/or type here...',
  		selectOnFocus:true,
  		lazyRender	: true,
  		id			: 'stateselector',
  		listeners	: {
				select: function(cb, record, idx){
					ugcStore.load({add: false, params: {state: record.data.abbr }});
					return false;
      		}
		}
	});
	
		var form = new Ext.form.FormPanel({
		applyTo		: 'myform',
		labelAlign	: 'top',
		width		: 320,
		style		: 'padding-left: 5px;',
		title		: 'Make Plot Selections Below...',
		items		: [stateCB, ugcCB],
		buttons		: [{
			text	: 'Create Graph',
			handler	: function(){
				updateImage();
				
			}
		}]
	
	});
	
	var gp = new Ext.grid.GridPanel({
		height : 500,
		width : 500,
		title : 'Events Listing',
		loadMask   : {msg:'Loading Data...'},
		store : eventStore,
		tbar : [{
			xtype : 'textfield',
			size : 50 
		},{
			xtype : 'button',
			text : 'Search!',
			handler : function(btn){
				alert( btn.ownerCt.items.items[0].getValue() );
			}
		}],
		columns : [
		{'header': 'Event ID', dataIndex: 'eventid'},
		{'header': 'Phenomena', dataIndex: 'phenomena'},
		{'header': 'Significance', dataIndex: 'significance'},
		{'header': 'Issued', dataIndex: 'issue', renderer  : function(value){
                return value.fromUTC().format('Y-m-d g:i A');
            }},
		{'header': 'Expired', dataIndex: 'expire', renderer  : function(value){
                return value.fromUTC().format('Y-m-d g:i A');
            }}
		]
	});
	gp.render('mytable');
	
});