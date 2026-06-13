/* SADS - 3D Orbit Viewer
   Renders Earth and the orbital path of the satellite using Three.js.
   Draws LEO/MEO/GEO paths, shadows, and animates the satellite along its trajectory.
*/

class OrbitViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    
    this.earth = null;
    this.orbitLine = null;
    this.satMesh = null;
    this.shadowMesh = null;
    
    // Orbital propagation parameters
    this.orbitRadius = 1.4; // relative to Earth radius = 1.0
    this.angle = 0;
    this.speed = 0.005;
    this.isPaused = false;
    
    this.init();
    this.animate();
  }

  init() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x020408);

    // Setup Camera
    const aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(40, aspect, 0.1, 100);
    this.camera.position.set(0, 3, 6);

    // Setup Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.shadowMap.enabled = true;
    this.container.appendChild(this.renderer.domElement);

    // Controls
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.minDistance = 1.5;
    this.controls.maxDistance = 30;

    // Light (Sun position at +X)
    const sunLight = new THREE.DirectionalLight(0xffffff, 1.5);
    sunLight.position.set(8, 0, 0);
    this.scene.add(sunLight);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.1);
    this.scene.add(ambientLight);

    // Earth (Radius = 1.0 units)
    const earthGeo = new THREE.SphereGeometry(1.0, 64, 64);
    
    // Procedural Earth material with continents representation and dark night side
    const earthMat = new THREE.MeshStandardMaterial({
      color: 0x1d3557,
      roughness: 0.8,
      metalness: 0.1
    });
    this.earth = new THREE.Mesh(earthGeo, earthMat);
    this.scene.add(this.earth);

    // Add Earth grid wireframe to make it look technical
    const gridGeo = new THREE.SphereGeometry(1.005, 32, 16);
    const gridMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.12
    });
    const earthGrid = new THREE.Mesh(gridGeo, gridMat);
    this.earth.add(earthGrid);

    // Shadow Cone (Earth shadow cylinder in -X direction)
    const shadowGeo = new THREE.CylinderGeometry(1.0, 1.0, 10.0, 32);
    shadowGeo.rotateZ(Math.PI / 2);
    const shadowMat = new THREE.MeshBasicMaterial({
      color: 0xff0055,
      transparent: true,
      opacity: 0.1,
      wireframe: true
    });
    this.shadowMesh = new THREE.Mesh(shadowGeo, shadowMat);
    this.shadowMesh.position.set(-5.0, 0, 0);
    this.scene.add(this.shadowMesh);

    // Small Satellite Mesh
    const satGeo = new THREE.SphereGeometry(0.06, 16, 16);
    const satMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff
    });
    this.satMesh = new THREE.Mesh(satGeo, satMat);
    this.scene.add(this.satMesh);

    // Add orbit line
    this.updateOrbitPath(600); // Default LEO altitude (relative units will be set)

    // Window resize
    window.addEventListener('resize', () => this.onWindowResize());
  }

  updateOrbitPath(altitudeKm) {
    if (this.orbitLine) this.scene.remove(this.orbitLine);

    // Calculate scale factor relative to Earth radius R = 6378 km
    const R_E = 6378.137;
    const radiusRatio = (R_E + altitudeKm) / R_E;
    this.orbitRadius = radiusRatio;

    // Draw circular path (equatorial plane X-Z)
    const points = [];
    const segments = 128;
    for (let i = 0; i <= segments; i++) {
      const theta = (i / segments) * 2 * Math.PI;
      points.push(new THREE.Vector3(Math.cos(theta) * this.orbitRadius, 0, Math.sin(theta) * this.orbitRadius));
    }

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.4
    });

    this.orbitLine = new THREE.Line(geometry, material);
    this.scene.add(this.orbitLine);

    // Rescale camera view if orbit is GEO or deep space
    if (this.orbitRadius > 4) {
      this.camera.position.set(0, this.orbitRadius * 1.5, this.orbitRadius * 2.5);
      this.controls.target.set(0, 0, 0);
    }
  }

  setSpeed(val) {
    this.speed = 0.002 * val;
  }

  pause(paused) {
    this.isPaused = paused;
  }

  onWindowResize() {
    this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
  }

  setTheme(isLight) {
    if (this.scene) {
      this.scene.background = new THREE.Color(isLight ? 0xf1f5f9 : 0x020408);
    }
  }

  checkEclipse() {
    // Eclipse occurs when satellite is behind Earth relative to Sun (+X direction)
    // So if sat.x < -0.2 and sat.y^2 + sat.z^2 < 1.0 (inside shadow cylinder)
    const x = this.satMesh.position.x;
    const y = this.satMesh.position.y;
    const z = this.satMesh.position.z;
    
    const isBehind = x < 0;
    const distSq = y * y + z * z;
    const inCylinder = distSq < 1.0;
    
    return isBehind && inCylinder;
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    if (!this.isPaused) {
      this.angle += this.speed;
      if (this.angle > Math.PI * 2) this.angle -= Math.PI * 2;
      
      // Update satellite position
      this.satMesh.position.set(
        Math.cos(this.angle) * this.orbitRadius,
        0,
        Math.sin(this.angle) * this.orbitRadius
      );
    }

    // Slowly rotate Earth
    if (this.earth) {
      this.earth.rotation.y += 0.001;
    }

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
