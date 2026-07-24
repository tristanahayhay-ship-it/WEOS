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
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 041 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.boot=

async function(){

WEOS.runtime.running=

true;

WEOS.runtime.frame=

0;

WEOS.runtime.lastFrame=

performance.now();

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"BOOTING"

);

await

WEOS.initialize();

};

// ======================================================================
// END SECTION : 041
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 042 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

async function(){

await

WEOS.initializeDOM();

await

WEOS.initializeRenderer();

await

WEOS.initializeScene();

await

WEOS.initializeCamera();

await

WEOS.initializeLights();

};

// ======================================================================
// END SECTION : 042
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 043 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeDOM=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"5 %"

);

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"INITIALIZING"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"5%"

);

};

// ======================================================================
// END SECTION : 043
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 044 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeRenderer=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"15 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"15%"

);

WEOS.renderer=

new THREE.WebGLRenderer(

{

antialias:

WEOS.settings.antialias,

alpha:

WEOS.settings.alpha,

powerPreference:

WEOS.settings.powerPreference

}

);

};

// ======================================================================
// END SECTION : 044
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 045 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.renderer

.setPixelRatio(

WEOS.cache.devicePixelRatio

);

WEOS.renderer

.setSize(

WEOS.cache.windowWidth,

WEOS.cache.windowHeight

);

WEOS.renderer

.setClearColor(

WEOS.settings.background,

1

);

WEOS.dom.renderer

.appendChild(

WEOS.renderer.domElement

);

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"20 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"20%"

);

// ======================================================================
// END SECTION : 045
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 046 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeScene=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"30 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"30%"

);

WEOS.scene=

new THREE.Scene();

WEOS.scene.background=

new THREE.Color(

WEOS.settings.background

);

};

// ======================================================================
// END SECTION : 046
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 047 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeCamera=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"40 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"40%"

);

WEOS.camera=

new THREE.PerspectiveCamera(

45,

WEOS.cache.aspect,

0.1,

5000

);

};

// ======================================================================
// END SECTION : 047
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 048 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.camera.position.set(

0,

0,

WEOS.settings.defaultZoom

);

WEOS.camera.lookAt(

0,

0,

0

);

WEOS.scene.add(

WEOS.camera

);

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"45 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"45%"

);

// ======================================================================
// END SECTION : 048
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 049 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeLights=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"55 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"55%"

);

WEOS.lights={};

WEOS.lights.ambient=

new THREE.AmbientLight(

0xffffff,

0.35

);

};

// ======================================================================
// END SECTION : 049
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 050 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.lights.directional=

new THREE.DirectionalLight(

0xffffff,

2.2

);

WEOS.lights.directional.position.set(

200,

150,

250

);

WEOS.scene.add(

WEOS.lights.ambient

);

WEOS.scene.add(

WEOS.lights.directional

);

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"60 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"60%"

);

// ======================================================================
// END SECTION : 050
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 051 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeGlobe=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"70 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"70%"

);

WEOS.globe.group=

new THREE.Group();

WEOS.scene.add(

WEOS.globe.group

);

};

// ======================================================================
// END SECTION : 051
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 052 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.globe.radius=

100;

WEOS.globe.geometry=

new THREE.SphereGeometry(

WEOS.globe.radius,

128,

128

);

WEOS.globe.material=

new THREE.MeshPhongMaterial(

{

color:0x2b6cff,

shininess:18

}

);

// ======================================================================
// END SECTION : 052
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 053 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.globe.mesh=

new THREE.Mesh(

WEOS.globe.geometry,

WEOS.globe.material

);

WEOS.globe.group.add(

WEOS.globe.mesh

);

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"75 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"75%"

);

// ======================================================================
// END SECTION : 053
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 054 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeAtmosphere=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"80 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"80%"

);

WEOS.atmosphere={};

WEOS.atmosphere.geometry=

new THREE.SphereGeometry(

WEOS.globe.radius+2,

128,

128

);

// ======================================================================
// END SECTION : 054
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 055 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.atmosphere.material=

new THREE.MeshPhongMaterial(

{

color:0x66ccff,

transparent:true,

opacity:0.12,

side:THREE.BackSide

}

);

WEOS.atmosphere.mesh=

new THREE.Mesh(

WEOS.atmosphere.geometry,

WEOS.atmosphere.material

);

WEOS.globe.group.add(

WEOS.atmosphere.mesh

);

// ======================================================================
// END SECTION : 055
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 056 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"85 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"85%"

);

WEOS.scene.add(

WEOS.globe.group

);

await

WEOS.initializeAnimation();

// ======================================================================
// END SECTION : 056
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 057 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeAnimation=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"90 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"90%"

);

WEOS.runtime.running=

true;

requestAnimationFrame(

WEOS.animate

);

};

// ======================================================================
// END SECTION : 057
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 058 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.animate=

