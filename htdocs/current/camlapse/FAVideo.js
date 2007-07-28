/**************************************************************************************************
BSD License
The BSD License (http://www.opensource.org/licenses/bsd-license.php) specifies the terms and
conditions of use for FAVideo:

Copyright (c) 2007. Adobe Systems Incorporated.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

  ¥ Redistributions of source code must retain the above copyright notice, this list of conditions
    and the following disclaimer.
  ¥ Redistributions in binary form must reproduce the above copyright notice, this list of
    conditions and the following disclaimer in the documentation and/or other materials provided
	with the distribution.
  ¥ Neither the name of Adobe Systems Incorporated nor the names of its contributors may be used
    to endorse or promote products derived from this software without specific prior written
	permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIESOF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


For more information and updates for FAVideo, please visit:
http://www.adobe.com/go/favideo/
**************************************************************************************************/

/* ----------------------------------------------------
 * FAVideo system
 *
 * This system provide a simple method for embedding and controlling Flash video through Javascript.
 *
 * Dependencies:
 * - Requires AC_RunActiveContent.js
 *----------------------------------------------------- */


/* ----------------------------------------------------
 * FAVideo
 *
 * FAVideo represents a video player instance on the page. It allows you to instantiate, control,
 * and listen to events from a Flash video player through Javascript.
 *----------------------------------------------------- */
	FAVideo = function(divName, videoPath, width, height, options) {
		this.DEFAULT_SWF_PATH = "FAVideo"; // dot swf is added by AC_RunActiveContent
		this.DEFAULT_SKIN_PATH = "skins/ClearOverAll.swf";
		this.DEFAULT_WIDTH = 320;
		this.DEFAULT_HEIGHT = 240;
		this.ERROR_DIV_NOT_FOUND = "The specified DIV element was not found.";
		
		//this.DEFAULT_SKIN_PATH = "skins/ClearExternalAll.swf";
		
		this.id = FAVideoManagerInstance.addPlayer(this); // Manager manages multiple players
		this.rendered = false;
		this.inited = false;
		
		// Div name, flash name, and container name
		this.divName = divName;
		this.name = "FAVideo_" + divName;
		
		// Video props
		this.videoPath = videoPath;
		this.width = (width > 0) ? width : this.DEFAULT_WIDTH;
		this.height = (height > 0) ? height : this.DEFAULT_HEIGHT;
		
		// Initialize player
		this.player = null;
		this.initProperties();
		this.setOptions(options);
		this.createPlayer();
		this.render();
	}

