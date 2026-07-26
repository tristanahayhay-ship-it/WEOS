// Khởi tạo globe 3D với Three.js
let scene, camera, renderer;
let globe, countries = {};
let selectedCountry = null;

function initGlobe() {
    // Cảnh
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e27);
    
    // Camera
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        10000
    );
    camera.position.z = 2.5;
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth - 400, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    document.getElementById('canvas-container').appendChild(renderer.domElement);
    
    // Tạo cầu địa cầu
    createGlobeGeometry();
    
    // Thêm đèn
    addLights();
    
    // Thêm các quốc gia lên bản đồ
    addCountriesMarkers();
    
    // Thêm dòng tiền
    addMoneyFlows();
    
    // Xử lý sự kiện click
    document.addEventListener('click', onGlobeClick);
    
    // Xử lý resize
    window.addEventListener('resize', onWindowResize);
    
    // Bắt đầu animation loop
    animate();
}

function createGlobeGeometry() {
    const geometry = new THREE.IcosahedronGeometry(1, 32);
    
    // Tạo material với gradient
    const canvas = document.createElement('canvas');
    canvas.width = 2048;
    canvas.height = 1024;
    const ctx = canvas.getContext('2d');
    
    // Vẽ gradient nền
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#1a3a52');
    gradient.addColorStop(0.5, '#0d1f2d');
    gradient.addColorStop(1, '#051219');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.MeshPhongMaterial({ map: texture });
    
    globe = new THREE.Mesh(geometry, material);
    scene.add(globe);
}

function addLights() {
    // Ánh sáng chính
    const light = new THREE.DirectionalLight(0xffffff, 1.2);
    light.position.set(5, 3, 5);
    scene.add(light);
    
    // Ánh sáng môi trường
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
}

function addCountriesMarkers() {
    COUNTRIES_DATA.forEach(country => {
        // Chuyển tọa độ địa lý sang 3D
        const phi = (90 - country.lat) * Math.PI / 180;
        const theta = (country.lng + 180) * Math.PI / 180;
        
        const x = Math.sin(phi) * Math.cos(theta);
        const y = Math.cos(phi);
        const z = Math.sin(phi) * Math.sin(theta);
        
        // Tạo marker
        const geometry = new THREE.SphereGeometry(0.03, 16, 16);
        const material = new THREE.MeshBasicMaterial({
            color: country.color
        });
        const marker = new THREE.Mesh(geometry, material);
        
        marker.position.set(x, y, z);
        marker.userData = country;
        
        globe.add(marker);
        countries[country.id] = marker;
    });
}

function addMoneyFlows() {
    MONEY_FLOWS.forEach(flow => {
        const fromCountry = getCountryData(flow.from);
        const toCountry = getCountryData(flow.to);
        
        // Chuyển tọa độ
        const fromPhi = (90 - fromCountry.lat) * Math.PI / 180;
        const fromTheta = (fromCountry.lng + 180) * Math.PI / 180;
        const fromX = Math.sin(fromPhi) * Math.cos(fromTheta);
        const fromY = Math.cos(fromPhi);
        const fromZ = Math.sin(fromPhi) * Math.sin(fromTheta);
        
        const toPhi = (90 - toCountry.lat) * Math.PI / 180;
        const toTheta = (toCountry.lng + 180) * Math.PI / 180;
        const toX = Math.sin(toPhi) * Math.cos(toTheta);
        const toY = Math.cos(toPhi);
        const toZ = Math.sin(toPhi) * Math.sin(toTheta);
        
        // Tạo đường dòng tiền
        const points = [];
        points.push(new THREE.Vector3(fromX, fromY, fromZ));
        
        // Thêm điểm trung gian để tạo cung
        const midX = (fromX + toX) / 2 * 1.5;
        const midY = (fromY + toY) / 2 * 1.5;
        const midZ = (fromZ + toZ) / 2 * 1.5;
        points.push(new THREE.Vector3(midX, midY, midZ));
        
        points.push(new THREE.Vector3(toX, toY, toZ));
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: flow.direction === 'export' ? 0xff3333 : 0x00ff88,
            linewidth: 2
        });
        const line = new THREE.Line(geometry, material);
        
        globe.add(line);
    });
}

function animate() {
    requestAnimationFrame(animate);
    
    // Quay cầu
    if (selectedCountry === null) {
        globe.rotation.y += 0.0001;
    }
    
    // Cập nhật dòng tiền
    updateMoneyFlowAnimation();
    
    renderer.render(scene, camera);
}

function onGlobeClick(event) {
    const mouse = new THREE.Vector2();
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mouse, camera);
    
    const intersects = raycaster.intersectObjects(globe.children);
    
    if (intersects.length > 0) {
        const object = intersects[0].object;
        if (object.userData) {
            selectedCountry = object.userData.id;
            updateCountryInfo(object.userData);
        }
    }
}

function onWindowResize() {
    camera.aspect = (window.innerWidth - 400) / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth - 400, window.innerHeight);
}

function updateMoneyFlowAnimation() {
    // Cập nhật animation dòng tiền
}