function(

time

){

if(

!WEOS.runtime.running

){

return;

}

WEOS.runtime.delta=

time-

WEOS.runtime.lastFrame;

WEOS.runtime.lastFrame=

time;

// ======================================================================
// END SECTION : 058
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 059 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.frame++;

WEOS.runtime.fps=

1000/

Math.max(

WEOS.runtime.delta,

1

);

WEOS.globe.group.rotation.y+=

0.0015;

WEOS.renderer.render(

WEOS.scene,

WEOS.camera

);

requestAnimationFrame(

WEOS.animate

);

// ======================================================================
// END SECTION : 059
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 060 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.setText(

WEOS.dom.fpsCounter,

Math.round(

WEOS.runtime.fps

)

+

" FPS"

);

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"ONLINE"

);

};

// ======================================================================
// END SECTION : 060
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 061 START
// STATUS  : COMPLETED
// ======================================================================

document

.addEventListener(

"DOMContentLoaded",

()=>{

WEOS.boot();

}

);

window

.WEOS=

WEOS;

// ======================================================================
// END SECTION : 061
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 062 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

WEOS.utils.once(

WEOS.initialize

);

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"100 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"100%"

);

WEOS.ready=

true;

// ======================================================================
// END SECTION : 062
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 063 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.hide(

WEOS.dom.loadingScreen

);

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"READY"

);

WEOS.utils.emit(

"weos-ready",

{

version:

WEOS.version

}

);

// ======================================================================
// END SECTION : 063
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 064 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"weos-ready",

()=>{

console.log(

"%cWEOS READY",

"color:#4CAF50;font-size:16px;font-weight:bold;"

);

console.log(

WEOS

);

}

);

// ======================================================================
// END SECTION : 064
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 065 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"resize",

WEOS.utils.debounce(

()=>{

WEOS.cache.windowWidth=

window.innerWidth;

WEOS.cache.windowHeight=

window.innerHeight;

WEOS.cache.aspect=

WEOS.cache.windowWidth/

WEOS.cache.windowHeight;

},

100

)

);

// ======================================================================
// END SECTION : 065
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 066 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"resize",

()=>{

if(

!WEOS.renderer

||

!WEOS.camera

){

return;

}

WEOS.renderer.setSize(

WEOS.cache.windowWidth,

WEOS.cache.windowHeight

);

WEOS.camera.aspect=

WEOS.cache.aspect;

WEOS.camera.updateProjectionMatrix();

}

);

// ======================================================================
// END SECTION : 066
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 067 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"resize",

()=>{

WEOS.cache.devicePixelRatio=

Math.min(

window.devicePixelRatio||

1,

2

);

WEOS.renderer

.setPixelRatio(

WEOS.cache.devicePixelRatio

);

}

);

// ======================================================================
// END SECTION : 067
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 068 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"pointermove",

event=>{

WEOS.cache.mouseX=

event.clientX;

WEOS.cache.mouseY=

event.clientY;

}

);

// ======================================================================
// END SECTION : 068
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 069 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"pointerdown",

event=>{

WEOS.cache.pointerDown=

true;

WEOS.cache.mouseX=

event.clientX;

WEOS.cache.mouseY=

event.clientY;

}

);

// ======================================================================
// END SECTION : 069
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 070 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"pointerup",

()=>{

WEOS.cache.pointerDown=

false;

WEOS.cache.hoverObject=

null;

}

);

// ======================================================================
// END SECTION : 070
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 071 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"visibilitychange",

()=>{

WEOS.runtime.running=

!

document.hidden;

if(

WEOS.runtime.running

){

WEOS.runtime.lastFrame=

performance.now();

requestAnimationFrame(

WEOS.animate

);

}

}

);

// ======================================================================
// END SECTION : 071
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 072 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"keydown",

event=>{

WEOS.events.keyboard =
WEOS.events.keyboard || {};

WEOS.events.keyboard[
event.code
]=true;

}

);
  
// ======================================================================
// END SECTION : 072
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 073 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"keyup",

event=>{

if(

!WEOS.events

.keyboard

){

return;

}

WEOS.events

.keyboard[

event.code

]=

false;

}

);

// ======================================================================
// END SECTION : 073
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 074 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.events.keyboard??

={};

WEOS.events.pointer??

={};

WEOS.events.pointer.x=

0;

WEOS.events.pointer.y=

0;

WEOS.events.pointer.down=

false;

WEOS.events.pointer.dragging=

false;

// ======================================================================
// END SECTION : 074
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 075 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"pointermove",

event=>{

WEOS.events.pointer.x=

event.clientX;

WEOS.events.pointer.y=

event.clientY;

if(

WEOS.cache.pointerDown

){

WEOS.events.pointer.dragging=

true;

}

}

);

// ======================================================================
// END SECTION : 075
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 076 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"pointerdown",

()=>{

WEOS.events.pointer.down=

true;

WEOS.events.pointer.dragging=

false;

}

);