/* ----------------------------------------------------
 * Public API methods
 *----------------------------------------------------- */
	/**
	 * Play an FLV.  Sets autoPlay to true.
	 * 
	 * @param videoPath Path to the FLV. If the videoPath is null, and the FLV is playing, it will act as a play/pause toggle.
	 * @param totalTime Optional totalTime to override the FLV's built in totalTime
	 */
	FAVideo.prototype.play = function(videoPath, totalTime) {
		this.autoPlay = true;
		if (totalTime != null) { this.setTotalTime(totalTime); }
		if (videoPath != null) { this.videoPath = videoPath; }
		if (this.videoPath == null && !this.firstLoad) { 
			this.dispatchEvent({type:"error", error:"FAVideo::play - No videoPath has been set."});
			return;
		}
		if (videoPath == null && this.firstLoad && !this.autoLoad) { // Allow play(null) to toggle playback 
			videoPath = this.videoPath;
		}
		this.firstLoad = false;
		this.callMethod("playVideo", videoPath, totalTime);	
	}
	
	/**
	 * Load a video.  Sets autoPlay to false.
	 *
	 * @param videoPath Path the the FLV.
	 */
	FAVideo.prototype.load = function(videoPath) {
		if (videoPath != null) { this.videoPath = videoPath; }
		if (this.videoPath == null) { 
			this.dispatchEvent({type:"error", error:"FAVideo::loadVideo - No videoPath has been set."});
			return;
		}
		this.firstLoad = false;
		this.autoPlay = false;
		this.callMethod("loadVideo", this.videoPath);
	}
	
	/**
	 * Toggle the pause state of the video.
	 *
	 * @param pauseState The pause state. Setting pause state to true will pause the video.
	 */
	FAVideo.prototype.pause = function(pauseState) {
		this.callMethod("pause", pauseState);
	}
	
	/**
	 * Stop playback of the video.
	 */
	FAVideo.prototype.stop = function() {
		this.callMethod("stop");
	}
	
	/**
	 * Seek the video to a specific position.
	 *
	 * @param seconds The number of seconds to seek the playhead to.
	 */
	FAVideo.prototype.seek = function(seconds) {
		this.callMethod("seek", seconds);
	}
	
	/**
	 * Set the size of the video.
	 *
	 * @param width The width of the video.
	 * @param height The height of the video.
	 */	
	FAVideo.prototype.setSize = function(width, height) {
		this.width = width;
		this.height = height;
		// Change the DOM.  Do not rerender.
		this.container.style.width = this.width + "px";
		this.container.style.height = this.height + "px";
		this.callMethod("setSize", this.width, this.height);
	}
	
	/**
	 * Add an event listener to the video.
	 *
	 * @param eventType A string representing the type of event.  e.g. "init"
	 * @param object The scope of the listener function (usually "this").
	 * @param function The function to be called when the event is dispatched.
	 */
	FAVideo.prototype.addEventListener = function(eventType, object, functionRef) {
		if (this.listeners == null) {
			this.listeners = {};
		}
		if (this.listeners[eventType] == null) {
			this.listeners[eventType] = [];
		} else {
			this.removeEventListener(eventType, object, functionRef);
		}
		this.listeners[eventType].push({target:object, func:functionRef});
	}
	
	/**
	 * Remove an event listener from the video.
	 *
	 * @param eventType A string representing the type of event.  e.g. "init"
	 * @param object The scope of the listener function (usually "this").
	 * @param functionRef The function to be called when the event is dispatched.
	 */
	FAVideo.prototype.removeEventListener = function(eventType, object, functionRef) {
		for (var i=0; i<this.listeners[eventType].length; i++) {
			var listener = this.listeners[eventType][i];
			if (listener.target == object && listener.func == functionRef) {
				this.listeners[eventType].splice(i, 1);
				break;
			}
		}
	}


