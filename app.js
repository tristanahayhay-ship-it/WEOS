// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 001 START
// STATUS  : COMPLETED
// ======================================================================

"use strict";

const WEOS={};

WEOS.version="1.0.0";

WEOS.name="World Economic Operating System";

WEOS.bootTime=Date.now();

WEOS.ready=false;

WEOS.debug=false;

WEOS.state={};

WEOS.cache={};

WEOS.dom={};

WEOS.events={};

WEOS.modules={};

WEOS.animation={};

WEOS.camera={};

WEOS.globe={};

WEOS.network={};

WEOS.data={};

WEOS.utils={};

WEOS.settings={};

WEOS.runtime={};

WEOS.runtime.fps=0;

WEOS.runtime.frame=0;

WEOS.runtime.delta=0;

WEOS.runtime.lastFrame=performance.now();

WEOS.runtime.running=false;

// ======================================================================
// END SECTION : 001
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 002 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.settings.targetFPS=60;

WEOS.settings.antialias=true;

WEOS.settings.alpha=true;

WEOS.settings.powerPreference="high-performance";

WEOS.settings.enableStars=true;

WEOS.settings.enableAtmosphere=true;

WEOS.settings.enableGlow=true;

WEOS.settings.enableClouds=true;

WEOS.settings.enableNetwork=true;

WEOS.settings.enableBloom=true;

WEOS.settings.enableControls=true;

WEOS.settings.autoRotate=true;

WEOS.settings.autoRotateSpeed=0.15;

WEOS.settings.minZoom=120;

WEOS.settings.maxZoom=520;

WEOS.settings.defaultZoom=260;

WEOS.settings.background="#000000";

WEOS.settings.locale="vi-VN";

WEOS.settings.timeZone="UTC";

WEOS.settings.version=WEOS.version;

// ======================================================================
// END SECTION : 002
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 003 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.cache.windowWidth=window.innerWidth;

WEOS.cache.windowHeight=window.innerHeight;

WEOS.cache.devicePixelRatio=Math.min(
window.devicePixelRatio||1,
2
);

WEOS.cache.centerX=
WEOS.cache.windowWidth/2;

WEOS.cache.centerY=
WEOS.cache.windowHeight/2;

WEOS.cache.aspect=
WEOS.cache.windowWidth/
WEOS.cache.windowHeight;

WEOS.cache.mouseX=0;

WEOS.cache.mouseY=0;

WEOS.cache.pointerDown=false;

WEOS.cache.hoverObject=null;

WEOS.cache.selectedObject=null;

WEOS.cache.resizePending=false;

// ======================================================================
// END SECTION : 003
// ======================================================================// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 004 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.dom.root=

document.getElementById(
"weos"
);

WEOS.dom.renderer=

document.getElementById(
"renderer"
);

WEOS.dom.overlay=

document.getElementById(
"overlay"
);

WEOS.dom.viewport=

document.getElementById(
"globeViewport"
);

WEOS.dom.loadingScreen=

document.getElementById(
"loadingScreen"
);

WEOS.dom.loadingProgress=

document.getElementById(
"loadingProgress"
);

WEOS.dom.loadingPercent=

document.getElementById(
"loadingPercent"
);

// ======================================================================
// END SECTION : 004
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 005 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.dom.utcClock=

document.getElementById(
"utcClock"
);

WEOS.dom.fpsCounter=

document.getElementById(
"fpsCounter"
);

WEOS.dom.connectionStatus=

document.getElementById(
"connectionStatus"
);

WEOS.dom.tooltip=

document.getElementById(
"tooltip"
);

WEOS.dom.countryPanel=

document.getElementById(
"countryPanel"
);

WEOS.dom.notificationContainer=

document.getElementById(
"notificationContainer"
);

// ======================================================================
// END SECTION : 005
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 006 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.dom.contextMenu=

document.getElementById(
"contextMenu"
);

WEOS.dom.modalContainer=

document.getElementById(
"modalContainer"
);

WEOS.dom.debugLayer=

document.getElementById(
"debugLayer"
);

WEOS.dom.effectLayer=

document.getElementById(
"effectLayer"
);

WEOS.dom.particleLayer=

document.getElementById(
"particleLayer"
);

WEOS.dom.systemLayer=

document.getElementById(
"systemLayer"
);

// ======================================================================
// END SECTION : 006
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 007 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.dom.backgroundCanvas=

document.getElementById(
"backgroundCanvas"
);

WEOS.dom.effectCanvas=

document.getElementById(
"effectCanvas"
);

WEOS.dom.homeButton=

document.getElementById(
"homeButton"
);

