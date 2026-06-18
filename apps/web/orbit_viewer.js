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
    
    // Advanced visualization elements
    this.groundStationMesh = null;
    this.laserLine = null;
    this.gsLat = 37.7749; // San Francisco default
    this.gsLon = -122.4194;
    
    this.propagatedPathPoints = null;
    this.pathStepIdx = 0;
    this.useLiveTelemetry = false;
    
    // Orbital propagation parameters (for fallback circular path)
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

    // Add Ground Station Mesh
    const gsGeo = new THREE.ConeGeometry(0.04, 0.1, 16);
    gsGeo.rotateX(Math.PI / 2);
    const gsMat = new THREE.MeshBasicMaterial({ color: 0xff3b30 });
    this.groundStationMesh = new THREE.Mesh(gsGeo, gsMat);
    
    const gsLatRad = THREE.MathUtils.degToRad(this.gsLat);
    const gsLonRad = THREE.MathUtils.degToRad(this.gsLon);
    this.groundStationMesh.position.set(
      Math.cos(gsLatRad) * Math.cos(gsLonRad),
      Math.sin(gsLatRad),
      Math.cos(gsLatRad) * Math.sin(gsLonRad)
    );
    this.groundStationMesh.lookAt(new THREE.Vector3(0, 0, 0));
    this.groundStationMesh.rotateX(Math.PI / 2);
    this.earth.add(this.groundStationMesh);

    // Add Laser Beam Line
    const laserMat = new THREE.LineBasicMaterial({ color: 0x34c759, linewidth: 2, transparent: true, opacity: 0.8 });
    const laserPoints = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, 0)];
    const laserGeo = new THREE.BufferGeometry().setFromPoints(laserPoints);
    this.laserLine = new THREE.Line(laserGeo, laserMat);
    this.laserLine.visible = false;
    this.scene.add(this.laserLine);

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
    this.updateOrbitPath(600); // Default LEO altitude

    // Window resize
    window.addEventListener('resize', () => this.onWindowResize());
  }

  updateOrbitPath(altitudeKm) {
    this.propagatedPathPoints = null; // Reset solver path
    this.useLiveTelemetry = false;
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

  updatePositionFromLatLon(latDeg, lonDeg, altKm) {
    this.useLiveTelemetry = true;
    this.propagatedPathPoints = null;
    
    const lat = THREE.MathUtils.degToRad(latDeg);
    const lon = THREE.MathUtils.degToRad(lonDeg);
    
    const R_E = 6378.137;
    const r = (R_E + altKm) / R_E;
    this.orbitRadius = r;
    
    this.satMesh.position.set(
      r * Math.cos(lat) * Math.cos(lon),
      r * Math.sin(lat),
      r * Math.cos(lat) * Math.sin(lon)
    );
  }

  drawPropagatedPath(history) {
    this.useLiveTelemetry = false;
    if (this.orbitLine) this.scene.remove(this.orbitLine);
    
    const points = [];
    const R_E = 6378.137;
    for (const step of history) {
      const pos = step.position;
      points.push(new THREE.Vector3(pos[0] / R_E, pos[2] / R_E, pos[1] / R_E)); // Swapped coordinates to match Y-up coordinate system
    }
    
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: 0x10b981,
      transparent: true,
      opacity: 0.6
    });
    
    this.orbitLine = new THREE.Line(geometry, material);
    this.scene.add(this.orbitLine);
    
    this.propagatedPathPoints = points;
    this.pathStepIdx = 0;
  }

  updateLaser() {
    if (!this.groundStationMesh || !this.satMesh || !this.laserLine) return;
    
    const gsWorldPos = new THREE.Vector3();
    this.groundStationMesh.getWorldPosition(gsWorldPos);
    
    const satPos = this.satMesh.position;
    
    const earthToGs = gsWorldPos.clone().normalize();
    const gsToSat = new THREE.Vector3().subVectors(satPos, gsWorldPos);
    
    const dot = earthToGs.dot(gsToSat.clone().normalize());
    const hasLos = dot > 0.087; // elevation angle > 5 degrees
    
    if (hasLos) {
      const points = [gsWorldPos, satPos];
      this.laserLine.geometry.setFromPoints(points);
      this.laserLine.visible = true;
      this.laserLine.material.color.setHex(0x34c759); // Green laser
    } else {
      this.laserLine.visible = false;
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
      if (this.propagatedPathPoints && this.propagatedPathPoints.length > 0) {
        this.pathStepIdx = (this.pathStepIdx + 1) % this.propagatedPathPoints.length;
        const pt = this.propagatedPathPoints[this.pathStepIdx];
        this.satMesh.position.copy(pt);
      } else if (!this.useLiveTelemetry) {
        this.angle += this.speed;
        if (this.angle > Math.PI * 2) this.angle -= Math.PI * 2;
        
        this.satMesh.position.set(
          Math.cos(this.angle) * this.orbitRadius,
          0,
          Math.sin(this.angle) * this.orbitRadius
        );
      }
    }

    // Update laser line
    this.updateLaser();

    // Slowly rotate Earth
    if (this.earth) {
      this.earth.rotation.y += 0.001;
    }

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}