/* ----------------------------------------------------
 * Public API property access methods
 *----------------------------------------------------- */
 	/**
	 * The volume of the player, from 0 to 100.
	 * @default 50
	 */
	FAVideo.prototype.getVolume = function() { return this.volume; }
	FAVideo.prototype.setVolume = function(value) {
		this.setProperty("volume", value);
	}
	
 	/**
	 * Specified whether the video begins playback when loaded.
	 * @default true
	 */
	FAVideo.prototype.getAutoPlay = function() { return this.autoPlay; }
	FAVideo.prototype.setAutoPlay = function(value) {
		this.setProperty("autoPlay", value);
	}
	
 	/**
	 * Specifies if the video toggles playback when the video is clicked.
	 * @default true
	 */
	FAVideo.prototype.getClickToTogglePlay = function() { return this.clickToTogglePlay; }
	FAVideo.prototype.setClickToTogglePlay = function(value) {
		this.setProperty("clickToTogglePlay", value);
	}
	
 	/**
	 * Specifies if the video automatically loads when the player is initialized with a videoPath.
	 * @default true
	 */
	FAVideo.prototype.getAutoLoad = function() { return this.autoLoad; }
	FAVideo.prototype.setAutoLoad = function(value) {
		this.setProperty("autoLoad", value);
	}
	
 	/**
	 * Determines if the flash controls hide when the user is idle.
	 * @default true
	 */
	FAVideo.prototype.getSkinAutoHide = function() { return this.skinAutoHide; }
	FAVideo.prototype.setSkinAutoHide = function(value) { 
		this.setProperty("skinAutoHide", value);
	}
	
 	/**
	 * Determines if the flash controls are visible.
	 * @default false
	 */
	FAVideo.prototype.getSkinVisible = function() { return this.skinVisible; }
	FAVideo.prototype.setSkinVisible = function(value) { 
		this.setProperty("skinVisible", value);
	}
	
 	/**
	 * Specifies the position of the playhead, in seconds.
	 * @default null
	 */
	FAVideo.prototype.getPlayheadTime = function() { return this.playheadTime; }
	FAVideo.prototype.setPlayheadTime = function(value) {
		this.setProperty("playheadTime", value);
	}
	
 	/**
	 * Determines the total time of the video.  The total time is automatically determined
	 * by the player, unless the user overrides it.
	 * @default null
	 */
	FAVideo.prototype.getTotalTime = function() { return this.totalTime; }
	FAVideo.prototype.setTotalTime = function(value) {
		this.setProperty("totalTime", value);
	}
	
 	/**
	 * Specifies the number of seconds the video requires in the buffer to keep playing.
	 * @default 0.1
	 */
	FAVideo.prototype.getBufferTime = function() { return this.bufferTime; }
	FAVideo.prototype.setBufferTime = function(value) {
		this.setProperty("bufferTime", value);
	}
	
 	/**
	 * Determines how videos are scaled.  Valid values are "maintainAspectRatio", "noScale", and "fitToWindow"
	 * @default "maintainAspectRatio"
	 */
	FAVideo.prototype.getVideoScaleMode = function() { return this.videoScaleMode; }
	FAVideo.prototype.setVideoScaleMode = function(value) {
		this.setProperty("videoScaleMode", value);
	}
	
 	/**
	 * Determines how videos are aligned in the player when the player dimensions exceed the 
	 * video dimensions on either axis.
	 * @default "center"
	 */
	FAVideo.prototype.getVideoAlign = function() { return this.videoAlign; }
	FAVideo.prototype.setVideoAlign = function(value) {
		this.setProperty("videoAlign", value);
	}
	
 	/**
	 * Specifies how often the video playhead is updated.  The updateInterval also affects how
	 * often playheadUpdate events are dispatched from the video player. In milliseconds.
	 * @default 1000
	 */
	FAVideo.prototype.getPlayheadUpdateInterval = function() { return this.playheadUpdateInterval; }
	FAVideo.prototype.setPlayheadUpdateInterval = function(value) {
		this.setProperty("playheadUpdateInterval", value);
	}
	
 	/**
	 * Specifies a preview image that is used when autoLoad is set to false.
	 * @default null
	 */
	FAVideo.prototype.getPreviewImagePath = function() { return this.previewImagePath; }
	FAVideo.prototype.setPreviewImagePath = function(value) {
		this.setProperty("previewImagePath", value);	
	}
	
	/**
	 * Specify a theme color
	 * @default null
	 */
	FAVideo.prototype.getThemeColor = function() { return this.themeColor; }
	FAVideo.prototype.setThemeColor = function(value) {
		this.setProperty("themeColor", value);	
	}
	
	/**
	 * Set a path for the flash video controls.
	 * @default "skins/ClearOverAll.swf"
	 */
	FAVideo.prototype.getSkinPath = function() { return this.skinPath; }
	FAVideo.prototype.setSkinPath = function(value) {
		this.setProperty("skinPath", value);	
	}
	
/**
 * Events dispatched by FAVideo instances
 *	> init: The player is initialized
 *	> ready: The video is ready
 *	> progress: The video is downloading. Properties: bytesLoaded, bytesTotal
 *	> playHeadUpdate: The video playhead has moved.  Properties: playheadTime, totalTime
 *	> stateChange: The state of the video has changed. Properties: state
 *	> change: The player has changed.
 *	> complete: Playback is complete.
 *	> metaData: The video has returned meta-data. Properties: infoObject
 *	> cuePoint: The video has passed a cuePoint. Properties: infoObject
 *	> error: An error has occurred.  Properties: error
 */


