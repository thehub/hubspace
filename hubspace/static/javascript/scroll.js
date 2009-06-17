
// ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
// 
// Coded by Travis Beckham
// http://www.squidfingers.com | http://www.podlob.com
// If want to use this code, feel free to do so, but please leave this message intact.
//
// ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
// --- version date: 01/24/03 ---------------------------------------------------------

// ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

// Cross-Browser Functions

var dom = document.getElementById;
var iex = document.all;
var ns4 = document.layers;

function addEvent(event,method){this[event] = method;
	if(ns4) this.captureEvents(Event[event.substr(2,event.length).toUpperCase()]);
}
function removeEvent(event){
	this[event] = null;
	if(ns4) this.releaseEvents(Event[event.substr(2,event.length).toUpperCase()]);
}
function getElement(name,nest){
	nest = nest ? "document."+nest+"." : "";
	var el = dom ? document.getElementById(name) : iex ? document.all[name] : ns4 ? eval(nest+"document."+name) : false;
	el.css = ns4 ? el : el.style;
	el.getTop = function(){return parseInt(el.css.top) || 0};
	el.setTop = function(y){el.css.top = ns4 ? y: y+"px"};
	el.getHeight = function(){return ns4 ? el.document.height : el.offsetHeight};
	el.getClipHeight = function(){return ns4 ? el.clip.height : el.offsetHeight};
	el.hideVis = function(){el.css.visibility="hidden"};
	el.showVis = function(){el.css.visibility="visible"};
	el.addEvent = addEvent;
	el.removeEvent = removeEvent;
	return el;
}
function getYMouse(e){
	return iex ? event.clientY : e.pageY;
}

document.addEvent = addEvent;
document.removeEvent = removeEvent;

// ||||||||||||||||||||||||||||||||||||||||||||||||||
// Scroller Class

ScrollObj = function(speed, dragHeight, trackHeight, trackObj, upObj, downObj, dragObj, contentMaskObj, contentObj){
	this.speed = speed;
	this.dragHeight = dragHeight;
	this.trackHeight = trackHeight;
	this.trackObj = getElement(trackObj);
	this.upObj = getElement(upObj);
	this.downObj = getElement(downObj);
	this.dragObj = getElement(dragObj);
	this.contentMaskObj = getElement(contentMaskObj);
	this.contentObj = getElement(contentObj,contentMaskObj);
	this.obj = contentObj+"Object";
	eval(this.obj+"=this");
	
	this.trackTop = this.dragObj.getTop();
	this.trackLength = this.trackHeight-this.dragHeight;
	this.trackBottom = this.trackTop+this.trackLength;
	this.contentMaskHeight = this.contentMaskObj.getClipHeight();

	this.contentHeight = this.contentObj.getHeight();

	this.contentLength = this.contentHeight-this.contentMaskHeight;
	this.scrollLength = this.trackLength/this.contentLength;
	this.scrollTimer = null;
	
	if(this.contentHeight <= (this.contentMaskHeight+2)){
		this.dragObj.hideVis();
	        this.trackObj.hideVis();
                this.upObj.hideVis();  
                this.downObj.hideVis();
	}else{
                this.upObj.showVis();  
                this.downObj.showVis();
		var self = this;
		this.trackObj.addEvent("onmousedown", function(e){self.scrollJump(e);return false});
		this.upObj.addEvent("onmousedown", function(){self.scroll(self.speed);return false});
		this.upObj.addEvent("onmouseup", function(){self.stopScroll()});
		this.upObj.addEvent("onmouseout", function(){self.stopScroll()});
		this.downObj.addEvent("onmousedown", function(){self.scroll(-self.speed);return false});
		this.downObj.addEvent("onmouseup", function(){self.stopScroll()});
		this.downObj.addEvent("onmouseout", function(){self.stopScroll()});
		this.dragObj.addEvent("onmousedown", function(e){self.startDrag(e);return false});
		if(iex) this.dragObj.addEvent("ondragstart", function(){return false});
	}
}
ScrollObj.prototype.startDrag = function(e){
	this.dragStartMouse = getYMouse(e);
	this.dragStartOffset = this.dragObj.getTop();
	var self = this;
	document.addEvent("onmousemove", function(e){self.drag(e)});
	document.addEvent("onmouseup", function(){self.stopDrag()});
}
ScrollObj.prototype.stopDrag = function(){
	document.removeEvent("onmousemove");
	document.removeEvent("onmouseup");
}
ScrollObj.prototype.drag = function(e){
	var currentMouse = getYMouse(e);
	var mouseDifference = currentMouse-this.dragStartMouse;
	var dragDistance = this.dragStartOffset+mouseDifference;
	var dragMovement = (dragDistance<this.trackTop) ? this.trackTop : (dragDistance>this.trackBottom) ? this.trackBottom : dragDistance;
	this.dragObj.setTop(dragMovement);
	var contentMovement = -(dragMovement-this.trackTop)*(1/this.scrollLength);
	this.contentObj.setTop(contentMovement);
}
ScrollObj.prototype.scroll = function(speed){
	var contentMovement = this.contentObj.getTop()+speed;
	var dragMovement = this.trackTop-Math.round(this.contentObj.getTop()*(this.trackLength/this.contentLength));
	if(contentMovement > 0){
		contentMovement = 0;
	}else if(contentMovement < -this.contentLength){
		contentMovement = -this.contentLength;
	}
	if(dragMovement < this.trackTop){
		dragMovement = this.trackTop;
	}else if(dragMovement > this.trackBottom){
		dragMovement = this.trackBottom;
	}
	this.contentObj.setTop(contentMovement);
	this.dragObj.setTop(dragMovement);
	this.scrollTimer = window.setTimeout(this.obj+".scroll("+speed+")",25);
}
ScrollObj.prototype.stopScroll = function(){
	if(this.scrollTimer){
		window.clearTimeout(this.scrollTimer);
		this.scrollTimer = null;
	}
}
ScrollObj.prototype.scrollJump = function(e){
	var currentMouse = getYMouse(e);
	var dragDistance = currentMouse-(this.dragHeight/2);
	var dragMovement = (dragDistance<this.trackTop) ? this.trackTop : (dragDistance>this.trackBottom) ? this.trackBottom : dragDistance;
	this.dragObj.setTop(dragMovement);
	var contentMovement = -(dragMovement-this.trackTop)*(1/this.scrollLength);
	this.contentObj.setTop(contentMovement);
}

// ||||||||||||||||||||||||||||||||||||||||||||||||||
// Misc Functions

function fixNetscape4(){
	if(ns4origWidth != window.innerWidth || ns4origHeight != window.innerHeight){
		window.location.reload();
	}	
}
if(document.layers){
	ns4origWidth = window.innerWidth;
	ns4origHeight = window.innerHeight;
	window.onresize = fixNetscape4;
}