WEOS.utils.listen(

"pointerup",

()=>{

WEOS.events.pointer.down=

false;

WEOS.events.pointer.dragging=

false;

}

);

// ======================================================================
// END SECTION : 076
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 077 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.events.update=

function(){

WEOS.events.pointer.dragging=

WEOS.events.pointer.down

&&

WEOS.cache.pointerDown;

WEOS.events.pointer.deltaX=

WEOS.events.pointer.x-

WEOS.cache.centerX;

WEOS.events.pointer.deltaY=

WEOS.events.pointer.y-

WEOS.cache.centerY;

};

// ======================================================================
// END SECTION : 077
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 078 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.events.reset=

function(){

WEOS.events.pointer.deltaX=

0;

WEOS.events.pointer.deltaY=

0;

WEOS.events.pointer.dragging=

false;

WEOS.cache.hoverObject=

null;

};

// ======================================================================
// END SECTION : 078
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 079 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.events.tick=

function(){

WEOS.events.update();

if(

!WEOS.runtime.running

){

return;

}

WEOS.runtime.frame++;

};

// ======================================================================
// END SECTION : 079
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 080 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.update=

function(

time

){

WEOS.runtime.delta=

time-

WEOS.runtime.lastFrame;

WEOS.runtime.lastFrame=

time;

WEOS.events.tick();

};

// ======================================================================
// END SECTION : 080
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 081 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.render=

function(){

if(

!WEOS.renderer

||

!WEOS.scene

||

!WEOS.camera

){

return;

}

WEOS.renderer.render(

WEOS.scene,

WEOS.camera

);

};

// ======================================================================
// END SECTION : 081
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 082 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.loop=

function(

time

){

WEOS.runtime.update(

time

);

WEOS.runtime.render();

requestAnimationFrame(

WEOS.runtime.loop

);

};

// ======================================================================
// END SECTION : 082
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 083 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.start=

function(){

if(

WEOS.runtime.running

){

return;

}

WEOS.runtime.running=

true;

WEOS.runtime.lastFrame=

performance.now();

requestAnimationFrame(

WEOS.runtime.loop

);

};

// ======================================================================
// END SECTION : 083
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 084 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.stop=

function(){

WEOS.runtime.running=

false;

};

WEOS.runtime.toggle=

function(){

if(

WEOS.runtime.running

){

WEOS.runtime.stop();

return;

}

WEOS.runtime.start();

};

// ======================================================================
// END SECTION : 084
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 085 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.pause=

function(){

WEOS.runtime.running=

false;

};

WEOS.runtime.resume=

function(){

if(

WEOS.runtime.running

){

return;

}

WEOS.runtime.start();

};

// ======================================================================
// END SECTION : 085
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 086 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.clock={};

WEOS.clock.start=

performance.now();

WEOS.clock.elapsed=

0;

WEOS.clock.delta=

0;

WEOS.clock.update=

function(

time

){

WEOS.clock.delta=

time-

WEOS.clock.start;

WEOS.clock.elapsed+=

WEOS.clock.delta;

WEOS.clock.start=

time;

};

// ======================================================================
// END SECTION : 086
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 087 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.clock.reset=

function(){

WEOS.clock.start=

performance.now();

WEOS.clock.elapsed=

0;

WEOS.clock.delta=

0;

};

WEOS.clock.seconds=

function(){

return

WEOS.clock.elapsed/

1000;

};

// ======================================================================
// END SECTION : 087
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 088 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.clock.minutes=

function(){

return

WEOS.clock.seconds()

/

60;

};

WEOS.clock.hours=

function(){

return

WEOS.clock.minutes()

/

60;

};

WEOS.clock.days=

function(){

return

WEOS.clock.hours()

/

24;

};

// ======================================================================
// END SECTION : 088
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 089 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.fps={};

WEOS.fps.value=

0;

WEOS.fps.frames=

0;

WEOS.fps.last=

performance.now();

WEOS.fps.update=

function(

time

){

WEOS.fps.frames++;

const elapsed=

time-

WEOS.fps.last;

if(

elapsed>=1000

){

WEOS.fps.value=

WEOS.fps.frames;

WEOS.fps.frames=

0;

WEOS.fps.last=

time;

}

};

// ======================================================================
// END SECTION : 089
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 090 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.fps.reset=

function(){

WEOS.fps.value=

0;

WEOS.fps.frames=

0;

WEOS.fps.last=

performance.now();

};

WEOS.fps.text=

function(){

return

WEOS.fps.value+

" FPS";

};

// ======================================================================
// END SECTION : 090
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 091 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.time={};

WEOS.time.utc=

function(){

return new

Date();

};

WEOS.time.updateClock=

function(){

if(

!WEOS.dom.utcClock

){

return;

}

WEOS.utils.setText(

WEOS.dom.utcClock,

WEOS.time.utc()

.toUTCString()

);

};