/* ----------------------------------------------------
 * Callbacks from flash
 *----------------------------------------------------- */
	FAVideo.prototype.update = function(props) {
		for (var n in props) {	
			this[n] = props[n]; // Set the internal property
		}
		props.type = "change";
		this.dispatchEvent(props); // This needs to have an array of changed props.
	}

	FAVideo.prototype.event = function(eventName, evtObj) {
		switch (eventName) {
			case "progress":
				this.bytesLoaded = evtObj.bytesLoaded;
				this.bytesTotal = evtObj.bytesTotal;
				this.dispatchEvent({type:"progress", bytesLoaded:this.bytesLoaded, bytesTotal:this.bytesTotal});
				break;
				
			case "playheadUpdate":
				this.playheadTime = evtObj.playheadTime;
				this.totalTime = evtObj.totalTime;
				this.dispatchEvent({type:"playheadUpdate", playheadTime:this.playheadTime, totalTime:this.totalTime});
				break;
				
			case "stateChange":
				this.state = evtObj.state;
				this.dispatchEvent({type:"stateChange", state:this.state});
				break;
				
			case "change":
				this.dispatchEvent({type:"change"});
				break;
			
			case "complete":
				this.dispatchEvent({type:"complete"});
				break;
				
			case "ready":
				this.dispatchEvent({type:"ready"});
				break;
				
			case "metaData":
				this.dispatchEvent({type:"metaData", infoObject:evtObj});
				break;
				
			case "cuePoint":
				this.dispatchEvent({type:"cuePoint", infoObject:evtObj});
				break;
				
			case "init":
				this.inited = true;
				this.callMethod("setSize", this.width, this.height); // There is a bug in IE innerHTML. Tell flash what size it is.  This will probably not work with liquid layouts in IE.
				this.invalidateProperty("clickToTogglePlay", "skinVisible", "skinAutoHide", "autoPlay", "autoLoad", "volume", "bufferTime", "videoScaleMode", "videoAlign", "playheadUpdateInterval", "skinPath", "previewImagePath");
				this.validateNow();
				this.makeDelayCalls();
				if (this.autoPlay) {
					this.play(this.videoPath);
				} else if (this.autoLoad) {
					this.load(this.videoPath);
				}
				
				this.dispatchEvent({type:"init"});
				break;
		}
	}

