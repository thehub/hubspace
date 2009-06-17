function setCookie (name, value) {  
	var argv = setCookie.arguments;  
	var argc = setCookie.arguments.length;  
	var expires = (argc > 2) ? argv[2] : null;  
	var path = (argc > 3) ? argv[3] : null;  
	var domain = (argc > 4) ? argv[4] : null;  
	var secure = (argc > 5) ? argv[5] : false;  
	document.cookie = name + "=" + escape (value) + 
	((expires == null) ? "" : ("; expires=" + expires.toGMTString())) + 
	((path == null) ? "" : ("; path=" + path)) +  
	((domain == null) ? "" : ("; domain=" + domain)) +    
	((secure == true) ? "; secure" : "");
}

function getCookieVal (offset) {  
	var endstr = document.cookie.indexOf (";", offset);  
	if (endstr == -1){
		endstr = document.cookie.length;  
	}
	return unescape(document.cookie.substring(offset, endstr));
}

function getCookie (name) {  
	var arg = name + "=";  
	var alen = arg.length;  
	var clen = document.cookie.length;  
	var i = 0;  
	while (i < clen) {    
		var j = i + alen;    
		if (document.cookie.substring(i, j) == arg) {    
			return getCookieVal (j);    
		}
		i = document.cookie.indexOf(" ", i) + 1;    
		if (i == 0) break;   		
	}  
	return null;
}

function setOpacity(obj, opacity) {
	opacity = (opacity == 100)?99.999:opacity;
	if(opacity){
		obj.style.visibility = 'visible';
	}else{
		obj.style.visibility = 'hidden';
	}
	// IE/Win
	if(obj.style.filter != 'undefined')
		obj.style.filter = "alpha(opacity:"+opacity+")";
	
	// Safari<1.2, Konqueror
	if(obj.style.KHTMLOpacity != 'undefined')
		obj.style.KHTMLOpacity = opacity/100;
	
	// Older Mozilla and Firefox
	if(obj.style.MozOpacity != 'undefined')
		obj.style.MozOpacity = opacity/100;
	
	// Safari 1.2, newer Firefox and Mozilla, CSS3
	if(obj.style.opacity != 'undefined')
		obj.style.opacity = opacity/100;
}

function toggle(){
	var toggleText = getCookie('toggleText');
	if (toggleText == "undefined") {
		setCookie('toggleText', 'on', null, '/');
		toggleText = 'on';
	}
	if(toggleText == 'off'){
		//text is off - turn it on
		setCookie('toggleText', 'on', null, '/');
		document.getElementById('lowText').style.display = 'block';
		document.getElementById('hiText').style.display = 'none';
		document.getElementById('nextArrow').style.visibility = 'hidden';
		document.getElementById('prevArrow').style.visibility = 'hidden';
		load('tintImage', 100);
	}else if(toggleText == 'on'){
		//text is on - turn it off
		setCookie('toggleText', 'off', null, '/');
		document.getElementById('lowText').style.display = 'none';
		document.getElementById('hiText').style.display = 'block';
		document.getElementById('nextArrow').style.visibility = 'visible';
		document.getElementById('prevArrow').style.visibility = 'visible';
		load('tintImage', 0);
	}
}
function load(objId, dest) {
	if(bgLoad.complete){
		document.getElementById('mainImage').style.background = "#FFFFFF url(" + bgLoad.src + ")";
		document.getElementById('mainImage').style.visibility = 'visible';
		document.getElementById('tintImage').style.visibility = 'visible';
		glob_objId = objId;
		glob_dest = dest;
		fade();
	}else{
		window.setTimeout("load('"+objId+"',"+dest+","+current+"')", 100);
	}
}
function fade() {
	if (document.getElementById) {
		var obj = document.getElementById(glob_objId);
		if(glob_current != glob_dest){
			if(glob_current > glob_dest){
				glob_current -= 10;
			}else{
				glob_current += 10;
			}
			setOpacity(obj, glob_current);
			window.setTimeout("fade()", 50);
		}
	}
}

function init(){
	var toggleText = getCookie('toggleText');
	if (toggleText == null) {toggleText='on';}
	
	var tintImage = document.getElementById('tintImage');
	var mainImage = document.getElementById('mainImage');
	
	bgLoad=new Image();
	bgLoad.src = path + name + '.jpg';
	arrowLoadPrev = new Image();
	arrowLoadNext = new Image();
	arrowLoadPrev.src = '/static/images/entry/arrow_next_default.gif';
	arrowLoadNext.src = '/static/images/entry/arrow_prev_default.gif';
	tintImage.style.background = "#FFFFFF url(" + path + name + '_tint.jpg)';
	
	if(toggleText == 'on'){
		tintImage.style.visibility = 'visible';
		document.getElementById('lowText').style.display = 'block';
		document.getElementById('hiText').style.display = 'none';
		glob_current = 100;
	}else{
		setOpacity(document.getElementById('tintImage'), 0);
		tintImage.style.visibility = 'HIDDEN';
		mainImage.style.background = "url(" + path + name + '.jpg)';
		document.getElementById('lowText').style.display = 'none';
		document.getElementById('hiText').style.display = 'block';
		document.getElementById('nextArrow').style.visibility = 'visible';
		document.getElementById('prevArrow').style.visibility = 'visible';
		glob_current = 0;
	}
}

function enter(tab){
	var toggleText = getCookie('toggleText');
	if (toggleText == null) {toggleText='on';}
	
	if(tab=='next'){
		document.getElementById('nextArrow').src = '/static/images/entry/arrow_next_on.gif';
		if(toggleText == 'on'){
			load('tintImage', 0);
		}
	}else if(tab=='prev'){
		document.getElementById('prevArrow').src = '/static/images/entry/arrow_prev_on.gif';
		if(toggleText == 'on'){
			load('tintImage', 0);
		}
	}
	document.getElementById('nextArrow').style.visibility = 'visible';
	document.getElementById('prevArrow').style.visibility = 'visible';
}

function leave(tab){
	var toggleText = getCookie('toggleText');
	if (toggleText == null) {toggleText='on';}
	document.getElementById('nextArrow').src = '/static/images/entry/arrow_next_default.gif';
	document.getElementById('prevArrow').src = '/static/images/entry/arrow_prev_default.gif';
	if(toggleText == 'on'){
		document.getElementById('nextArrow').style.visibility = 'hidden';
		document.getElementById('prevArrow').style.visibility = 'hidden';
		if(tab=='next' || tab == 'prev'){
			load('tintImage', 100);
		}
	}else{
		document.getElementById('nextArrow').style.visibility = 'visible';
		document.getElementById('prevArrow').style.visibility = 'visible';
	}
}

function click(dest){
	//setCookie('toggleText', 'off', null, '/');
	if(dest=='prev'){
		document.location=prev;	
	}else if(dest=='next'){
		document.location=next;	
	}
}

function textMode(){
	setCookie('toggleText', 'on', null, '/');
}