// ======================================================================
// END SECTION : 091
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 092 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.time.startClock=

function(){

WEOS.time.updateClock();

setInterval(

()=>{

WEOS.time.updateClock();

},

1000

);

};

// ======================================================================
// END SECTION : 092
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 093 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.time.stopClock=

function(){

if(

WEOS.time.interval

){

clearInterval(

WEOS.time.interval

);

WEOS.time.interval=

null;

}

};

WEOS.time.interval=

setInterval(

WEOS.time.updateClock,

1000

);

// ======================================================================
// END SECTION : 093
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 094 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.time.startClock=

function(){

WEOS.time.stopClock();

WEOS.time.updateClock();

WEOS.time.interval=

setInterval(

WEOS.time.updateClock,

1000

);

};

// ======================================================================
// END SECTION : 094
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 095 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.time.initialize=

function(){

WEOS.time.startClock();

WEOS.utils.listen(

"visibilitychange",

()=>{

if(

document.hidden

){

WEOS.time.stopClock();

return;

}

WEOS.time.startClock();

}

);

};

// ======================================================================
// END SECTION : 095
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 096 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

WEOS.utils.once(

async function(){

await

WEOS.initializeDOM();

await

WEOS.initializeRenderer();

await

WEOS.initializeScene();

await

WEOS.initializeCamera();

await

WEOS.initializeLights();

await

WEOS.initializeGlobe();

await

WEOS.initializeAtmosphere();

WEOS.time.initialize();

}

);

// ======================================================================
// END SECTION : 096
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 097 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

WEOS.utils.once(

async function(){

await

WEOS.initializeDOM();

await

WEOS.initializeRenderer();

await

WEOS.initializeScene();

await

WEOS.initializeCamera();

await

WEOS.initializeLights();

await

WEOS.initializeGlobe();

await

WEOS.initializeAtmosphere();

await

WEOS.initializeAnimation();

WEOS.time.initialize();

WEOS.ready=

true;

}

);

// ======================================================================
// END SECTION : 097
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 098 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

WEOS.utils.once(

async function(){

await

WEOS.initializeDOM();

await

WEOS.initializeRenderer();

await

WEOS.initializeScene();

await

WEOS.initializeCamera();

await

WEOS.initializeLights();

await

WEOS.initializeGlobe();

await

WEOS.initializeAtmosphere();

await

WEOS.initializeAnimation();

WEOS.time.initialize();

WEOS.utils.hide(

WEOS.dom.loadingScreen

);

WEOS.ready=

true;

}

);

// ======================================================================
// END SECTION : 098
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 099 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

WEOS.utils.once(

async function(){

await

WEOS.initializeDOM();

await

WEOS.initializeRenderer();

await

WEOS.initializeScene();

await

WEOS.initializeCamera();

await

WEOS.initializeLights();

await

WEOS.initializeGlobe();

await

WEOS.initializeAtmosphere();

await

WEOS.initializeAnimation();

WEOS.time.initialize();

WEOS.utils.hide(

WEOS.dom.loadingScreen

);

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"READY"

);

WEOS.ready=

true;

WEOS.utils.emit(

"weos-ready"

);

}

);

// ======================================================================
// END SECTION : 099
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 100 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"weos-ready",

()=>{

console.log(

"WEOS Version:",

WEOS.version

);

console.log(

"Renderer:",

WEOS.renderer

);

console.log(

"Scene:",

WEOS.scene

);

console.log(

"Camera:",

WEOS.camera

);

}

);

// ======================================================================
// END SECTION : 100
// ======================================================================
// ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 101 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeStars=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"92 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"92%"

);

WEOS.stars={};

WEOS.stars.geometry=

new THREE.BufferGeometry();

// ======================================================================
// END SECTION : 101
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 102 START
// STATUS  : COMPLETED
// ======================================================================

const starCount=

15000;

const starPositions=

new Float32Array(

starCount*3

);

WEOS.stars.count=

starCount;

WEOS.stars.positions=

starPositions;

// ======================================================================
// END SECTION : 102
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 103 START
// STATUS  : COMPLETED
// ======================================================================

for(

let i=0;

i<

starPositions.length;

i+=3

){

starPositions[i]=

(

Math.random()

-0.5

)

*

4000;

starPositions[i+1]=

(

Math.random()

-0.5

)

*

4000;

starPositions[i+2]=

(

Math.random()

-0.5

)

*

4000;

}

// ======================================================================
// END SECTION : 103
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 104 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.stars.geometry

.setAttribute(

"position",

new THREE.BufferAttribute(

WEOS.stars.positions,

3

)

);

WEOS.stars.material=

new THREE.PointsMaterial(

{

color:0xffffff,

size:1.2,

sizeAttenuation:true

}

);

// ======================================================================
// END SECTION : 104
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 105 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.stars.points=