/* ----------------------------------------------------
 * Initialization methods
 *----------------------------------------------------- */
	FAVideo.prototype.render = function() {
		var div = this.getElement(this.divName);
		if (div == null) {
			return;
		}
		this.pluginError = false;
		div.innerHTML = this.content;
		
		this.player = this.getElement(this.name);
		this.container = this.getElement(this.name + "_Container");		
		this.rendered = true;
	}
	
	FAVideo.prototype.setOptions = function(options) {
		if (options == null) { return; }
		// Create a hash of acceptable properties
		var hash = ["volume", "skinAutoHide", "skinVisible", "autoPlay","clickToTogglePlay","autoLoad","playHeadTime","totalTime","bufferTime","videoScaleMode","videoAlign","playheadUpdateInterval","skinPath","previewImagePath"];
		for (var i=0;i<hash.length;i++) {
			var prop = hash[i];
			if (options[prop] == null) { continue; }
			this.setProperty(prop, options[prop]);
		}
	}
	
	// Mark out the properties, so they are initialized, and documented.
	FAVideo.prototype.initProperties = function() {
		this.delayCalls = [];
		
		// Properties set by flash player
		this.videoWidth = 0;
		this.videoHeight = 0;
		this.totalTime = 0;
		this.bytesLoaded = 0;
		this.bytesTotal = 0;
		this.state = null;
		
		// Internal properties that match get/set methods
		this.volume = 50;
		this.clickToTogglePlay = true;
		this.autoPlay = true;
		this.autoLoad = true;
		this.skinAutoHide = false;
		this.skinVisible = true;
		this.skinPath = this.DEFAULT_SKIN_PATH;
		this.playheadTime = null;
		this.bufferTime = 0.1;
		this.videoScaleMode = "maintainAspectRatio"; // Also "noScale", "fitToWindow"
		this.videoAlign = "center";
		this.playheadUpdateInterval = 1000;
		this.previewImagePath = null;
		this.themeColor = null
		
		this.firstLoad = true;
		this.pluginError = false;
	}
	
	// Create the HTML to render the player.
	FAVideo.prototype.createPlayer = function() {
		this.requiredMajorVersion = 8;
		this.requiredMinorVersion = 0;
		this.requiredRevision = 0;
		this.content = "";
		var flash = "";
		var hasProductInstall = DetectFlashVer(6, 0, 65);
		var hasRequestedVersion = DetectFlashVer(this.requiredMajorVersion, this.requiredMinorVersion, this.requiredRevision);		
		if (hasProductInstall && !hasRequestedVersion ) {
			var MMPlayerType = (isIE == true) ? "ActiveX" : "PlugIn";
			var MMredirectURL = window.location;
			document.title = document.title.slice(0, 47) + " - Flash Player Installation";
			var MMdoctitle = document.title;
			
			flash = this.AC_FL_RunContent(
				"src", "playerProductInstall",
				"FlashVars", "MMredirectURL="+MMredirectURL+"&MMplayerType="+MMPlayerType+"&MMdoctitle="+MMdoctitle+"",
				"width", "100%",
				"height", "100%",
				"align", "middle",
				"id", this.name,
				"quality", "high",
				"bgcolor", "#000000",
				"name", this.name,
				"allowScriptAccess","always",
				"type", "application/x-shockwave-flash",
				"pluginspage", "http://www.adobe.com/go/getflashplayer"
			);
		} else if (hasRequestedVersion) {
			flash = this.AC_FL_RunContent(
				"src", this.DEFAULT_SWF_PATH,
				"width", "100%",
				"height", "100%",
				"align", "middle",
				"id", this.name,
				"quality", "high",
				"bgcolor", "#000000",
				"allowFullScreen", "true", 
				"name", this.name,
				"flashvars","playerID="+this.id+"&initialVideoPath="+this.videoPath,
				"allowScriptAccess","always",
				"type", "application/x-shockwave-flash",
				"pluginspage", "http://www.adobe.com/go/getflashplayer",
				"menu", "true"
			);
		} else {
			flash = "This content requires the <a href=http://www.adobe.com/go/getflash/>Adobe Flash Player</a>.";
			this.pluginError = true;
		}
	
		this.content = "<div id='" + this.name + "_Container" + "' class='FAVideo' style='width:"+this.width+"px;height:"+this.height+"px;'>" + flash + "</div>";
		return this.content;
	}
	
	