WEOS.dom.worldButton=

document.getElementById(
"worldButton"
);

WEOS.dom.macroButton=

document.getElementById(
"macroButton"
);

WEOS.dom.marketButton=

document.getElementById(
"marketButton"
);

WEOS.dom.flowButton=

document.getElementById(
"flowButton"
);

// ======================================================================
// END SECTION : 007
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 008 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.dom.settingButton=

document.getElementById(
"settingButton"
);

WEOS.dom.selectionLayer=

document.getElementById(
"selectionLayer"
);

WEOS.dom.animationLayer=

document.getElementById(
"animationLayer"
);

WEOS.dom.informationLayer=

document.getElementById(
"informationLayer"
);

WEOS.dom.cameraLayer=

document.getElementById(
"cameraLayer"
);

WEOS.dom.systemAssets=

document.getElementById(
"systemAssets"
);

// ======================================================================
// END SECTION : 008
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 009 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.dom.earthDayTexture=

document.getElementById(
"earthDayTexture"
);

WEOS.dom.earthNightTexture=

document.getElementById(
"earthNightTexture"
);

WEOS.dom.earthBumpTexture=

document.getElementById(
"earthBumpTexture"
);

WEOS.dom.earthSpecularTexture=

document.getElementById(
"earthSpecularTexture"
);

WEOS.dom.earthCloudTexture=

document.getElementById(
"earthCloudTexture"
);

WEOS.dom.starfieldTexture=

document.getElementById(
"starfieldTexture"
);

WEOS.dom.moonTexture=

document.getElementById(
"moonTexture"
);

// ======================================================================
// END SECTION : 009
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 010 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.clamp=

function(

value,

min,

max

){

return Math.min(

Math.max(

value,

min

),

max

);

};

WEOS.utils.lerp=

function(

start,

end,

factor

){

return start+

(

end-start

)

*

factor;

};

// ======================================================================
// END SECTION : 010
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 011 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.map=

function(

value,

inMin,

inMax,

outMin,

outMax

){

return outMin+

(

(

value-inMin

)

/

(

inMax-inMin

)

)

*

(

outMax-outMin

);

};

WEOS.utils.degToRad=

function(

degree

){

return degree*

Math.PI/

180;

};

// ======================================================================
// END SECTION : 011
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 012 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.radToDeg=

function(

radian

){

return radian*

180/

Math.PI;

};

WEOS.utils.distance=

function(

x1,

y1,

x2,

y2

){

return Math.hypot(

x2-x1,

y2-y1

);

};

// ======================================================================
// END SECTION : 012
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 013 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.uuid=

function(){

return crypto
.randomUUID();

};

WEOS.utils.now=

function(){

return performance
.now();

};

WEOS.utils.timestamp=

function(){

return Date
.now();

};

// ======================================================================
// END SECTION : 013
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 014 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.formatNumber=

function(

value,

digits=2

){

return Number(

value

)

.toLocaleString(

WEOS.settings.locale,

{

maximumFractionDigits:

digits

}

);

};

WEOS.utils.isFunction=

function(

value

){

return typeof

value===

"function";

};

// ======================================================================
// END SECTION : 014
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 015 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.isObject=

function(

value

){

return

value!==null

&&

typeof value===

"object"

&&

!Array.isArray(

value

);

};

WEOS.utils.isString=

function(

value

){

return typeof

value===

"string";

};

// ======================================================================
// END SECTION : 015
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 016 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.isNumber=

function(

value

){

return

typeof value===

"number"

&&

Number.isFinite(

value

);

};

WEOS.utils.isBoolean=

function(

value

){

return typeof

value===

"boolean";

};

// ======================================================================
// END SECTION : 016
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 017 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.isArray=

function(

value

){

return

Array.isArray(

value

);

};

WEOS.utils.isDefined=

function(

value

){

return

value!==

undefined

&&

value!==

null;

};

// ======================================================================
// END SECTION : 017
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 018 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.isEmpty=

function(

value

){

if(

value===null

||

value===undefined

){

return true;

}

if(

typeof value===

"string"

){

return

value.trim()

.length===0;

}

if(

Array.isArray(

value

)

){

return

value.length===0;

}

if(

WEOS.utils.isObject(

value

)

){

return

Object.keys(

value

)

.length===0;

}

return false;

};

// ======================================================================
// END SECTION : 018
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 019 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.deepClone=

function(

value

){

if(

structuredClone

){

return

structuredClone(

value

);

}

return JSON.parse(

JSON.stringify(

value

)

);

};

// ======================================================================
// END SECTION : 019
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 020 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.deepMerge=