new THREE.Points(

WEOS.stars.geometry,

WEOS.stars.material

);

WEOS.scene.add(

WEOS.stars.points

);

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"94 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"94%"

);

// ======================================================================
// END SECTION : 105
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 106 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeStars=

WEOS.utils.once(

WEOS.initializeStars

);

await

WEOS.initializeStars();

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"95 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"95%"

);

// ======================================================================
// END SECTION : 106
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 107 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.animate=

function(

time

){

if(

!WEOS.runtime.running

){

return;

}

WEOS.runtime.update(

time

);

WEOS.clock.update(

time

);

WEOS.fps.update(

time

);

if(

WEOS.stars

&&

WEOS.stars.points

){

WEOS.stars.points.rotation.y+=

0.00005;

}

// ======================================================================
// END SECTION : 107
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 108 START
// STATUS  : COMPLETED
// ======================================================================

if(

WEOS.globe

&&

WEOS.globe.group

){

WEOS.globe.group.rotation.y+=

0.0015;

}

WEOS.runtime.render();

WEOS.utils.setText(

WEOS.dom.fpsCounter,

WEOS.fps.text()

);

requestAnimationFrame(

WEOS.animate

);

};

// ======================================================================
// END SECTION : 108
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 109 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

WEOS.utils.once(

async function(){

await

WEOS.initializeDOM();

await

WEOS.initializeRenderer();

await

WEOS.initializeScene();

await

WEOS.initializeCamera();

await

WEOS.initializeLights();

await

WEOS.initializeGlobe();

await

WEOS.initializeAtmosphere();

await

WEOS.initializeStars();

await

WEOS.initializeAnimation();

WEOS.time.initialize();

WEOS.utils.hide(

WEOS.dom.loadingScreen

);

WEOS.ready=

true;

}

);

// ======================================================================
// END SECTION : 109
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 110 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

WEOS.utils.once(

async function(){

await

WEOS.initializeDOM();

await

WEOS.initializeRenderer();

await

WEOS.initializeScene();

await

WEOS.initializeCamera();

await

WEOS.initializeLights();

await

WEOS.initializeGlobe();

await

WEOS.initializeAtmosphere();

await

WEOS.initializeStars();

await

WEOS.initializeAnimation();

WEOS.time.initialize();

WEOS.utils.hide(

WEOS.dom.loadingScreen

);

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"READY"

);

WEOS.utils.emit(

"weos-ready"

);

WEOS.ready=

true;

}

);

// ======================================================================
// END SECTION : 110
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 111 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeClouds=

async function(){

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"96 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"96%"

);

WEOS.clouds={};

WEOS.clouds.geometry=

new THREE.SphereGeometry(

WEOS.globe.radius+

0.8,

128,

128

);

// ======================================================================
// END SECTION : 111
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 112 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.clouds.material=

new THREE.MeshPhongMaterial(

{

color:0xffffff,

transparent:true,

opacity:0.18,

depthWrite:false,

side:THREE.DoubleSide

}

);

WEOS.clouds.mesh=

new THREE.Mesh(

WEOS.clouds.geometry,

WEOS.clouds.material

);

// ======================================================================
// END SECTION : 112
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 113 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.globe.group.add(

WEOS.clouds.mesh

);

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"97 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"97%"

);

// ======================================================================
// END SECTION : 113
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 114 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initializeClouds=

WEOS.utils.once(

WEOS.initializeClouds

);

await

WEOS.initializeClouds();

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"98 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"98%"

);

// ======================================================================
// END SECTION : 114
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 115 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.initialize=

WEOS.utils.once(

async function(){

await

WEOS.initializeDOM();

await

WEOS.initializeRenderer();

await

WEOS.initializeScene();

await

WEOS.initializeCamera();

await

WEOS.initializeLights();

await

WEOS.initializeGlobe();

await

WEOS.initializeAtmosphere();

await

WEOS.initializeStars();

await

WEOS.initializeClouds();

await

WEOS.initializeAnimation();

WEOS.time.initialize();

WEOS.utils.hide(

WEOS.dom.loadingScreen

);

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"READY"

);

WEOS.utils.emit(

"weos-ready"

);

WEOS.ready=

true;

}

);

// ======================================================================
// END SECTION : 115
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 116 START
// STATUS  : COMPLETED
// ======================================================================

if(

WEOS.clouds

&&

WEOS.clouds.mesh

){

WEOS.clouds.mesh.rotation.y+=

0.0019;

}

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"99 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"99%"

);

// ======================================================================
// END SECTION : 116
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 117 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"100 %"

);

WEOS.utils.setStyle(

WEOS.dom.loadingProgress,

"width",

"100%"

);

WEOS.utils.hide(

WEOS.dom.loadingScreen

);

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"ONLINE"

);

// ======================================================================
// END SECTION : 117
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 118 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.emit(

"weos-online",

{

version:

WEOS.version,

bootTime:

WEOS.bootTime,

ready:

WEOS.ready

}

);