/* ----------------------------------------------------
 * Utility methods
 *----------------------------------------------------- */
	FAVideo.prototype.getElement = function(id) {
		var elem;
	   
	   if (navigator.appName.indexOf("Microsoft") != -1) {
			return window[id]
		} else {
			if (document[id]) {
				elem = document[id];
			} else {
				elem = document.getElementById(id);
			}
			return elem;
		}
	}
	
	// Mark a property as invalid, and create a timeout for redraw
	FAVideo.prototype.invalidateProperty = function() {
		if (this.invalidProperties == null) {
			this.invalidProperties = {};
		}
		for (var i=0; i<arguments.length; i++) {
			this.invalidProperties[arguments[i]] = true;
		}
		
		if (this.validateInterval == null && this.inited) {
			var _this = this;
			this.validateInterval = setTimeout(function() { _this.validateNow(); }, 100);
		}
	}
	
	// Updated player with properties marked as invalid.
	FAVideo.prototype.validateNow = function() {
		this.validateInterval = null;
		var props = {};
		for (var n in this.invalidProperties) { props[n] = this[n]; }
		this.invalidProperties = {};
		this.player.callMethod("update", props);
	}
		
	// All public methods use this proxy to make sure that methods called before
	// initialization are properly called after the player is ready.
	FAVideo.prototype.callMethod = function(param1, param2, param3) {
		if (this.inited) {
			this.player.callMethod(param1, param2, param3); // function.apply does not work on the flash object
		} else {
			this.delayCalls.push(arguments);
		}
	}
	
	// Call methods that were made before the player was initialized.
	FAVideo.prototype.makeDelayCalls = function() {
		for (var i=0; i<this.delayCalls.length; i++) {
			this.callMethod.apply(this, this.delayCalls[i]);
		}
	}
	
	// All public properties use this proxy to minimize player updates
	FAVideo.prototype.setProperty = function(property, value) {
		this[property] = value; // Set the internal property
		if (this.inited) {
			this.invalidateProperty(property);
		} // Otherwise, it is already invalidated on init.
	}
	
	// Notify all listeners when a new event is dispatched.
	FAVideo.prototype.dispatchEvent = function(eventObj) {
		if (this.listeners == null) { return; }
		var type = eventObj.type;
		var items = this.listeners[type];
		if (items == null) { return; }
		for (var i=0; i<items.length; i++) {
			var item = items[i];
			item.func.apply(item.target, [eventObj]);
		}
	}

/* ----------------------------------------------------
 * Include ActiveContent methods that we need to
 * override. Avoids collision with the default file
 *----------------------------------------------------- */
	FAVideo.prototype.AC_Generateobj = function(objAttrs, params, embedAttrs) { 
		var str = '';
		if (isIE && isWin && !isOpera) {
			str += '<object ';
			for (var i in objAttrs) {
				str += i + '="' + objAttrs[i] + '" ';
			}
			str += '>';
			for (var i in params) {
				str += '<param name="' + i + '" value="' + params[i] + '" /> ';
			}
			str += '</object>';
		} else {
			str += '<embed ';
			for (var i in embedAttrs) {
				str += i + '="' + embedAttrs[i] + '" ';
			}
			str += '> </embed>';
		}
		return str; // Instead of document.write
	}
	
	FAVideo.prototype.AC_FL_RunContent = function() {
		var ret = AC_GetArgs(arguments, ".swf", "movie", "clsid:d27cdb6e-ae6d-11cf-96b8-444553540000", "application/x-shockwave-flash");
		return this.AC_Generateobj(ret.objAttrs, ret.params, ret.embedAttrs);
	}
	
	
	


/* ----------------------------------------------------
 * FAVideoManager
 *
 * This manages the collection of FAVideo instances on the HTML page. It directs calls from embedded
 * FAVideo SWFs to the appropriate FAVideo instance in Javascript.
 *----------------------------------------------------- */
	FAVideoManager = function() {
		hash = {};
		uniqueID = 1;
	}
	
	FAVideoManager.prototype.addPlayer = function(player) {
		hash[++uniqueID] = player;
		return uniqueID;
	}
	
	FAVideoManager.prototype.getPlayer = function(id) {
		return hash[id];
	}
	
	FAVideoManager.prototype.callMethod = function(id, methodName) {
		var player = FAVideoManagerInstance.getPlayer(id);
		if (player == null) { alert("Player with id: " + id + " not found"); }
		if (player[methodName] == null) { alert("Method " + methodName + " Not found"); }
		
		// Unable to use slice on arguments in some browsers. Iterate instead:
		var args = new Array();
		for (var i=2; i<arguments.length; i++) {
			args.push(arguments[i]);
		}
		player[methodName].apply(player, args);
	}
	
	if (FAVideoManagerInstance == null) {
		var FAVideoManagerInstance = new FAVideoManager();
	}