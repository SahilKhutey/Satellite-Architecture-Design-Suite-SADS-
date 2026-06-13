/* SADS - 3D Satellite Viewer
   Renders a procedurally generated 3D satellite assembly using Three.js.
   Supports exploded view, wireframe mode, and rotates/interacts with OrbitControls.
*/

class Viewer3D {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    
    // Group containing all parts
    this.satelliteGroup = null;
    
    // Individual component meshes
    this.parts = {};
    
    this.explodeFactor = 0;
    this.isWireframe = false;
    
    this.init();
    this.animate();
  }

  init() {
    // Setup Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x03050a);
    
    // Add subtle grid stars in background
    this.createStars();

    // Setup Camera
    const aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100);
    this.camera.position.set(4, 3, 5);

    // Setup Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.shadowMap.enabled = true;
    this.container.appendChild(this.renderer.domElement);

    // Setup OrbitControls
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.minDistance = 2;
    this.controls.maxDistance = 20;

    // Add Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.25);
    this.scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 1.2);
    sunLight.position.set(10, 8, 5);
    sunLight.castShadow = true;
    this.scene.add(sunLight);

    const fillLight = new THREE.DirectionalLight(0x00f0ff, 0.4);
    fillLight.position.set(-10, -5, -5);
    this.scene.add(fillLight);

    // Build Satellite
    this.satelliteGroup = new THREE.Group();
    this.scene.add(this.satelliteGroup);
    this.buildSatellite();

    // Resize handler
    window.addEventListener('resize', () => this.onWindowResize());
  }

  createStars() {
    const starCount = 300;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount * 3; i += 3) {
      // Random positions on a distant sphere
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const r = 40 + Math.random() * 20;
      
      positions[i] = r * Math.sin(phi) * Math.cos(theta);
      positions[i + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i + 2] = r * Math.cos(phi);
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.15,
      transparent: true,
      opacity: 0.8
    });

    this.starPoints = new THREE.Points(geometry, material);
    this.scene.add(this.starPoints);
  }

  buildSatellite() {
    // Materials
    const goldFoilMat = new THREE.MeshStandardMaterial({
      color: 0xd4af37,
      metalness: 0.9,
      roughness: 0.15,
      bumpScale: 0.05
    });

    const metalMat = new THREE.MeshStandardMaterial({
      color: 0x8e9aaf,
      metalness: 0.8,
      roughness: 0.2
    });

    const panelBlueMat = new THREE.MeshStandardMaterial({
      color: 0x001d3d,
      emissive: 0x000814,
      metalness: 0.9,
      roughness: 0.1,
      roughnessMap: null
    });

    const thrusterMat = new THREE.MeshStandardMaterial({
      color: 0x212529,
      metalness: 0.95,
      roughness: 0.3
    });

    const glassMat = new THREE.MeshPhysicalMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.6,
      transmission: 0.9,
      roughness: 0.1
    });

    // 1. Central Bus Structure (Main Body)
    const busGeo = new THREE.BoxGeometry(1.2, 1.2, 1.2);
    const busMesh = new THREE.Mesh(busGeo, goldFoilMat);
    busMesh.castShadow = true;
    busMesh.receiveShadow = true;
    this.satelliteGroup.add(busMesh);
    this.parts['bus'] = { mesh: busMesh, basePos: new THREE.Vector3(0, 0, 0), dir: new THREE.Vector3(0, 0, 0) };

    // 2. Solar Arrays (Extend along X-axis)
    const leftPanelGroup = new THREE.Group();
    const rightPanelGroup = new THREE.Group();

    const panelGeo = new THREE.BoxGeometry(1.6, 0.04, 0.9);
    const yokesGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.4);
    yokesGeo.rotateZ(Math.PI / 2);

    const yokeLeft = new THREE.Mesh(yokesGeo, metalMat);
    yokeLeft.position.set(-0.8, 0, 0);
    leftPanelGroup.add(yokeLeft);

    const leftPanel = new THREE.Mesh(panelGeo, panelBlueMat);
    leftPanel.position.set(-1.8, 0, 0);
    leftPanelGroup.add(leftPanel);

    const yokeRight = new THREE.Mesh(yokesGeo, metalMat);
    yokeRight.position.set(0.8, 0, 0);
    rightPanelGroup.add(yokeRight);

    const rightPanel = new THREE.Mesh(panelGeo, panelBlueMat);
    rightPanel.position.set(1.8, 0, 0);
    rightPanelGroup.add(rightPanel);

    this.satelliteGroup.add(leftPanelGroup);
    this.satelliteGroup.add(rightPanelGroup);

    this.parts['solar_panel_left'] = { mesh: leftPanelGroup, basePos: new THREE.Vector3(0, 0, 0), dir: new THREE.Vector3(-1, 0, 0) };
    this.parts['solar_panel_right'] = { mesh: rightPanelGroup, basePos: new THREE.Vector3(0, 0, 0), dir: new THREE.Vector3(1, 0, 0) };

    // 3. High Gain Antenna (Front face, +Z direction)
    const antennaGroup = new THREE.Group();
    const boomGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.5);
    boomGeo.rotateX(Math.PI / 2);
    const boom = new THREE.Mesh(boomGeo, metalMat);
    boom.position.set(0, 0, 0.85);
    antennaGroup.add(boom);

    const dishGeo = new THREE.ConeGeometry(0.4, 0.15, 32, 1, true);
    dishGeo.rotateX(-Math.PI / 2);
    const dish = new THREE.Mesh(dishGeo, metalMat);
    dish.position.set(0, 0, 1.1);
    antennaGroup.add(dish);

    const subReflectorGeo = new THREE.SphereGeometry(0.06, 16, 16);
    const subReflector = new THREE.Mesh(subReflectorGeo, metalMat);
    subReflector.position.set(0, 0, 1.25);
    antennaGroup.add(subReflector);

    this.satelliteGroup.add(antennaGroup);
    this.parts['antenna'] = { mesh: antennaGroup, basePos: new THREE.Vector3(0, 0, 0), dir: new THREE.Vector3(0, 0, 1) };

    // 4. Main Engine / Thrusters (Rear face, -Z direction)
    const engineGroup = new THREE.Group();
    const nozzleGeo = new THREE.CylinderGeometry(0.12, 0.22, 0.35, 16);
    nozzleGeo.rotateX(Math.PI / 2);
    const nozzle = new THREE.Mesh(nozzleGeo, thrusterMat);
    nozzle.position.set(0, 0, -0.78);
    engineGroup.add(nozzle);

    // Glowing plume (transparent blue cone) for simulation feedback
    const plumeGeo = new THREE.ConeGeometry(0.15, 0.6, 16, 1, true);
    plumeGeo.rotateX(-Math.PI / 2);
    const plume = new THREE.Mesh(plumeGeo, glassMat);
    plume.position.set(0, 0, -1.2);
    plume.name = "thrusterPlume";
    plume.visible = false;
    engineGroup.add(plume);

    this.satelliteGroup.add(engineGroup);
    this.parts['thrusters'] = { mesh: engineGroup, basePos: new THREE.Vector3(0, 0, 0), dir: new THREE.Vector3(0, 0, -1) };

    // 5. Internals: Reaction Wheels (Visible inside when exploded)
    const wheelsGroup = new THREE.Group();
    const wheelGeo = new THREE.CylinderGeometry(0.18, 0.18, 0.08, 16);
    
    const w1 = new THREE.Mesh(wheelGeo, metalMat);
    w1.position.set(0.15, 0.15, 0);
    wheelsGroup.add(w1);
    
    const w2 = new THREE.Mesh(wheelGeo, metalMat);
    w2.rotation.x = Math.PI / 2;
    w2.position.set(-0.15, 0.15, 0.15);
    wheelsGroup.add(w2);

    const w3 = new THREE.Mesh(wheelGeo, metalMat);
    w3.rotation.z = Math.PI / 2;
    w3.position.set(0, -0.2, -0.15);
    wheelsGroup.add(w3);

    this.satelliteGroup.add(wheelsGroup);
    this.parts['reaction_wheels'] = { mesh: wheelsGroup, basePos: new THREE.Vector3(0, 0, 0), dir: new THREE.Vector3(0, 1, 0) };

    // 6. Star Trackers (Mounted on top face, +Y direction)
    const trackerGroup = new THREE.Group();
    const housingGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.25, 16);
    const housing = new THREE.Mesh(housingGeo, metalMat);
    housing.position.set(0, 0.72, 0.2);
    trackerGroup.add(housing);

    const lensGeo = new THREE.SphereGeometry(0.075, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    const lens = new THREE.Mesh(lensGeo, glassMat);
    lens.position.set(0, 0.85, 0.2);
    trackerGroup.add(lens);

    this.satelliteGroup.add(trackerGroup);
    this.parts['star_tracker'] = { mesh: trackerGroup, basePos: new THREE.Vector3(0, 0, 0), dir: new THREE.Vector3(0, 1, 0.5).normalize() };
  }

  setExplode(val) {
    this.explodeFactor = val / 100.0;
    Object.keys(this.parts).forEach(key => {
      const part = this.parts[key];
      // Translate the part along its direction vector
      const dist = this.explodeFactor * 1.5;
      part.mesh.position.copy(part.basePos).addScaledVector(part.dir, dist);
    });
  }

  setWireframe(enabled) {
    this.isWireframe = enabled;
    this.scene.traverse((child) => {
      if (child.isMesh && child.name !== "thrusterPlume") {
        child.material.wireframe = enabled;
      }
    });
  }

  fireThruster(active) {
    const plume = this.scene.getObjectByName("thrusterPlume");
    if (plume) {
      plume.visible = active;
    }
  }

  onWindowResize() {
    this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
  }

  setTheme(isLight) {
    if (this.scene) {
      this.scene.background = new THREE.Color(isLight ? 0xf1f5f9 : 0x03050a);
    }
    if (this.starPoints) {
      this.starPoints.visible = !isLight;
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    
    // Slow rotate satellite if not dragging
    if (this.satelliteGroup && !this.controls.state === -1) {
      this.satelliteGroup.rotation.y += 0.003;
      this.satelliteGroup.rotation.x += 0.001;
    }

    // Dynamic thruster plume scaling
    const plume = this.scene.getObjectByName("thrusterPlume");
    if (plume && plume.visible) {
      const scale = 0.85 + Math.random() * 0.3;
      plume.scale.set(scale, 1, scale);
    }

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
