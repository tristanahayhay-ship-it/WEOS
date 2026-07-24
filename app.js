'use strict';

const WEOS={
scene:null,
camera:null,
renderer:null,
globe:null,
clock:null,
frames:0,
last:performance.now()
};

function init(){

const container=document.getElementById('globeViewport');

WEOS.scene=new THREE.Scene();

WEOS.camera=new THREE.PerspectiveCamera(
45,
window.innerWidth/window.innerHeight,
0.1,
2000
);

WEOS.camera.position.z=300;

WEOS.renderer=new THREE.WebGLRenderer({
antialias:true,
alpha:true
});

WEOS.renderer.setSize(
window.innerWidth,
window.innerHeight
);

container.appendChild(
WEOS.renderer.domElement
);

WEOS.globe=Globe()(container)
.globeImageUrl(
'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg'
)
.showAtmosphere(true)
.atmosphereColor('#3a8fff');

document.getElementById('connectionStatus').textContent='CONNECTED';

animate();

}

function animate(){

requestAnimationFrame(animate);

WEOS.frames++;

let now=performance.now();

if(now-WEOS.last>1000){

document.getElementById('fpsCounter').textContent=
'FPS '+WEOS.frames;

WEOS.frames=0;
WEOS.last=now;

}

document.getElementById('utcClock').textContent=
new Date().toISOString().substring(11,19)+' UTC';

WEOS.renderer.render(
WEOS.scene,
WEOS.camera
);

}

window.addEventListener('resize',()=>{
WEOS.camera.aspect=window.innerWidth/window.innerHeight;
WEOS.camera.updateProjectionMatrix();
WEOS.renderer.setSize(window.innerWidth,window.innerHeight);
});

window.addEventListener('load',()=>{
init();
document.getElementById('loadingScreen').style.display='none';
});