// ======================================================================
// END SECTION : 118
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 119 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"weos-online",

()=>{

console.log(

"%cWEOS ONLINE",

"color:#00E5FF;font-size:16px;font-weight:bold;"

);

WEOS.ready=

true;

WEOS.runtime.start();

}

);

// ======================================================================
// END SECTION : 119
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 120 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.utils.listen(

"weos-online",

()=>{

WEOS.utils.setText(

WEOS.dom.connectionStatus,

"ONLINE"

);

WEOS.utils.setText(

WEOS.dom.loadingPercent,

"100 %"

);

console.log(

"WEOS Runtime Started"

);

}

);

// ======================================================================
// END SECTION : 120
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 121 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network={};

WEOS.network.nodes=[];

WEOS.network.links=[];

WEOS.network.group=

new THREE.Group();

WEOS.scene.add(

WEOS.network.group

);

// ======================================================================
// END SECTION : 121
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 122 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.material=

new THREE.LineBasicMaterial(

{

color:0x3aa6ff,

transparent:true,

opacity:0.35

}

);

WEOS.network.maxDistance=

32;

WEOS.network.nodeCount=

0;

// ======================================================================
// END SECTION : 122
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 123 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.initialize=

function(

count=250

){

WEOS.network.nodeCount=

count;

WEOS.network.nodes.length=

0;

WEOS.network.links.length=

0;

};

// ======================================================================
// END SECTION : 123
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 124 START
// STATUS  : COMPLETED
// ======================================================================

for(

let i=0;

i<

WEOS.network.nodeCount;

i++

){

WEOS.network.nodes.push(

new THREE.Vector3()

);

}

// ======================================================================
// END SECTION : 124
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 125 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.createNode=

function(

latitude,

longitude

){

const position=

new THREE.Vector3();

position

.setFromSphericalCoords(

WEOS.globe.radius+

1,

WEOS.utils.degToRad(

90-latitude

),

WEOS.utils.degToRad(

longitude+180

)

);

WEOS.network.nodes.push(

position

);

};

// ======================================================================
// END SECTION : 125
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 126 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.createNodes=

function(

locations

){

for(

const location

of

locations

){

WEOS.network.createNode(

location.latitude,

location.longitude

);

}

};

// ======================================================================
// END SECTION : 126
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 127 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.clear=

function(){

WEOS.network.nodes

.length=

0;

WEOS.network.links

.length=

0;

WEOS.network.group

.clear();

};

// ======================================================================
// END SECTION : 127
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 128 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.dispose=

function(){

WEOS.network.clear();

WEOS.network.group

.removeFromParent();

WEOS.network.material

.dispose();

WEOS.network.nodes=

[];

WEOS.network.links=

[];

};

// ======================================================================
// END SECTION : 128
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 129 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.update=

function(){

if(

!WEOS.network.group

){

return;

}

WEOS.network.group

.rotation.y+=

0.0008;

};

// ======================================================================
// END SECTION : 129
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 130 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.animate=

function(){

if(

!WEOS.network.group

){

return;

}

WEOS.network.update();

requestAnimationFrame(

WEOS.network.animate

);

};

// ======================================================================
// END SECTION : 130
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 131 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.start=

function(){

if(

WEOS.network.running

){

return;

}

WEOS.network.running=

true;

requestAnimationFrame(

WEOS.network.animate

);

};

// ======================================================================
// END SECTION : 131
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 132 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.stop=

function(){

WEOS.network.running=

false;

};

WEOS.network.toggle=

function(){

WEOS.network.running

?

WEOS.network.stop()

:

WEOS.network.start();

};

// ======================================================================
// END SECTION : 132
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 133 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.initialize=

WEOS.utils.once(

WEOS.network.initialize

);

WEOS.network.initialize(

250

);

WEOS.network.start();

// ======================================================================
// END SECTION : 133
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 134 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.on(

"frame",

function(){

if(

WEOS.network.running

){

WEOS.network.update();

}

}

);

// ======================================================================
// END SECTION : 134
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 135 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.on(

"destroy",

function(){

WEOS.network.stop();

WEOS.network.dispose();

}

);

// ======================================================================
// END SECTION : 135
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 136 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.runtime.on(

"ready",

function(){

WEOS.network.initialize(

250

);

WEOS.network.start();

}

);

// ======================================================================
// END SECTION : 136
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 137 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.build=

function(

locations

){

WEOS.network.clear();

WEOS.network.createNodes(

locations

);

WEOS.network.update();

};

// ======================================================================
// END SECTION : 137
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 138 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.addNode=

function(

location

){

WEOS.network.createNode(

location.latitude,

location.longitude

);

WEOS.network.update();

};

// ======================================================================
// END SECTION : 138
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 139 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.removeNode=

