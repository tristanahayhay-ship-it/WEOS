/* ====================================================================== */
/* PROJECT : WEOS                                                         */
/* FILE    : app.js                                                        */
/* SECTION : 001 START                                                     */
/* ====================================================================== */

"use strict";


const WEOS = {

version:"1.0.0",

state:{

ready:false,

loading:0,

fps:0,

time:0,

country:null

},

config:{

container:"globeViewport",

autoRotate:true,

rotationSpeed:0.15,

background:"#000000"

},

scene:null,

camera:null,

renderer:null,

globe:null,

controls:null,

clock:null,

events:{}

};



window.WEOS = WEOS;



WEOS.utils = {

id:function(name){

return document.getElementById(name);

},


clamp:function(value,min,max){

return Math.max(
min,
Math.min(
max,
value
)
);

},


sleep:function(time){

return new Promise(
resolve=>setTimeout(resolve,time)
);

}

};



WEOS.dom = {

init:function(){

WEOS.dom.loading =
WEOS.utils.id("loadingScreen");

WEOS.dom.progress =
WEOS.utils.id("loadingProgressBar");

WEOS.dom.percent =
WEOS.utils.id("loadingPercent");

WEOS.dom.clock =
WEOS.utils.id("utcClock");

WEOS.dom.fps =
WEOS.utils.id("fpsCounter");

WEOS.dom.connection =
WEOS.utils.id("connectionStatus");

WEOS.dom.viewport =
WEOS.utils.id("globeViewport");

}

};


/* ====================================================================== */
/* SECTION : 001 END                                                       */
/* ====================================================================== */
/* ====================================================================== */
/* PROJECT : WEOS                                                         */
/* FILE    : app.js                                                        */
/* SECTION : 002 START                                                     */
/* ====================================================================== */


WEOS.loader = {

start:function(){

WEOS.loader.progress(10);

},


progress:function(value){

WEOS.state.loading=value;

if(
WEOS.dom.progress
){

WEOS.dom.progress.style.width =
value+"%";

}


if(
WEOS.dom.percent
){

WEOS.dom.percent.textContent =
Math.floor(value)+"%";

}

},


finish:function(){

WEOS.loader.progress(100);


setTimeout(
function(){

if(
WEOS.dom.loading
){

WEOS.dom.loading.style.opacity="0";

WEOS.dom.loading.style.pointerEvents="none";

}

},
500
);

}

};



WEOS.time = {

update:function(){

const now =
new Date();


if(
WEOS.dom.clock
){

WEOS.dom.clock.textContent =
now.toISOString()
.substring(11,19)
+" UTC";

}

}

};



WEOS.fps = {

frames:0,

last:performance.now(),


update:function(){

this.frames++;


const now =
performance.now();


if(
now-this.last>=1000
){

WEOS.state.fps =
this.frames;


this.frames=0;

this.last=now;


if(
WEOS.dom.fps
){

WEOS.dom.fps.textContent =
"FPS "
+
WEOS.state.fps;

}

}

}

};


/* ====================================================================== */
/* SECTION : 002 END                                                       */
/* ====================================================================== */
/* ====================================================================== */
/* PROJECT : WEOS                                                         */
/* FILE    : app.js                                                        */
/* SECTION : 003 START                                                     */
/* ====================================================================== */


WEOS.rendererSystem = {

init:function(){

const container =
WEOS.dom.viewport;


WEOS.scene =
new THREE.Scene();


WEOS.camera =
new THREE.PerspectiveCamera(

45,

window.innerWidth /
window.innerHeight,

0.1,

1000

);


WEOS.camera.position.z = 300;



WEOS.renderer =
new THREE.WebGLRenderer({

antialias:true,

alpha:true

});


WEOS.renderer.setPixelRatio(
window.devicePixelRatio
);


WEOS.renderer.setSize(

window.innerWidth,

window.innerHeight

);



if(container){

container.appendChild(
WEOS.renderer.domElement
);

}



WEOS.scene.background =
new THREE.Color(
WEOS.config.background
);



WEOS.clock =
new THREE.Clock();



},



resize:function(){


if(
!WEOS.camera ||
!WEOS.renderer
){

return;

}



WEOS.camera.aspect =
window.innerWidth /
window.innerHeight;


WEOS.camera.updateProjectionMatrix();


WEOS.renderer.setSize(

window.innerWidth,

window.innerHeight

);



}


};



window.addEventListener(

"resize",

function(){

WEOS.rendererSystem.resize();

}

);


/* ====================================================================== */
/* SECTION : 003 END                                                       */
/* ====================================================================== */
/* ====================================================================== */
/* PROJECT : WEOS                                                         */
/* FILE    : app.js                                                        */
/* SECTION : 004 START                                                     */
/* ====================================================================== */


WEOS.globeSystem = {

init:function(){

if(
typeof Globe === "undefined"
){

return;

}


WEOS.globe =
Globe()
(
WEOS.dom.viewport
);



WEOS.globe
.globeImageUrl(
""
);



WEOS.globe
.showAtmosphere(true);



WEOS.globe
.atmosphereColor(
"#3a8fff"
);



WEOS.globe
.atmosphereAltitude(
0.25
);



WEOS.globe
.width(
window.innerWidth
);



WEOS.globe
.height(
window.innerHeight
);



},



resize:function(){

if(
WEOS.globe
){

WEOS.globe
.width(
window.innerWidth
);


WEOS.globe
.height(
window.innerHeight
);

}

}

};



WEOS.cameraSystem = {

home:function(){

if(
WEOS.camera
){

WEOS.camera.position.set(

0,

0,

300

);

}

},


look:function(){

if(
WEOS.camera
&&
WEOS.globe
){

WEOS.camera.lookAt(

0,

0,

0

);

}

}

};



/* ====================================================================== */
/* SECTION : 004 END                                                       */
/* ====================================================================== */
/* ====================================================================== */
/* PROJECT : WEOS                                                         */
/* FILE    : app.js                                                        */
/* SECTION : 005 START                                                     */
/* ====================================================================== */


WEOS.countrySystem = {

data:[],


init:function(){


this.data = [];


},



select:function(country){


WEOS.state.country =
country;


const panel =
WEOS.utils.id(
"countryPanel"
);



if(
panel
){

panel.innerHTML =
`<div class="countryTitle">
${country}
</div>`;

}



},



clear:function(){


WEOS.state.country =
null;



const panel =
WEOS.utils.id(
"countryPanel"
);



if(
panel
){

panel.innerHTML =
"";

}


}


};




WEOS.eventSystem = {


init:function(){


WEOS.events = {};



window.addEventListener(

"click",

function(event){


WEOS.events.lastClick =
event;


}

);



window.addEventListener(

"mousemove",

function(event){


WEOS.events.mouse = {

x:event.clientX,

y:event.clientY

};


}

);



},



getMouse:function(){


return WEOS.events.mouse || {

x:0,

y:0

};


}



};



/* ====================================================================== */
/* SECTION : 005 END                                                       */
/* ====================================================================== */