function(

target,

source

){

if(

!WEOS.utils.isObject(

target

)

||

!WEOS.utils.isObject(

source

)

){

return source;

}

for(

const key

in source

){

const value=

source[key];

if(

WEOS.utils.isObject(

value

)

){

target[key]=

WEOS.utils.deepMerge(

target[key]??{},

value

);

continue;

}

target[key]=

value;

}

return target;

};

// ======================================================================
// END SECTION : 020
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 021 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.debounce=

function(

callback,

delay=250

){

let timer;

return function(

...args

){

clearTimeout(

timer

);

timer=

setTimeout(

()=>{

callback.apply(

this,

args

);

},

delay

);

};

};

// ======================================================================
// END SECTION : 021
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 022 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.throttle=

function(

callback,

delay=100

){

let waiting=

false;

return function(

...args

){

if(

waiting

){

return;

}

waiting=

true;

callback.apply(

this,

args

);

setTimeout(

()=>{

waiting=

false;

},

delay

);

};

};

// ======================================================================
// END SECTION : 022
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 023 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.once=

function(

callback

){

let executed=

false;

let result;

return function(

...args

){

if(

executed

){

return result;

}

executed=

true;

result=

callback.apply(

this,

args

);

return result;

};

};

// ======================================================================
// END SECTION : 023
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 024 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.wait=

function(

milliseconds

){

return new

Promise(

resolve=>{

setTimeout(

resolve,

milliseconds

);

}

);

};

// ======================================================================
// END SECTION : 024
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 025 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.nextFrame=

function(){

return new

Promise(

resolve=>{

requestAnimationFrame(

resolve

);

}

);

};

// ======================================================================
// END SECTION : 025
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 026 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.createElement=

function(

tag,

className=""

){

const element=

document

.createElement(

tag

);

if(

className

){

element.className=

className;

}

return element;

};

// ======================================================================
// END SECTION : 026
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 027 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.query=

function(

selector,

scope=document

){

return scope

.querySelector(

selector

);

};

WEOS.utils.queryAll=

function(

selector,

scope=document

){

return Array.from(

scope

.querySelectorAll(

selector

)

);

};

// ======================================================================
// END SECTION : 027
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 028 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.on=

function(

element,

event,

handler,

options

){

if(

!element

){

return;

}

element

.addEventListener(

event,

handler,

options

);

};

// ======================================================================
// END SECTION : 028
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 029 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.off=

function(

element,

event,

handler,

options

){

if(

!element

){

return;

}

element

.removeEventListener(

event,

handler,

options

);

};

// ======================================================================
// END SECTION : 029
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 030 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.emit=

function(

name,

detail={}

){

window

.dispatchEvent(

new CustomEvent(

name,

{

detail

}

)

);

};

// ======================================================================
// END SECTION : 030
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 031 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen=

function(

name,

handler,

options

){

window

.addEventListener(

name,

handler,

options

);

return handler;

};

// ======================================================================
// END SECTION : 031
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 032 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.unlisten=

function(

name,

handler,

options

){

window

.removeEventListener(

name,

handler,

options

);

};

// ======================================================================
// END SECTION : 032
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 033 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.setText=

function(

element,

text

){

if(

!element

){

return;

}

element

.textContent=

text;

};

// ======================================================================
// END SECTION : 033
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 034 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.setHTML=

function(

element,

html

){

if(

!element

){

return;

}

element

.innerHTML=

html;

};

// ======================================================================
// END SECTION : 034
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 035 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.addClass=

function(

element,

className

){

if(

!element

){

return;

}

element

.classList

.add(

className

);

};

// ======================================================================
// END SECTION : 035
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 036 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.removeClass=

function(

element,

className

){

if(

!element

){

return;

}

element

.classList

.remove(

className

);

};

// ======================================================================
// END SECTION : 036
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 037 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.toggleClass=

function(

element,

className,

force

){

if(

!element

){

return;

}

element

.classList

.toggle(

className,

force

);

};

// ======================================================================
// END SECTION : 037
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 038 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.hasClass=

function(

element,

className

){

if(

!element

){

return false;

}

return element

.classList

.contains(

className

);

};

// ======================================================================
// END SECTION : 038
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 039 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.show=

function(

element

){

if(

!element

){

return;

}

element

.style.display=

"";

};

WEOS.utils.hide=

function(

element

){

if(

!element

){

return;

}

element

.style.display=

"none";

};

// ======================================================================
// END SECTION : 039
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 040 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.setStyle=

function(

element,

property,

value

){

if(

!element

){

return;

}

element

.style[

property

]=

value;

};

// ======================================================================
// END SECTION : 040
// ======================================================================