function(

index

){

WEOS.network.nodes

.splice(

index,

1

);

WEOS.network.update();

};

// ======================================================================
// END SECTION : 139
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 140 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.hasNodes=

function(){

return

WEOS.network.nodes

.length>

0;

};

// ======================================================================
// END SECTION : 140
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 141 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.count=

function(){

return

WEOS.network.nodes

.length;

};

// ======================================================================
// END SECTION : 141
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 142 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.isEmpty=

function(){

return

WEOS.network.nodes

.length===

0;

};

// ======================================================================
// END SECTION : 142
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 143 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.getNode=

function(

index

){

return

WEOS.network.nodes[

index

];

};

// ======================================================================
// END SECTION : 143
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 144 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.getNodes=

function(){

return

WEOS.network.nodes;

};

// ======================================================================
// END SECTION : 144
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 145 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.forEach=

function(

callback

){

WEOS.network.nodes

.forEach(

callback

);

};

// ======================================================================
// END SECTION : 145
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 146 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.map=

function(

callback

){

return

WEOS.network.nodes

.map(

callback

);

};

// ======================================================================
// END SECTION : 146
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 147 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.filter=

function(

callback

){

return

WEOS.network.nodes

.filter(

callback

);

};

// ======================================================================
// END SECTION : 147
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 148 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.find=

function(

callback

){

return

WEOS.network.nodes

.find(

callback

);

};

// ======================================================================
// END SECTION : 148
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 149 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.reduce=

function(

callback,

initialValue

){

return

WEOS.network.nodes

.reduce(

callback,

initialValue

);

};

// ======================================================================
// END SECTION : 149
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 150 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.some=

function(

callback

){

return

WEOS.network.nodes

.some(

callback

);

};

// ======================================================================
// END SECTION : 150
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 151 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.every=

function(

callback

){

return

WEOS.network.nodes

.every(

callback

);

};

// ======================================================================
// END SECTION : 151
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 152 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.clone=

function(){

return

WEOS.network.nodes

.slice();

};

// ======================================================================
// END SECTION : 152
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 153 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.first=

function(){

return

WEOS.network.nodes[

0

];

};

// ======================================================================
// END SECTION : 153
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 154 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.last=

function(){

return

WEOS.network.nodes[

WEOS.network.nodes

.length-1

];

};

// ======================================================================
// END SECTION : 154
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 155 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.random=

function(){

return

WEOS.network.nodes[

Math.floor(

Math.random()*

WEOS.network.nodes

.length

)

];

};

// ======================================================================
// END SECTION : 155
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 156 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.indexOf=

function(

node

){

return

WEOS.network.nodes

.indexOf(

node

);

};

// ======================================================================
// END SECTION : 156
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 157 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.includes=

function(

node

){

return

WEOS.network.nodes

.includes(

node

);

};

// ======================================================================
// END SECTION : 157
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 158 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.push=

function(

node

){

WEOS.network.nodes

.push(

node

);

return

WEOS.network.nodes

.length;

};

// ======================================================================
// END SECTION : 158
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 159 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.pop=

function(){

return

WEOS.network.nodes

.pop();

};

// ======================================================================
// END SECTION : 159
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 160 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.shift=

function(){

return

WEOS.network.nodes

.shift();

};

// ======================================================================
// END SECTION : 160
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 161 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.unshift=

function(

node

){

return

WEOS.network.nodes

.unshift(

node

);

};

// ======================================================================
// END SECTION : 161
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 162 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.splice=

function(

start,

deleteCount,

...items

){

return

WEOS.network.nodes

.splice(

start,

deleteCount,

...items

);

};

// ======================================================================
// END SECTION : 162
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 163 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.slice=

function(

start,

end

){

return

WEOS.network.nodes

.slice(

start,

end

);

};

// ======================================================================
// END SECTION : 163
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 164 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.concat=

function(

...arrays

){

return

WEOS.network.nodes

.concat(

...arrays

);

};

// ======================================================================
// END SECTION : 164
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 165 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.reverse=

function(){

return

WEOS.network.nodes

.reverse();

};

// ======================================================================
// END SECTION : 165
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 166 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.sort=

function(

compareFn

){

return

WEOS.network.nodes

.sort(

compareFn

);

};

// ======================================================================
// END SECTION : 166
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 167 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.clearNodes=

function(){

WEOS.network.nodes

.length=

0;

return

WEOS.network.nodes;

};

// ======================================================================
// END SECTION : 167
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 168 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.reset=

function(){

WEOS.network.clear();

WEOS.network.nodes=

[];

WEOS.network.links=

[];

};

// ======================================================================
// END SECTION : 168
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 169 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkCount=

function(){

return

WEOS.network.links

.length;

};

// ======================================================================
// END SECTION : 169
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 170 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.hasLinks=

function(){

return

WEOS.network.links

.length>

0;

};

// ======================================================================
// END SECTION : 170
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 171 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.getLinks=

