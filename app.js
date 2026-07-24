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

WEOS.events

.keyboard??

={};

WEOS.events

.keyboard[

event.code

]=

true;

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
