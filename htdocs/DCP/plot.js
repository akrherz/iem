Ext.BLANK_IMAGE_URL = '/vendor/ext/3.4.1/resources/images/default/s.gif';

Ext.override(Ext.form.ComboBox, {
    doQuery: function (q, forceAll) {
        if (q === undefined || q === null) {
            q = '';
        }
        var qe = {
            query: q,
            forceAll: forceAll,
            combo: this,
            cancel: false
        };
        if (this.fireEvent('beforequery', qe) === false || qe.cancel) {
            return false;
        }
        q = qe.query;
        forceAll = qe.forceAll;
        if (forceAll === true || (q.length >= this.minChars)) {
            if (this.lastQuery !== q) {
                this.lastQuery = q;
                if (this.mode == 'local') {
                    this.selectedIndex = -1;
                    if (forceAll) {
                        this.store.clearFilter();
                    } else {
                        this.store.filter(this.displayField, q, true);
                    }
                    this.onLoad();
                } else {
                    this.store.baseParams[this.queryParam] = q;
                    this.store.load({
                        params: this.getParams(q)
                    });
                    this.expand();
                }
            } else {
                this.selectedIndex = -1;
                this.onLoad();
            }
        }
    }
});


Ext.onReady(function () {

    var states = [
        ["AL", "Alabama"],
        ["AK", "Alaska"],
        ["AZ", "Arizona"],
        ["AR", "Arkansas"],
        ["CA", "California"],
        ["CO", "Colorado"],
        ["CT", "Connecticut"],
        ["DE", "Delaware"],
        ["FL", "Florida"],
        ["GA", "Georgia"],
        ["HI", "Hawaii"],
        ["ID", "Idaho"],
        ["IL", "Illinois"],
        ["IN", "Indiana"],
        ["IA", "Iowa"],
        ["KS", "Kansas"],
        ["KY", "Kentucky"],
        ["LA", "Louisiana"],
        ["ME", "Maine"],
        ["MD", "Maryland"],
        ["MA", "Massachusetts"],
        ["MI", "Michigan"],
        ["MN", "Minnesota"],
        ["MS", "Mississippi"],
        ["MO", "Missouri"],
        ["MT", "Montana"],
        ["NE", "Nebraska"],
        ["NV", "Nevada"],
        ["NH", "New Hampshire"],
        ["NJ", "New Jersey"],
        ["NM", "New Mexico"],
        ["NY", "New York"],
        ["NC", "North Carolina"],
        ["ND", "North Dakota"],
        ["OH", "Ohio"],
        ["OK", "Oklahoma"],
        ["OR", "Oregon"],
        ["PA", "Pennsylvania"],
        ["RI", "Rhode Island"],
        ["SC", "South Carolina"],
        ["SD", "South Dakota"],
        ["TN", "Tennessee"],
        ["TX", "Texas"],
        ["UT", "Utah"],
        ["VT", "Vermont"],
        ["VA", "Virginia"],
        ["WA", "Washington"],
        ["WV", "West Virginia"],
        ["WI", "Wisconsin"],
        ["WY", "Wyoming"]
    ];

    var varStore = new Ext.data.Store({
        autoLoad: false,
        proxy: new Ext.data.HttpProxy({
            url: '/json/dcp_vars.php'
        }),
        reader: new Ext.data.JsonReader({
            root: 'vars',
            id: 'id'
        }, [
            { name: 'id', mapping: 'id' }
        ]),
        listeners: {
            load: function (st, records) {
                if (records.length == 0) {
                    Ext.get('msg').update('Sorry, did not find any variables for this site!');
                } else {
                    Ext.get('msg').update('');
                }
            }
        }
    });

    var varCB = new Ext.form.ComboBox({
        store: varStore,
        displayField: 'id',
        valueField: 'id',
        width: 100,
        mode: 'local',
        fieldLabel: 'Variable',
        emptyText: 'Select Variable...',
        tpl: new Ext.XTemplate(
            '<tpl for="."><div class="search-item">',
            '<span>[{id}]</span>',
            '</div></tpl>'
        ),
        typeAhead: false,
        itemSelector: 'div.search-item',
        hideTrigger: false
    });
    var stationStore = new Ext.data.Store({
        autoLoad: false,
        proxy: new Ext.data.HttpProxy({
            url: '/json/network.php'
        }),
        baseParams: { 'network': 'IA_DCP' },
        reader: new Ext.data.JsonReader({
            root: 'stations',
            id: 'id'
        }, [
            { name: 'id', mapping: 'id' },
            { name: 'name', mapping: 'name' },
            { name: 'combo', mapping: 'combo' }
        ])
    });

    var stateCB = new Ext.form.ComboBox({
        hiddenName: 'state',
        store: new Ext.data.SimpleStore({
            fields: ['abbr', 'name'],
            data: states
        }),
        valueField: 'abbr',
        width: 180,
        fieldLabel: 'Select State',
        displayField: 'name',
        typeAhead: true,
        tpl: '<tpl for="."><div class="x-combo-list-item">[{abbr}] {name}</div></tpl>',
        mode: 'local',
        triggerAction: 'all',
        emptyText: 'Select/or type here...',
        selectOnFocus: true,
        lazyRender: true,
        id: 'stateselector',
        listeners: {
            select: function (cb, record, idx) {
                stationStore.load({ add: false, params: { network: record.data.abbr + "_DCP" } });
                return false;
            }
        }
    });


    var stationCB = new Ext.form.ComboBox({
        store: stationStore,
        displayField: 'combo',
        valueField: 'id',
        width: 300,
        mode: 'local',
        triggerAction: 'all',
        fieldLabel: 'Station',
        emptyText: 'Select Station...',
        tpl: new Ext.XTemplate(
            '<tpl for="."><div class="search-item">',
            '<span>[{id}] {name}</span>',
            '</div></tpl>'
        ),
        typeAhead: false,
        itemSelector: 'div.search-item',
        hideTrigger: false,
        listeners: {
            select: function (cb, record, idx) {
                varStore.load({ add: false, params: { station: record.id } });
                return false;
            }
        }
    });
    var datepicker = new Ext.form.DateField({
        minValue: new Date('1/1/2002'),
        maxValue: new Date(),
        fieldLabel: 'Start Date',
        emptyText: "Select Date",
        allowBlank: false
    });
    var dayInterval = new Ext.form.NumberField({
        minValue: 1,
        maxValue: 31,
        value: 5,
        width: 30,
        fieldLabel: 'Number of Days'
    });

    function updateImage() {
        var ds = datepicker.getValue();
        var ds2 = ds.add(Date.DAY, dayInterval.getValue());
        var url = String.format('plot.php?station={0}&sday={1}&eday={2}&var={3}',
            stationCB.getValue(), ds.format('Y-m-d'),
            ds2.format('Y-m-d'), varCB.getValue());
        Ext.get("imagedisplay").dom.src = url;
        /* Now adjust the URL */
        var uri = String.format('#{0}.{1}.{2}.{3}.{4}', stateCB.getValue(), stationCB.getValue(),
            varCB.getValue(), ds.format('Y-m-d'),
            dayInterval.getValue());
        window.location.href = uri;

    }

    new Ext.form.FormPanel({
        applyTo: 'myform',
        labelAlign: 'top',
        width: 320,
        style: 'padding-left: 5px;',
        title: 'Make Plot Selections Below...',
        items: [stateCB, stationCB, varCB, datepicker, dayInterval],
        buttons: [{
            text: 'Create Graph',
            handler: function () {
                updateImage();

            }
        }]

    });
    /* Check to see if we had something specified on the URL! */
    var tokens = window.location.href.split('#');
    if (tokens.length == 2) {
        var tokens2 = tokens[1].split('.');
        if (tokens2.length == 5) {
            stateCB.setValue(tokens2[0]);
            stationCB.setValue(tokens2[1]);
            varCB.setValue(tokens2[2]);
            datepicker.setValue(tokens2[3]);
            dayInterval.setValue(tokens2[4]);
            updateImage();
        }
    }
});