function(){

return

WEOS.network.links;

};

// ======================================================================
// END SECTION : 171
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 172 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.firstLink=

function(){

return

WEOS.network.links[

0

];

};

// ======================================================================
// END SECTION : 172
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 173 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.lastLink=

function(){

return

WEOS.network.links[

WEOS.network.links

.length-1

];

};

// ======================================================================
// END SECTION : 173
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 174 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.forEachLink=

function(

callback

){

WEOS.network.links

.forEach(

callback

);

};

// ======================================================================
// END SECTION : 174
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 175 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.mapLinks=

function(

callback

){

return

WEOS.network.links

.map(

callback

);

};

// ======================================================================
// END SECTION : 175
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 176 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.filterLinks=

function(

callback

){

return

WEOS.network.links

.filter(

callback

);

};

// ======================================================================
// END SECTION : 176
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 177 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.findLink=

function(

callback

){

return

WEOS.network.links

.find(

callback

);

};

// ======================================================================
// END SECTION : 177
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 178 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.someLink=

function(

callback

){

return

WEOS.network.links

.some(

callback

);

};

// ======================================================================
// END SECTION : 178
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 179 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.everyLink=

function(

callback

){

return

WEOS.network.links

.every(

callback

);

};

// ======================================================================
// END SECTION : 179
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 180 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.reduceLinks=

function(

callback,

initialValue

){

return

WEOS.network.links

.reduce(

callback,

initialValue

);

};

// ======================================================================
// END SECTION : 180
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 181 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.cloneLinks=

function(){

return

WEOS.network.links

.slice();

};

// ======================================================================
// END SECTION : 181
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 182 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.clearLinks=

function(){

WEOS.network.links

.length=

0;

return

WEOS.network.links;

};

// ======================================================================
// END SECTION : 182
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 183 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.addLink=

function(

link

){

WEOS.network.links

.push(

link

);

return

WEOS.network.links

.length;

};

// ======================================================================
// END SECTION : 183
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 184 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.removeLink=

function(

index

){

return

WEOS.network.links

.splice(

index,

1

)[0];

};

// ======================================================================
// END SECTION : 184
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 185 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.getLink=

function(

index

){

return

WEOS.network.links[

index

];

};

// ======================================================================
// END SECTION : 185
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 186 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkIndexOf=

function(

link

){

return

WEOS.network.links

.indexOf(

link

);

};

// ======================================================================
// END SECTION : 186
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 187 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkIncludes=

function(

link

){

return

WEOS.network.links

.includes(

link

);

};

// ======================================================================
// END SECTION : 187
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 188 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkPush=

function(

link

){

WEOS.network.links

.push(

link

);

return

WEOS.network.links

.length;

};

// ======================================================================
// END SECTION : 188
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 189 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkPop=

function(){

return

WEOS.network.links

.pop();

};

// ======================================================================
// END SECTION : 189
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 190 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkShift=

function(){

return

WEOS.network.links

.shift();

};

// ======================================================================
// END SECTION : 190
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 191 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkUnshift=

function(

link

){

return

WEOS.network.links

.unshift(

link

);

};

// ======================================================================
// END SECTION : 191
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 192 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkSplice=

function(

start,

deleteCount,

...links

){

return

WEOS.network.links

.splice(

start,

deleteCount,

...links

);

};

// ======================================================================
// END SECTION : 192
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 193 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkSlice=

function(

start,

end

){

return

WEOS.network.links

.slice(

start,

end

);

};

// ======================================================================
// END SECTION : 193
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 194 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkConcat=

function(

...links

){

return

WEOS.network.links

.concat(

...links

);

};

// ======================================================================
// END SECTION : 194
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 195 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkReverse=

function(){

return

WEOS.network.links

.reverse();

};

// ======================================================================
// END SECTION : 195
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 196 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkSort=

function(

compareFn

){

return

WEOS.network.links

.sort(

compareFn

);

};

// ======================================================================
// END SECTION : 196
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 197 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkClear=

function(){

WEOS.network.links

.length=

0;

return

WEOS.network.links;

};

// ======================================================================
// END SECTION : 197
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 198 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.linkReset=

function(){

WEOS.network.clearLinks();

WEOS.network.links=

[];

};

// ======================================================================
// END SECTION : 198
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 199 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.destroy=

function(){

WEOS.network.stop();

WEOS.network.dispose();

WEOS.network.reset();

};

// ======================================================================
// END SECTION : 199
// ======================================================================
  // ======================================================================
// PROJECT : WEOS
// FILE    : app.js
// SECTION : 200 START
// STATUS  : COMPLETED
// ======================================================================

WEOS.network.version=

"1.0.0";

WEOS.network.name=

"WEOS Network";

WEOS.network.author=

"WEOS";

Object.freeze(

WEOS.network

);

// ======================================================================
// END SECTION : 200
// ======================================================================
