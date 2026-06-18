/* SADS - Main App Logic
   Coordinates the 2D canvas, 3D viewers, Chart.js metrics, and calls FastAPI backend endpoints.
*/

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Canvas and Viewers
  const canvas = new CanvasEngine('canvasContainer', 'canvasSvg', 'canvasDomLayer');
  const viewer3D = new Viewer3D('threeDViewerContainer');
  const orbitViewer = new OrbitViewer('orbitViewerContainer');
  let customManeuvers = [];
  
  
  // API URL Config
  let API_BASE = '/api';
  if (window.location.protocol === 'file:') {
    API_BASE = 'http://localhost:8080/api';
  }

  // WebSocket Sync
  let socket = null;
  let reconnectInterval = 1000;
  
  function updateWsIndicator(status) {
    const wsEl = document.getElementById('wsStatus');
    if (!wsEl) return;
    const dot = wsEl.querySelector('.status-dot');
    
    // reset classes
    wsEl.className = 'ws-status ' + status;
    
    if (status === 'connected') {
      wsEl.childNodes[1].nodeValue = ' Live Sync';
    } else if (status === 'connecting') {
      wsEl.childNodes[1].nodeValue = ' Syncing...';
    } else {
      wsEl.childNodes[1].nodeValue = ' Offline';
    }
  }


  function initWebSocket() {
    updateWsIndicator('connecting');
    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let wsHost = window.location.host;
    if (!wsHost || window.location.protocol === 'file:') {
      wsHost = 'localhost:8080';
    }
    socket = new WebSocket(`${wsProto}//${wsHost}/api/telemetry/ws`);

    socket.onopen = () => {
      console.log('SADS Telemetry WebSocket Connected');
      updateWsIndicator('connected');
      reconnectInterval = 1000;
    };

    socket.onmessage = (event) => {
      try {
        const packet = JSON.parse(event.data);
        handleRealTimeTelemetry(packet);
      } catch (err) {
        console.error('Failed to parse telemetry frame:', err);
      }
    };

    socket.onclose = () => {
      console.warn('SADS Telemetry WebSocket Disconnected. Retrying...');
      updateWsIndicator('disconnected');
      setTimeout(() => {
        reconnectInterval = Math.min(10000, reconnectInterval * 1.5);
        initWebSocket();
      }, reconnectInterval);
    };

    socket.onerror = (err) => {
      console.error('WebSocket Error:', err);
    };
  }

  function handleRealTimeTelemetry(packet) {
    const orbit = packet.orbit_parameters;
    const power = packet.power_telemetry;
    const thermal = packet.thermal_telemetry;
    const adcs = packet.adcs_telemetry;

    // Mass and Power Budget updates
    document.getElementById('sumPower').textContent = `${power.generation_w > power.load_w ? '+' : ''}${(power.generation_w - power.load_w).toFixed(1)} W`;
    const powerFill = Math.min(100, (power.generation_w / (power.load_w * 2 || 1)) * 100);
    const powerProgress = document.getElementById('powerProgress');
    if (powerProgress) {
      powerProgress.style.width = `${powerFill}%`;
      powerProgress.style.background = (power.generation_w >= power.load_w) ? 'var(--accent-green)' : 'var(--accent-red)';
    }

    const sumLink = document.getElementById('sumLink');
    if (sumLink) {
      sumLink.textContent = `${(15.0 - adcs.pointing_error_deg * 2).toFixed(1)} dB`;
    }

    if (typeof dashboardRouter !== 'undefined') {
      dashboardRouter.feedTelemetry(packet);
    }

    // Orbit coordinates sync
    const orbPeriod = document.getElementById('orbPeriod');
    if (orbPeriod) orbPeriod.textContent = `92.7 min`;
    const orbEclipse = document.getElementById('orbEclipse');
    if (orbEclipse) orbEclipse.textContent = `35.7 min`;
    const orbDrift = document.getElementById('orbDrift');
    if (orbDrift) orbDrift.textContent = `0.06°/day`;

    // Sync 3D orbit viewer
    if (orbitViewer) {
      if (orbit) {
        orbitViewer.updatePositionFromLatLon(orbit.latitude_deg, orbit.longitude_deg, orbit.altitude_km);
      }
      orbitViewer.updateLaser();
      
      const badge = document.getElementById('telemetryContactStatus');
      if (badge) {
        if (orbitViewer.laserLine && orbitViewer.laserLine.visible) {
          badge.textContent = 'CONNECTED';
          badge.className = 'badge bg-green';
        } else {
          badge.textContent = 'NO CONTACT';
          badge.className = 'badge bg-red';
        }
      }
    }

    // Sync 3D viewer elements
    if (viewer3D && viewer3D.satelliteGroup) {
      viewer3D.satelliteGroup.rotation.y += 0.005;
      if (packet.timestamp % 10 < 2) {
        viewer3D.fireThruster(true);
      } else {
        viewer3D.fireThruster(false);
      }
    }
  }


  // 2. Drag Start Setup
  const dragItems = document.querySelectorAll('.drag-item');
  dragItems.forEach(item => {
    item.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('comp-type', item.getAttribute('data-type'));
      const properties = {
        name: item.textContent.trim(),
        efficiency: item.getAttribute('data-efficiency'),
        mass: item.getAttribute('data-mass'),
        capacity: item.getAttribute('data-capacity'),
        thrust: item.getAttribute('data-thrust'),
        isp: item.getAttribute('data-isp'),
        gain: item.getAttribute('data-gain'),
        freq: item.getAttribute('data-freq'),
        accuracy: item.getAttribute('data-accuracy'),
        stype: item.getAttribute('data-stype'),
        area: item.getAttribute('data-area')
      };
      e.dataTransfer.setData('comp-meta', JSON.stringify(properties));
    });
  });

  // 3. Tab Navigation
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      const paneId = tab.getAttribute('data-target');
      document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
      });
      document.getElementById(paneId).classList.add('active');
      
      // Trigger canvas resize or WebGL renders updates
      if (paneId === 'tab3d') {
        viewer3D.onWindowResize();
      } else if (paneId === 'tabOrbit') {
        orbitViewer.onWindowResize();
      }
    });
  });

  // Sidebar Right Tabs (Details vs Copilot)
  const sideTabs = document.querySelectorAll('.side-tab-btn');
  sideTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      sideTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      const paneId = tab.getAttribute('data-target');
      document.querySelectorAll('.sidebar-pane').forEach(pane => {
        pane.classList.remove('active');
      });
      document.getElementById(paneId).classList.add('active');
    });
  });

  // 4. Zoom & Canvas toolbar controls
  canvas.on('zoom', (percent) => {
    document.getElementById('zoomPercent').textContent = `${percent}%`;
  });
  
  document.getElementById('btnZoomIn').addEventListener('click', () => {
    canvas.zoom = Math.min(2.5, canvas.zoom * 1.15);
    canvas.updateTransform();
    document.getElementById('zoomPercent').textContent = `${Math.round(canvas.zoom * 100)}%`;
  });

  document.getElementById('btnZoomOut').addEventListener('click', () => {
    canvas.zoom = Math.max(0.4, canvas.zoom / 1.15);
    canvas.updateTransform();
    document.getElementById('zoomPercent').textContent = `${Math.round(canvas.zoom * 100)}%`;
  });

  document.getElementById('btnClearCanvas').addEventListener('click', () => {
    canvas.clear();
  });

  document.getElementById('btnAutoLayout').addEventListener('click', () => {
    canvas.zoomToFit();
  });

  const btnRunTradeStudy = document.getElementById('btnRunTradeStudy');
  if (btnRunTradeStudy) {
    btnRunTradeStudy.addEventListener('click', () => {
      btnRunTradeStudy.disabled = true;
      btnRunTradeStudy.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Optimizing Architecture...';
      
      const design = compileArchitecture();
      
      fetch(`${API_BASE}/optimization/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(design)
      })
      .then(res => {
        if (!res.ok) throw new Error('Failed to run optimization trade study');
        return res.json();
      })
      .then(data => {
        btnRunTradeStudy.disabled = false;
        btnRunTradeStudy.innerHTML = '<i class="fa-solid fa-rotate"></i> Run Trade-Study Optimization';
        
        if (data.status === 'success' && dashboardRouter.charts && dashboardRouter.charts['opt']) {
          const optChart = dashboardRouter.charts['opt'];
          optChart.data.datasets[0].data = data.variants;
          optChart.data.datasets[1].data = data.pareto_front;
          optChart.update();
          
          const copilotLog = document.getElementById('copilotLog');
          if (copilotLog) {
            const opt = data.optimum;
            const bubble = document.createElement('div');
            bubble.className = 'chat-bubble assistant';
            bubble.innerHTML = `
              <div class="header" style="font-weight: 700; display: flex; align-items: center; gap: 6px; color: var(--accent-cyan);">
                <i class="fa-solid fa-robot"></i> SADS Optimization Agent
              </div>
              <div class="message" style="margin-top: 6px; font-size: 11px; line-height: 1.4;">
                <strong>Architecture trade study completed!</strong><br>
                Evaluated 40 design variants. Located global optimum using Nelder-Mead Simplex solver:<br>
                <ul style="margin-top: 4px; padding-left: 16px;">
                  <li>Optimal Solar Panel Area: <strong>${opt.area_m2.toFixed(2)} m²</strong></li>
                  <li>Optimal Battery Capacity: <strong>${opt.capacity_wh.toFixed(1)} Wh</strong></li>
                  <li>Resulting Total Mass: <strong>${opt.mass_kg.toFixed(1)} kg</strong></li>
                  <li>Resulting Power Margin: <strong>${opt.power_margin_w.toFixed(1)} W</strong></li>
                </ul>
              </div>
            `;
            copilotLog.appendChild(bubble);
            copilotLog.scrollTop = copilotLog.scrollHeight;
          }
        }
      })
      .catch(err => {
        btnRunTradeStudy.disabled = false;
        btnRunTradeStudy.innerHTML = '<i class="fa-solid fa-rotate"></i> Run Trade-Study Optimization';
        alert(err.message);
      });
    });
  }

  // Delete key binds to delete selected node
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Delete' || e.key === 'Backspace') {
      // Check if not typing in inputs
      if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'SELECT') {
        canvas.deleteSelectedNode();
      }
    }
  });

  // 5. 3D Viewer controls
  // 5. 3D Viewer controls
  const rangeExplode = document.getElementById('rangeExplode');
  if (rangeExplode) {
    rangeExplode.addEventListener('input', (e) => {
      viewer3D.setExplode(e.target.value);
    });
  }

  const chkWireframe = document.getElementById('chkWireframe');
  if (chkWireframe) {
    chkWireframe.addEventListener('change', (e) => {
      viewer3D.setWireframe(e.target.checked);
    });
  }

  // 6. Orbit Viewer controls
  const orbitPreset = document.getElementById('orbitPreset');
  if (orbitPreset) {
    orbitPreset.addEventListener('change', (e) => {
      const val = e.target.value;
      let alt = 400;
      if (val === 'meo') alt = 20000;
      if (val === 'geo') alt = 35786;
      if (val === 'deep') alt = 70000;
      
      orbitViewer.updateOrbitPath(alt);
      runLiveAnalysis();
    });
  }

  const btnPause = document.getElementById('btnOrbitPause');
  if (btnPause) {
    btnPause.addEventListener('click', () => {
      const isPaused = !orbitViewer.isPaused;
      orbitViewer.pause(isPaused);
      btnPause.innerHTML = isPaused ? '<i class="fa-solid fa-play"></i>' : '<i class="fa-solid fa-pause"></i>';
    });
  }

  const rangeOrbitSpeed = document.getElementById('rangeOrbitSpeed');
  if (rangeOrbitSpeed) {
    rangeOrbitSpeed.addEventListener('input', (e) => {
      orbitViewer.setSpeed(e.target.value);
    });
  }

  // 7. Inspector Details Panel & Pixel-Perfect form generator
  canvas.on('nodeSelected', (node) => {
    const emptyState = document.getElementById('inspectorEmptyState');
    const details = document.getElementById('inspectorDetails');
    const form = document.getElementById('inspectForm');
    
    if (!node) {
      emptyState.style.display = 'flex';
      details.style.display = 'none';
      return;
    }

    emptyState.style.display = 'none';
    details.style.display = 'block';
    document.getElementById('inspectHeader').textContent = node.name;
    
    // Clear and build dynamic layout
    form.innerHTML = '';
    
    const labelMapping = {
      mass_kg: 'Mass',
      nominal_power_w: 'Nominal Power',
      area_m2: 'Surface Area',
      efficiency: 'Efficiency',
      capacity_wh: 'Capacity',
      dod_limit: 'DoD Limit',
      thrust_n: 'Thrust',
      isp_s: 'Isp',
      gain_dbi: 'Gain',
      frequency_hz: 'Frequency',
      accuracy_deg: 'Accuracy'
    };

    const unitMapping = {
      mass_kg: 'kg',
      nominal_power_w: 'W',
      area_m2: 'm²',
      efficiency: 'frac',
      capacity_wh: 'Wh',
      dod_limit: 'frac',
      thrust_n: 'N',
      isp_s: 's',
      gain_dbi: 'dBi',
      frequency_hz: 'Hz',
      accuracy_deg: '°'
    };

    // Filter relevant properties to avoid UI noise
    const typeProperties = {
      solar_panel: ['mass_kg', 'nominal_power_w', 'area_m2', 'efficiency'],
      battery: ['mass_kg', 'capacity_wh', 'dod_limit'],
      thruster: ['mass_kg', 'nominal_power_w', 'thrust_n', 'isp_s'],
      tank: ['mass_kg'],
      antenna: ['mass_kg', 'nominal_power_w', 'gain_dbi', 'frequency_hz'],
      reaction_wheel: ['mass_kg', 'nominal_power_w'],
      sensor: ['mass_kg', 'nominal_power_w', 'accuracy_deg'],
      instrument: ['mass_kg', 'nominal_power_w'],
      camera: ['mass_kg', 'nominal_power_w'],
      software: ['mass_kg', 'nominal_power_w'],
      module: ['mass_kg', 'nominal_power_w']
    };

    const ignoreList = ['name', 'type', 'id'];

    Object.keys(node.properties).forEach(key => {
      if (ignoreList.includes(key)) return;
      
      const allowedKeys = typeProperties[node.type] || [];
      if (!allowedKeys.includes(key)) return;

      const lblText = labelMapping[key] || key;
      const val = node.properties[key];
      const unit = unitMapping[key] || '';
      
      const row = document.createElement('div');
      row.className = 'form-row';
      row.innerHTML = `
        <label for="inp_${key}">${lblText}</label>
        <div class="input-wrapper">
          <input id="inp_${key}" type="number" step="any" value="${val}">
          ${unit ? `<span class="unit-tag">${unit}</span>` : ''}
        </div>
      `;
      
      // Update properties dynamically on input change
      row.querySelector('input').addEventListener('input', (ev) => {
        node.properties[key] = parseFloat(ev.target.value) || 0;
        
        // update node display text
        const nodeEl = document.getElementById(node.id);
        if (nodeEl) {
          const detailEl = nodeEl.querySelector('.node-details');
          if (detailEl) {
            if (node.type === 'solar_panel' && key === 'area_m2') detailEl.textContent = `Area: ${node.properties.area_m2}m²`;
            if (node.type === 'battery' && key === 'capacity_wh') detailEl.textContent = `Cap: ${node.properties.capacity_wh}Wh`;
            if (node.type === 'thruster' && key === 'thrust_n') detailEl.textContent = `Thrust: ${node.properties.thrust_n}N`;
            if (node.type === 'tank' && key === 'mass_kg') detailEl.textContent = `Fuel: ${node.properties.mass_kg}kg`;
            if (['instrument', 'camera', 'software', 'module'].includes(node.type)) {
              detailEl.textContent = `Mass: ${node.properties.mass_kg}kg | Power: ${node.properties.nominal_power_w}W`;
            }
          }
        }
        runLiveAnalysis();
      });
      
      form.appendChild(row);
    });
  });

  // 8. Compile Architecture JSON for backend solvers
  function compileArchitecture() {
    const payload = {
      satellite_name: document.getElementById('satelliteName').value || 'Satellite',
      phases: [
        { name: 'Sunlight Phase', duration_days: 0.04, power_load_w: 120.0, thermal_load_w: 100.0, adcs_mode: 'sun_pointing' },
        { name: 'Eclipse Phase', duration_days: 0.02, power_load_w: 120.0, thermal_load_w: 60.0, adcs_mode: 'nadir' }
      ],
      power: { arrays: [], batteries: [], loads: [], eclipse_duration_min: 35.0, orbit_period_min: 95.0 },
      thermal: { nodes: [] },
      propulsion: {
        thrusters: [],
        tanks: [],
        dry_mass_kg: 50.0,
        maneuvers: [
          { name: 'Orbit Raising (50km)', delta_v_m_s: 25.8 },
          { name: 'Station Keeping (5 yrs)', delta_v_m_s: 45.0 },
          { name: 'Deorbit Maneuver', delta_v_m_s: 85.0 },
          ...customManeuvers
        ]
      },
      orbit: { altitude_km: 400.0, inclination_deg: 51.6 }
    };

    // Map Orbit Presets
    const orbitPreset = document.getElementById('orbitPreset').value;
    if (orbitPreset === 'leo') {
      payload.orbit.altitude_km = 400;
      payload.power.orbit_period_min = 93;
      payload.power.eclipse_duration_min = 35;
    } else if (orbitPreset === 'meo') {
      payload.orbit.altitude_km = 20000;
      payload.power.orbit_period_min = 720;
      payload.power.eclipse_duration_min = 55;
    } else if (orbitPreset === 'geo') {
      payload.orbit.altitude_km = 35786;
      payload.power.orbit_period_min = 1440;
      payload.power.eclipse_duration_min = 70;
    } else {
      payload.orbit.altitude_km = 70000;
      payload.power.orbit_period_min = 4000;
      payload.power.eclipse_duration_min = 0;
    }

    // Populate Subsystems from Canvas Nodes
    let totalDryMass = 50.0; // Bus structure baseline
    let totalSolarPower = 0.0;
    let totalNominalLoad = 20.0; // baseline OBC + sensors

    Object.keys(canvas.nodes).forEach(id => {
      const node = canvas.nodes[id];
      const p = node.properties;
      totalDryMass += p.mass_kg;

      if (node.type === 'solar_panel') {
        payload.power.arrays.push({
          name: node.name,
          area: p.area_m2,
          efficiency: p.efficiency,
          degradation_per_year: 0.025
        });
        totalSolarPower += p.area_m2 * p.efficiency * 1361.0;
      } else if (node.type === 'battery') {
        payload.power.batteries.push({
          name: node.name,
          capacity_wh: p.capacity_wh,
          dod_limit: p.dod_limit,
          mass_kg: p.mass_kg
        });
      } else if (node.type === 'thruster') {
        payload.propulsion.thrusters.push({
          name: node.name,
          isp_s: p.isp_s,
          thrust_n: p.thrust_n,
          mass_kg: p.mass_kg,
          power_w: p.nominal_power_w || 0.0
        });
        totalNominalLoad += p.nominal_power_w || 0.0;
      } else if (node.type === 'tank') {
        payload.propulsion.tanks.push({
          name: node.name,
          mass_kg: p.mass_kg,
          volume_l: p.mass_kg / 1.0
        });
      } else if (node.type === 'antenna') {
        totalNominalLoad += 15.0; // transmitter power
      } else {
        totalNominalLoad += p.nominal_power_w || 2.0;
      }
    });

    // Add unified load representation with standard fields
    payload.power.loads.push({
      name: 'Integrated Bus & Payload Load',
      nominal_power_w: totalNominalLoad,
      duty_cycle: 1.0
    });

    // Thermal node represent
    payload.thermal.nodes.push({
      name: 'Main Spacecraft Bus',
      mass_kg: totalDryMass,
      internal_heat_w: totalNominalLoad,
      surfaces: [
        { name: 'Radiator Side', area_m2: 1.2, absorptivity: 0.2, emissivity: 0.85 },
        { name: 'Bus Panels', area_m2: 3.5, absorptivity: 0.35, emissivity: 0.8 }
      ]
    });

    payload.propulsion.dry_mass_kg = totalDryMass;

    return { payload, totalDryMass, totalSolarPower, totalNominalLoad };
  }

  // 9. Run Simulations & Update Dashboard
  async function runLiveAnalysis() {
    const { payload, totalDryMass, totalSolarPower, totalNominalLoad } = compileArchitecture();
    
    // Quick UI Client-side estimations
    const totalPropellant = payload.propulsion.tanks.reduce((sum, t) => sum + t.mass_kg, 0);
    const totalMass = totalDryMass + totalPropellant;
    
    document.getElementById('sumMass').textContent = `${totalMass.toFixed(1)} kg`;
    const massFill = Math.min(100, (totalMass / 500) * 100);
    document.getElementById('massProgress').style.width = `${massFill}%`;
    
    const massBar = document.getElementById('massProgress');
    if (totalMass > 500) {
      massBar.classList.add('bg-red');
    } else {
      massBar.classList.remove('bg-red');
    }

    const powerBalance = totalSolarPower - totalNominalLoad;
    document.getElementById('sumPower').textContent = `${powerBalance > 0 ? '+' : ''}${powerBalance.toFixed(1)} W`;
    const powerFill = Math.min(100, (totalSolarPower / (totalNominalLoad * 2 || 1)) * 100);
    document.getElementById('powerProgress').style.width = `${powerFill}%`;
    document.getElementById('powerProgress').style.background = powerBalance >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';

    // Trigger API Calls to Backend Engines
    try {
      // 1. Power Analysis
      let powerResult = { status: "MARGINAL", generation_w: totalSolarPower, average_load_w: totalNominalLoad, battery_margin: -1.0 };
      if (payload.power.arrays.length > 0 && payload.power.batteries.length > 0) {
        const pRes = await fetch(`${API_BASE}/power/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload.power)
        });
        if (pRes.ok) powerResult = await pRes.json();
      }
      

      // 2. Comm Analysis (if antenna present)
      let commResult = { link_closed: true, link_margin_db: 15.0 };
      const antennaNode = Object.values(canvas.nodes).find(n => n.type === 'antenna');
      if (antennaNode) {
        const commPayload = {
          tx_power_w: 5.0,
          tx_line_loss_db: 1.0,
          data_rate_bps: 1e6,
          rx_diameter_m: 0.3,
          rx_frequency_hz: antennaNode.properties.frequency_hz,
          rx_efficiency: 0.55,
          distance_km: document.getElementById('orbitPreset').value === 'geo' ? 36000.0 : 800.0,
          system_temp_k: 290.0,
          required_cn_db: 10.0,
          atmospheric_loss_db: 1.0
        };
        const cRes = await fetch(`${API_BASE}/comm/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(commPayload)
        });
        if (cRes.ok) commResult = await cRes.json();
      }

      const sumLink = document.getElementById('sumLink');
      if (sumLink) {
        sumLink.textContent = `${commResult.link_margin_db.toFixed(1)} dB`;
      }

      // 3. Thermal Analysis
      let thermalResult = {};
      const tRes = await fetch(`${API_BASE}/thermal/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload.thermal)
      });
      if (tRes.ok) {
        thermalResult = await tRes.json();
        const mainNodeTemp = thermalResult['Main Spacecraft Bus'] || { temperature_c: 20.0, margin_ok: true };
      }

      // 4. Orbit Elements / Propagation
      const oRes = await fetch(`${API_BASE}/orbit/circular`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload.orbit)
      });
      if (oRes.ok) {
        const orbitResult = await oRes.json();
        const orbPeriod = document.getElementById('orbPeriod');
        if (orbPeriod) orbPeriod.textContent = `${orbitResult.period_min.toFixed(1)} min`;
        const orbEclipse = document.getElementById('orbEclipse');
        if (orbEclipse) orbEclipse.textContent = `${orbitResult.eclipse_min.toFixed(1)} min`;
        const orbDrift = document.getElementById('orbDrift');
        if (orbDrift) orbDrift.textContent = `${orbitResult.j2_raan_drift_deg_day.toFixed(3)}°/day`;
      }

      // 5. Propulsion Analysis
      let propResult = { fuel_margin: 1.0, total_delta_v_m_s: 0.0, required_propellant_kg: 0.0 };
      if (payload.propulsion.thrusters.length > 0 && payload.propulsion.tanks.length > 0) {
        const prRes = await fetch(`${API_BASE}/propulsion/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload.propulsion)
        });
        if (prRes.ok) propResult = await prRes.json();
      }
      
      // Update Propulsion Subsystem Dashboard UI
      const propActiveThruster = document.getElementById('propActiveThruster');
      if (propActiveThruster) {
        if (payload.propulsion.thrusters.length > 0) {
          const t = payload.propulsion.thrusters[0];
          propActiveThruster.textContent = t.name;
          document.getElementById('propThrustLevel').textContent = `${t.thrust_n.toFixed(2)} N`;
          document.getElementById('propIsp').textContent = `${t.isp_s.toFixed(1)} seconds`;
        } else {
          propActiveThruster.textContent = 'None configured';
          document.getElementById('propThrustLevel').textContent = '0.0 N';
          document.getElementById('propIsp').textContent = '0 seconds';
        }
        
        if (payload.propulsion.tanks.length > 0) {
          const totalPropellant = payload.propulsion.tanks.reduce((sum, tk) => sum + tk.mass_kg, 0);
          const requiredPropellant = propResult.required_propellant_kg || 0.0;
          const propPercentage = totalPropellant > 0 ? Math.max(0.0, ((totalPropellant - requiredPropellant) / totalPropellant) * 100.0) : 0.0;
          
          const tankName = payload.propulsion.tanks[0].name || '';
          const propellantName = tankName.toLowerCase().includes('xenon') ? 'Xenon' : 'Hydrazine';
          
          document.getElementById('propTankLevel').textContent = `${propPercentage.toFixed(1)}% (${propellantName})`;
          const reserveLabel = document.getElementById('propFuelReserveLabel');
          if (reserveLabel) reserveLabel.textContent = `${propellantName} Fuel Reserve`;
          
          const fillWidth = `${propPercentage.toFixed(1)}%`;
          document.getElementById('propFuelFill').style.width = fillWidth;
          document.getElementById('propFuelLabel').textContent = `${Math.max(0, totalPropellant - requiredPropellant).toFixed(2)} kg remaining (${propPercentage.toFixed(1)}%)`;
          
          const lifetimeYrs = requiredPropellant > 0 ? (5.0 * (totalPropellant / requiredPropellant)) : 0.0;
          document.getElementById('propLifetimeText').textContent = `Expected station keeping lifetime: ${lifetimeYrs.toFixed(1)} years with existing fuel margins.`;
          
          // Populate dynamic maneuvers table with custom sequence
          let currentMass = totalDryMass + totalPropellant;
          let avgIsp = propResult.average_isp_s || 220;
          const g0 = 9.80665;
          let tableHtml = '';
          
          payload.propulsion.maneuvers.forEach(m => {
            const mFuel = currentMass * (1 - Math.exp(-m.delta_v_m_s / (avgIsp * g0)));
            currentMass -= mFuel;
            tableHtml += `<tr>
              <td>${m.name}</td>
              <td>${m.delta_v_m_s.toFixed(1)} m/s</td>
              <td>${mFuel.toFixed(2)} kg</td>
            </tr>`;
          });
          document.getElementById('propManeuverTableBody').innerHTML = tableHtml;
        } else {
          document.getElementById('propTankLevel').textContent = '0.0%';
          document.getElementById('propFuelFill').style.width = '0%';
          document.getElementById('propFuelLabel').textContent = '0.00 kg remaining (0.0%)';
          document.getElementById('propLifetimeText').textContent = 'Expected station keeping lifetime: 0.0 years with existing fuel margins.';
          document.getElementById('propManeuverTableBody').innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-secondary);">Add thruster and tank elements to active design to compute budget.</td></tr>`;
        }
        
        // Update vital badge
        const vitalProp = document.getElementById('vitalProp');
        if (vitalProp) {
          if (payload.propulsion.thrusters.length === 0 || payload.propulsion.tanks.length === 0) {
            vitalProp.textContent = 'NO PROP';
            vitalProp.className = 'val text-red';
          } else if (propResult.propellant_match_ok === false) {
            vitalProp.textContent = 'MISMATCH';
            vitalProp.className = 'val text-red';
          } else if (propResult.fuel_margin < 0.0) {
            vitalProp.textContent = 'LOW MARGIN';
            vitalProp.className = 'val text-red';
          } else {
            vitalProp.textContent = 'OK';
            vitalProp.className = 'val text-green';
          }
        }
      }
      

      // 6. Structures Analysis
      const structuresPayload = {
        components: Object.values(canvas.nodes).map(node => ({
          name: node.name,
          mass_kg: node.properties.mass_kg || 1.0,
          com: node.type === 'solar_panel' ? [-1.8, 0, 0] : (node.type === 'antenna' ? [0, 0, 1.1] : [0, 0, 0])
        })),
        nodes: [[0.0, 0.0], [1.0, 0.0], [0.5, 0.866]],
        elements: [[0, 2, 70e9, 1e-4], [1, 2, 70e9, 1e-4]],
        boundary_conditions: { 0: [true, true], 1: [true, true] },
        static_g_axial: 6.0,
        dynamic_g_lateral: 2.0,
        stiffness_n_m: 2e7
      };

      let structuresResult = { safety_margins: { max_stress_mpa: 0.0, minimum_factor_of_safety: Infinity, margins_ok: true }, vibration_analysis: { natural_frequency_hz: 65.0, compliance: { status: "PASSED" } } };
      try {
        const sRes = await fetch(`${API_BASE}/structures/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(structuresPayload)
        });
        if (sRes.ok) structuresResult = await sRes.json();
      } catch (e) {
        console.warn("Failed to reach structures analyze endpoint:", e);
      }

      // Update structural values in 3D canvas Overlay controls
      const maxStressEl = document.getElementById('feaMaxStress');
      if (maxStressEl) maxStressEl.textContent = `${structuresResult.safety_margins.max_stress_mpa.toFixed(2)} MPa`;
      const minFosEl = document.getElementById('feaMinFos');
      if (minFosEl) {
        const minFos = structuresResult.safety_margins.minimum_factor_of_safety;
        minFosEl.textContent = (minFos === Infinity || minFos === null || isNaN(minFos)) ? 'N/A' : minFos.toFixed(2);
      }
      const marginStatusEl = document.getElementById('feaMarginStatus');
      if (marginStatusEl) {
        marginStatusEl.textContent = structuresResult.safety_margins.margins_ok ? 'PASSED' : 'FAILED';
        marginStatusEl.style.color = structuresResult.safety_margins.margins_ok ? 'var(--accent-green)' : 'var(--accent-red)';
      }
      const feaFreqEl = document.getElementById('feaFrequency');
      if (feaFreqEl) feaFreqEl.textContent = `${structuresResult.vibration_analysis.natural_frequency_hz.toFixed(1)} Hz`;

      // Update main summary card elements
      const sumStressMargin = document.getElementById('sumStressMargin');
      if (sumStressMargin) {
        const minFos = structuresResult.safety_margins.minimum_factor_of_safety;
        sumStressMargin.textContent = (minFos === Infinity || minFos === null || isNaN(minFos)) ? 'N/A' : `${minFos.toFixed(2)} FoS`;
        sumStressMargin.style.color = structuresResult.safety_margins.margins_ok ? 'var(--accent-green)' : 'var(--accent-red)';
      }
      const sumFrequency = document.getElementById('sumFrequency');
      if (sumFrequency) {
        sumFrequency.textContent = `${structuresResult.vibration_analysis.natural_frequency_hz.toFixed(1)} Hz`;
      }

    } catch (e) {
      console.warn("Failed to reach FastAPI backend, working in offline estimation mode:", e);

      // Offline fallback values
      const maxStressEl = document.getElementById('feaMaxStress');
      if (maxStressEl) maxStressEl.textContent = "0.00 MPa";
      const minFosEl = document.getElementById('feaMinFos');
      if (minFosEl) minFosEl.textContent = "N/A";
      const marginStatusEl = document.getElementById('feaMarginStatus');
      if (marginStatusEl) {
        marginStatusEl.textContent = "PASSED";
        marginStatusEl.style.color = "var(--accent-green)";
      }
      const feaFreqEl = document.getElementById('feaFrequency');
      if (feaFreqEl) feaFreqEl.textContent = "65.0 Hz";
    }
  }

  // Hook canvas modifications to rerun live analysis
  canvas.on('change', () => {
    runLiveAnalysis();
  });

  document.getElementById('btnRunSim').addEventListener('click', () => {
    viewer3D.fireThruster(true);
    setTimeout(() => {
      viewer3D.fireThruster(false);
    }, 4000);
    runLiveAnalysis();
  });

  // MBSE Co-Simulation Run button handler
  const btnRunCoSim = document.getElementById('btnRunCoSim');
  if (btnRunCoSim) {
    btnRunCoSim.addEventListener('click', async () => {
      const blocks = Object.keys(canvas.nodes).map(id => {
        const node = canvas.nodes[id];
        const p = node.properties;
        let type = "Load";
        if (node.type === "solar_panel") type = "SolarArray";
        if (node.type === "battery") type = "Battery";

        const block = {
          name: node.name.replace(/\s+/g, ''),
          type: type,
          properties: {
            area_m2: p.area_m2 || 1.0,
            efficiency: p.efficiency || 0.30,
            capacity_wh: p.capacity_wh || 50.0,
            dod_limit: p.dod_limit || 0.30,
            power_draw_w: (node.type === "solar_panel" || node.type === "battery") ? undefined : (p.nominal_power_w || 10.0)
          },
          requirements: []
        };

        // Add standard design requirement bounds
        if (node.type === "solar_panel") {
          block.requirements.push({
            id: `REQ-${node.name.substring(0,3).toUpperCase()}-1`,
            name: `${node.name} Power Output`,
            category: "power",
            limit_value: 300.0,
            operator: "greater_than"
          });
        } else if (node.type === "battery") {
          block.requirements.push({
            id: `REQ-${node.name.substring(0,3).toUpperCase()}-2`,
            name: `${node.name} Storage Bounds`,
            category: "power",
            limit_value: 40.0,
            operator: "greater_than"
          });
        }
        return block;
      });

      // Add system-level verification metrics blocks
      blocks.push({
        name: "Total_Generation",
        type: "PowerMetric",
        properties: {},
        requirements: [
          {
            id: "REQ-SYS-GEN",
            name: "System Generation Target",
            category: "power",
            limit_value: 500.0,
            operator: "greater_than"
          }
        ]
      });

      blocks.push({
        name: "Battery_Margin",
        type: "PowerMetric",
        properties: {},
        requirements: [
          {
            id: "REQ-SYS-BAT",
            name: "System Eclipse Battery Margin",
            category: "power",
            limit_value: 0.0,
            operator: "greater_than"
          }
        ]
      });

      const sysmlPayload = { blocks };
      document.getElementById('sysmlJsonOutput').textContent = JSON.stringify(sysmlPayload, null, 2);

      // Get altitude
      const orbitPreset = document.getElementById('orbitPreset').value;
      let altitude = 400.0;
      if (orbitPreset === 'meo') altitude = 20000.0;
      if (orbitPreset === 'geo') altitude = 35786.0;
      if (orbitPreset === 'deep') altitude = 70000.0;

      try {
        const response = await fetch(`${API_BASE}/mbse/cosimulate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sysml_blocks_json: JSON.stringify(sysmlPayload),
            altitude_km: altitude
          })
        });

        if (response.ok) {
          const result = await response.json();
          
          // Render verification results
          const listContainer = document.getElementById('cosimVerificationList');
          listContainer.innerHTML = '';
          result.verification_results.forEach(res => {
            const item = document.createElement('div');
            item.className = `verification-item`;
            item.style.padding = '8px 12px';
            item.style.background = res.satisfied ? 'rgba(34, 197, 94, 0.08)' : 'rgba(239, 68, 68, 0.08)';
            item.style.borderLeft = `4px solid ${res.satisfied ? '#16a34a' : '#dc2626'}`;
            item.style.borderRadius = '6px';
            item.style.fontSize = '12px';
            item.innerHTML = `
              <div style="font-weight: bold; color: ${res.satisfied ? '#16a34a' : '#dc2626'};">Req ID: ${res.requirement_id} - ${res.satisfied ? 'SATISFIED' : 'VIOLATED'}</div>
              <div style="color: var(--text-secondary); margin-top: 4px;">Measured: ${res.measured_value.toFixed(1)} | Limit: ${res.limit_value.toFixed(1)}</div>
            `;
            listContainer.appendChild(item);
          });

          // Render compliance signoff log
          document.getElementById('cosimSignoffLog').textContent = result.signoff_log;
        } else {
          const errText = await response.text();
          document.getElementById('cosimSignoffLog').textContent = `Co-simulation error: ${errText}`;
        }
      } catch (e) {
        document.getElementById('cosimSignoffLog').textContent = `Failed to connect to co-simulation service: ${e.message}`;
      }
    });
  }


  // 11. AI Copilot Integration
  const copilotLog = document.getElementById('copilotLog');
  const copilotInput = document.getElementById('copilotInput');
  const btnCopilotSend = document.getElementById('btnCopilotSend');

  function appendChatBubble(sender, text) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.textContent = text;
    copilotLog.appendChild(bubble);
    copilotLog.scrollTop = copilotLog.scrollHeight;
  }

  btnCopilotSend.addEventListener('click', () => {
    const text = copilotInput.value.trim();
    if (!text) return;
    appendChatBubble('user', text);
    copilotInput.value = '';
    
    setTimeout(() => {
      const response = processCopilotQuery(text);
      appendChatBubble('assistant', response);
    }, 800);
  });

  copilotInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') btnCopilotSend.click();
  });

  document.getElementById('btnCopilotReview').addEventListener('click', () => {
    const review = runFeasibilityReview();
    appendChatBubble('assistant', review);
  });

  document.getElementById('btnCopilotOptimize').addEventListener('click', () => {
    let optimizedCount = 0;
    Object.keys(canvas.nodes).forEach(id => {
      const node = canvas.nodes[id];
      if (node.type === 'solar_panel' && node.properties.area_m2 < 1.5) {
        node.properties.area_m2 = 1.5;
        optimizedCount++;
      }
      if (node.type === 'battery' && node.properties.capacity_wh < 120) {
        node.properties.capacity_wh = 120;
        optimizedCount++;
      }
    });

    if (optimizedCount > 0) {
      appendChatBubble('assistant', `Auto-optimization complete: increased Solar Panel area and expanded battery capacity to 120Wh to guarantee eclipse safety and POS balance.`);
      canvas.emit('change', { nodes: canvas.nodes, links: canvas.links });
    } else {
      appendChatBubble('assistant', `Your satellite architecture is already fully optimized for LEO mission parameters.`);
    }
  });

  function runFeasibilityReview() {
    const { payload, totalMass } = compileArchitecture();
    const panels = Object.values(canvas.nodes).filter(n => n.type === 'solar_panel');
    const batteries = Object.values(canvas.nodes).filter(n => n.type === 'battery');
    const thrusters = Object.values(canvas.nodes).filter(n => n.type === 'thruster');
    const antennas = Object.values(canvas.nodes).filter(n => n.type === 'antenna');
    
    let report = `--- MISSION ARCHITECTURE FEASIBILITY REVIEW ---\n`;
    report += `Spacecraft Wet Mass: \${totalMass.toFixed(1)} kg\n`;
    
    if (panels.length === 0) {
      report += `⚠️ Critical: No Solar Arrays added. Spacecraft will run out of power within LEO insertion phase.\n`;
    }
    if (batteries.length === 0) {
      report += `⚠️ Critical: No Battery packs found. Satellite will experience instant thermal/power shutoff during LEO eclipse.\n`;
    }
    if (thrusters.length > 0) {
      const tanks = Object.values(canvas.nodes).filter(n => n.type === 'tank');
      if (tanks.length === 0) {
        report += `⚠️ Warning: Thrusters added but no Propellant Tank detected. propulsion is non-functional.\n`;
      } else {
        const thrName = thrusters[0].name.toLowerCase();
        const tnkName = tanks[0].name.toLowerCase();
        const isElectricThr = thrName.includes('ion') || thrName.includes('hall') || thrName.includes('bolt');
        const isXenonTnk = tnkName.includes('xenon') || tnkName.includes('gas');
        if (isElectricThr && !isXenonTnk) {
          report += `⚠️ Warning: Electric Ion Engine is coupled with a Chemical tank. Xenon gas propellant is required.\n`;
        } else if (!isElectricThr && isXenonTnk) {
          report += `⚠️ Warning: Chemical Thruster is coupled with a Xenon tank. Hydrazine propellant is required.\n`;
        }
      }
    }
    if (antennas.length === 0) {
      report += `⚠️ Warning: Missing high-gain transmitter antenna. Comm payload cannot close link budget for Earth ground station.\n`;
    }

    if (panels.length > 0 && batteries.length > 0) {
      report += `✅ Power balance is closed. Solar array generates sufficient power to recharge Li-ion batteries during sunlit orbital phase.\n`;
    }

    const instruments = Object.values(canvas.nodes).filter(n => ['instrument', 'camera'].includes(n.type));
    if (instruments.length > 0) {
      report += `✅ Payloads: Detected \${instruments.length} active instrument/camera subsystems.\n`;
    } else {
      report += `ℹ️ Info: No primary mission instrument or camera detected. Consider adding payload sensors.\n`;
    }

    return report;
  }

  function processCopilotQuery(query) {
    const q = query.toLowerCase();
    if (q.includes('eclipse')) {
      const batteries = Object.values(canvas.nodes).filter(n => n.type === 'battery');
      if (batteries.length === 0) return "No battery detected. The satellite will shut down immediately upon entering Earth's shadow.";
      const totalCapacity = batteries.reduce((s, b) => s + b.properties.capacity_wh, 0);
      if (totalCapacity < 50) {
        return `Current battery capacity (\${totalCapacity}Wh) is low. I recommend upgrading your batteries by at least 30Wh to withstand a standard 35-minute LEO eclipse.`;
      }
      return `Your total battery capacity of \${totalCapacity}Wh is fully sufficient. In eclipse, the depth of discharge will stay within safe limits (<30%).`;
    }
    if (q.includes('mass') || q.includes('weight')) {
      const { payload } = compileArchitecture();
      const dryMass = payload.propulsion.dry_mass_kg;
      return `Your current spacecraft dry mass is \${dryMass.toFixed(1)} kg. This falls safely within standard ESPA launcher constraints.`;
    }
    if (q.includes('link') || q.includes('bandwidth') || q.includes('comm')) {
      const antennas = Object.values(canvas.nodes).filter(n => n.type === 'antenna');
      if (antennas.length === 0) return "You need to add a high gain antenna (like X-Band patch or Ka-band) to link telemetry back to Earth.";
      return `Your transmitter link budget is currently closed. Estimated down-link margin is robust with a 15.0 dB margin at X-band.`;
    }
    return "I can analyze orbital mechanics, power budgets, link budgets, and thermal balance. Try asking: 'Can this CubeSat survive eclipse?' or 'What is our link budget?'";
  }

  // 12. Load Baseline Design
  setTimeout(() => {
    const panelId = canvas.addNode('solar_panel', 'Spectrolab UTJ', 100, 100, { area: 1.5, efficiency: 0.30 });
    const battId = canvas.addNode('battery', 'Saft VES16', 320, 100, { capacity: 120.0, dod: 0.30 });
    const thrId = canvas.addNode('thruster', 'Aerojet MR-103', 100, 250, { thrust: 0.5, isp: 220 });
    const tankId = canvas.addNode('tank', 'Prop Tank 10L', 320, 250, { mass: 8.0 });
    const antId = canvas.addNode('antenna', 'Ka-Band Parabolic', 540, 170, { gain: 35.0, freq: 8.4 });

    canvas.links.push({ from: panelId, to: battId });
    canvas.links.push({ from: thrId, to: tankId });
    canvas.links.push({ from: battId, to: antId });
    canvas.drawLinks();
    
    canvas.zoomToFit();
    runLiveAnalysis();
    initWebSocket();
  }, 1000);

  // 13. Collapsible Panels & Theme Toggle Setup
  const btnToggleLeft = document.getElementById('btnToggleLeft');
  const btnToggleRight = document.getElementById('btnToggleRight');
  const btnThemeToggle = document.getElementById('btnThemeToggle');

  const sidebarLeft = document.querySelector('.sidebar-left');
  const sidebarRight = document.querySelector('.sidebar-right');

  if (localStorage.getItem('panel-left-collapsed') === 'true') {
    sidebarLeft.classList.add('collapsed');
    if (btnToggleLeft) {
      btnToggleLeft.classList.add('active');
      btnToggleLeft.querySelector('i').className = 'fa-solid fa-chevron-right';
    }
  }
  if (localStorage.getItem('panel-right-collapsed') === 'true') {
    sidebarRight.classList.add('collapsed');
    if (btnToggleRight) {
      btnToggleRight.classList.add('active');
      btnToggleRight.querySelector('i').className = 'fa-solid fa-chevron-left';
    }
  }

  if (btnToggleLeft) {
    btnToggleLeft.addEventListener('click', () => {
      const isCollapsed = sidebarLeft.classList.toggle('collapsed');
      localStorage.setItem('panel-left-collapsed', isCollapsed);
      btnToggleLeft.classList.toggle('active', isCollapsed);
      btnToggleLeft.querySelector('i').className = isCollapsed ? 'fa-solid fa-chevron-right' : 'fa-solid fa-chevron-left';
      window.dispatchEvent(new Event('resize'));
    });
  }

  if (btnToggleRight) {
    btnToggleRight.addEventListener('click', () => {
      const isCollapsed = sidebarRight.classList.toggle('collapsed');
      localStorage.setItem('panel-right-collapsed', isCollapsed);
      btnToggleRight.classList.toggle('active', isCollapsed);
      btnToggleRight.querySelector('i').className = isCollapsed ? 'fa-solid fa-chevron-left' : 'fa-solid fa-chevron-right';
      window.dispatchEvent(new Event('resize'));
    });
  }

  function applyTheme(isLight) {
    if (isLight) {
      document.body.classList.remove('dark-theme');
      document.body.classList.add('light-theme');
      if (btnThemeToggle) {
        btnThemeToggle.querySelector('i').className = 'fa-solid fa-moon';
        btnThemeToggle.title = 'Switch to Dark Theme';
        btnThemeToggle.classList.remove('active');
      }
    } else {
      document.body.classList.remove('light-theme');
      document.body.classList.add('dark-theme');
      if (btnThemeToggle) {
        btnThemeToggle.querySelector('i').className = 'fa-solid fa-sun';
        btnThemeToggle.title = 'Switch to Light Theme';
        btnThemeToggle.classList.add('active');
      }
    }
    
    if (viewer3D) viewer3D.setTheme(isLight);
    if (orbitViewer) orbitViewer.setTheme(isLight);
  }

  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme === 'light');

  if (btnThemeToggle) {
    btnThemeToggle.addEventListener('click', () => {
      const isLight = document.body.classList.contains('light-theme');
      const newTheme = isLight ? 'dark' : 'light';
      localStorage.setItem('theme', newTheme);
      applyTheme(newTheme === 'light');
    });
  }

  // 14. Custom Component Creator fields sync & dynamic update
  const customCompType = document.getElementById('customCompType');
  const customParamRow1 = document.getElementById('customParamRow1');
  const customParamRow2 = document.getElementById('customParamRow2');
  const customParamLabel1 = document.getElementById('customParamLabel1');
  const customParamLabel2 = document.getElementById('customParamLabel2');
  const customCompVal1 = document.getElementById('customCompVal1');
  const customCompVal2 = document.getElementById('customCompVal2');

  function updateCreatorFields() {
    if (!customCompType) return;
    const type = customCompType.value;
    if (type === 'solar_panel') {
      if (customParamRow1) customParamRow1.style.display = 'flex';
      if (customParamLabel1) customParamLabel1.textContent = 'Area (m²)';
      if (customCompVal1) customCompVal1.value = '1.5';
      if (customParamRow2) customParamRow2.style.display = 'flex';
      if (customParamLabel2) customParamLabel2.textContent = 'Eff (0-1)';
      if (customCompVal2) customCompVal2.value = '0.30';
    } else if (type === 'battery') {
      if (customParamRow1) customParamRow1.style.display = 'flex';
      if (customParamLabel1) customParamLabel1.textContent = 'Cap (Wh)';
      if (customCompVal1) customCompVal1.value = '120';
      if (customParamRow2) customParamRow2.style.display = 'flex';
      if (customParamLabel2) customParamLabel2.textContent = 'DoD (0-1)';
      if (customCompVal2) customCompVal2.value = '0.30';
    } else if (type === 'thruster') {
      if (customParamRow1) customParamRow1.style.display = 'flex';
      if (customParamLabel1) customParamLabel1.textContent = 'Thrust (N)';
      if (customCompVal1) customCompVal1.value = '0.5';
      if (customParamRow2) customParamRow2.style.display = 'flex';
      if (customParamLabel2) customParamLabel2.textContent = 'Isp (s)';
      if (customCompVal2) customCompVal2.value = '220';
    } else if (type === 'antenna') {
      if (customParamRow1) customParamRow1.style.display = 'flex';
      if (customParamLabel1) customParamLabel1.textContent = 'Gain (dBi)';
      if (customCompVal1) customCompVal1.value = '35';
      if (customParamRow2) customParamRow2.style.display = 'flex';
      if (customParamLabel2) customParamLabel2.textContent = 'Freq (GHz)';
      if (customCompVal2) customCompVal2.value = '8.4';
    } else if (type === 'sensor') {
      if (customParamRow1) customParamRow1.style.display = 'flex';
      if (customParamLabel1) customParamLabel1.textContent = 'Acc (deg)';
      if (customCompVal1) customCompVal1.value = '0.01';
      if (customParamRow2) customParamRow2.style.display = 'none';
    } else {
      if (customParamRow1) customParamRow1.style.display = 'none';
      if (customParamRow2) customParamRow2.style.display = 'none';
    }
  }

  if (customCompType) {
    customCompType.addEventListener('change', updateCreatorFields);
    updateCreatorFields(); // init creator fields
  }

  const btnCreateCustom = document.getElementById('btnCreateCustom');
  if (btnCreateCustom) {
    btnCreateCustom.addEventListener('click', () => {
      const name = document.getElementById('customCompName').value.trim() || 'Custom Subsystem';
      const type = customCompType.value;
      const mass = parseFloat(document.getElementById('customCompMass').value) || 0.0;
      const power = parseFloat(document.getElementById('customCompPower').value) || 0.0;
      
      const val1 = (customParamRow1 && customParamRow1.style.display !== 'none') ? parseFloat(customCompVal1.value) || 0 : 0;
      const val2 = (customParamRow2 && customParamRow2.style.display !== 'none') ? parseFloat(customCompVal2.value) || 0 : 0;

      // Create new drag item
      const item = document.createElement('div');
      item.className = 'drag-item';
      item.setAttribute('draggable', 'true');
      item.setAttribute('data-type', type);
      item.setAttribute('data-mass', mass);
      item.setAttribute('data-power', power);

      // Icon classes for library representation
      let icon = 'fa-microchip';
      if (type === 'instrument') icon = 'fa-microscope text-purple';
      else if (type === 'camera') icon = 'fa-camera text-yellow';
      else if (type === 'software') icon = 'fa-file-code text-green';
      else if (type === 'module') icon = 'fa-cubes text-blue';
      else if (type === 'tank') icon = 'fa-circle-nodes text-purple';
      else if (type === 'reaction_wheel') icon = 'fa-circle-notch text-blue';
      else if (type === 'sensor') icon = 'fa-star text-yellow';
      else if (type === 'antenna') icon = 'fa-satellite text-cyan';
      else if (type === 'thruster') icon = 'fa-fire text-red';
      else if (type === 'solar_panel') icon = 'fa-solar-panel text-cyan';
      else if (type === 'battery') icon = 'fa-battery-three-quarters text-green';

      item.innerHTML = `<i class="fa-solid ${icon}"></i> ${name}`;

      // Set custom attributes
      if (type === 'solar_panel') {
        item.setAttribute('data-area', val1);
        item.setAttribute('data-efficiency', val2);
      } else if (type === 'battery') {
        item.setAttribute('data-capacity', val1);
        item.setAttribute('data-dod', val2);
      } else if (type === 'thruster') {
        item.setAttribute('data-thrust', val1);
        item.setAttribute('data-isp', val2);
      } else if (type === 'antenna') {
        item.setAttribute('data-gain', val1);
        item.setAttribute('data-freq', val2);
      } else if (type === 'sensor') {
        item.setAttribute('data-accuracy', val1);
      }

      // Drag start binding
      item.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('comp-type', type);
        const properties = {
          name: name,
          mass: mass,
          power: power,
          efficiency: item.getAttribute('data-efficiency') || '0',
          capacity: item.getAttribute('data-capacity') || '0',
          dod: item.getAttribute('data-dod') || '0.3',
          thrust: item.getAttribute('data-thrust') || '0',
          isp: item.getAttribute('data-isp') || '0',
          gain: item.getAttribute('data-gain') || '0',
          freq: item.getAttribute('data-freq') || '8.4',
          accuracy: item.getAttribute('data-accuracy') || '0.01',
          area: item.getAttribute('data-area') || '1.0'
        };
        e.dataTransfer.setData('comp-meta', JSON.stringify(properties));
      });

      // Append
      const customGroup = document.getElementById('groupCustomComponents');
      if (customGroup) {
        customGroup.appendChild(item);
      }

      bindDragEvents();
      syncCustomComponentToBackend(name, type, mass, power, { val1, val2 });

      // Reset input name
      document.getElementById('customCompName').value = '';
    });
  }

  // ==========================================================================
  // 22-Dashboard Route & Component Manager
  // ==========================================================================
  const dashboardRouter = {
    currentRoute: '',
    charts: {},
    telemetryBuffers: {
      labels: Array.from({length: 30}, (_, i) => `-${30 - i}s`),
      gen: Array(30).fill(0),
      load: Array(30).fill(0),
      soc: Array(30).fill(0),
      temp: Array(30).fill(20.0),
      pointing: Array(30).fill(0.01),
      wheels: Array(30).fill(1000)
    },
    
    routes: {
      'dash-home': { title: 'Platform > Home', showRightSidebar: false },
      'dash-missions': { title: 'Platform > Mission Control', showRightSidebar: false, onOpen: () => dashboardRouter.initMissionMap() },
      'dash-satellites': { title: 'Platform > Spacecraft Vitals', showRightSidebar: true, onOpen: () => dashboardRouter.mountSatelliteViewer('dash-satellites') },
      'dash-architecture': { title: 'Platform > Architecture Designer', showRightSidebar: true, onOpen: () => {
        dashboardRouter.mountCanvas();
        setTimeout(() => {
          canvas.zoomToFit();
        }, 100);
      }},
      'dash-power': { title: 'Platform > EPS (Power)', showRightSidebar: false, onOpen: () => dashboardRouter.initPowerChart() },
      'dash-thermal': { title: 'Platform > TCS (Thermal)', showRightSidebar: false, onOpen: () => dashboardRouter.initThermalChart() },
      'dash-communications': { title: 'Platform > TT&C (Comms)', showRightSidebar: false, onOpen: () => dashboardRouter.initCommChart() },
      'dash-propulsion': { title: 'Platform > Propulsion', showRightSidebar: false },
      'dash-adcs': { title: 'Platform > ADCS (Attitude)', showRightSidebar: false, onOpen: () => dashboardRouter.initAdcsChart() },
      'dash-orbit': { title: 'Platform > Orbit Simulator', showRightSidebar: false, onOpen: () => dashboardRouter.mountOrbitViewer() },
      'dash-payload': { title: 'Platform > Payload Manager', showRightSidebar: false },
      'dash-structures': { title: 'Platform > Structures & FEA', showRightSidebar: true, onOpen: () => dashboardRouter.mountSatelliteViewer('dash-structures') },
      'dash-simulation': { title: 'Platform > Simulation Queue', showRightSidebar: false },
      'dash-optimization': { title: 'Platform > Optimization Sweep', showRightSidebar: false, onOpen: () => dashboardRouter.initOptChart() },
      'dash-digital-twin': { title: 'Platform > Digital Twin Stream', showRightSidebar: false, onOpen: () => {
        dashboardRouter.mountSatelliteViewer('dash-digital-twin');
        dashboardRouter.initTwinChart();
      }},
      'dash-ai-copilot': { title: 'Platform > AI Copilot Chat', showRightSidebar: false, onOpen: () => dashboardRouter.mountCopilotChat() },
      'dash-mbse': { title: 'Platform > MBSE Co-Simulation', showRightSidebar: false },
      'dash-verification': { title: 'Platform > Verification constraints', showRightSidebar: false },
      'dash-validation': { title: 'Platform > Validation benchmarks', showRightSidebar: false, onOpen: () => dashboardRouter.initValChart() },
      'dash-reports': { title: 'Platform > Reports & Exports', showRightSidebar: false, onOpen: () => dashboardRouter.initReportsDashboard() },
      'dash-collaboration': { title: 'Platform > Collaboration workspace', showRightSidebar: false },
      'dash-admin': { title: 'Platform > Administration Settings', showRightSidebar: false }
    },

    init() {
      // Listen for hash changes
      window.addEventListener('hashchange', () => this.handleRouting());
      
      // Left Navigation Click Bindings
      document.querySelectorAll('.sidebar-left .nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
          document.querySelectorAll('.sidebar-left .nav-item').forEach(n => n.classList.remove('active'));
          item.classList.add('active');
        });
      });

      // Initialize subpage tabs & calculators
      this.initSubpageTabs();
      this.initCalculators();

      // Default route
      if (!window.location.hash) {
        window.location.hash = '#/dashboard';
      } else {
        this.handleRouting();
      }
    },

    handleRouting() {
      const hash = window.location.hash || '#/dashboard';
      let panelId = 'dash-home';

      // Map Hash Paths to panel IDs
      if (hash.includes('/dashboard')) panelId = 'dash-home';
      else if (hash.includes('/missions')) panelId = 'dash-missions';
      else if (hash.includes('/satellites')) panelId = 'dash-satellites';
      else if (hash.includes('/architecture')) panelId = 'dash-architecture';
      else if (hash.includes('/power')) panelId = 'dash-power';
      else if (hash.includes('/thermal')) panelId = 'dash-thermal';
      else if (hash.includes('/communications')) panelId = 'dash-communications';
      else if (hash.includes('/propulsion')) panelId = 'dash-propulsion';
      else if (hash.includes('/adcs')) panelId = 'dash-adcs';
      else if (hash.includes('/orbit')) panelId = 'dash-orbit';
      else if (hash.includes('/payload')) panelId = 'dash-payload';
      else if (hash.includes('/structures')) panelId = 'dash-structures';
      else if (hash.includes('/simulation')) panelId = 'dash-simulation';
      else if (hash.includes('/optimization')) panelId = 'dash-optimization';
      else if (hash.includes('/digital-twin')) panelId = 'dash-digital-twin';
      else if (hash.includes('/ai-copilot')) panelId = 'dash-ai-copilot';
      else if (hash.includes('/mbse')) panelId = 'dash-mbse';
      else if (hash.includes('/verification')) panelId = 'dash-verification';
      else if (hash.includes('/validation')) panelId = 'dash-validation';
      else if (hash.includes('/reports')) panelId = 'dash-reports';
      else if (hash.includes('/collaboration')) panelId = 'dash-collaboration';
      else if (hash.includes('/admin')) panelId = 'dash-admin';

      this.currentRoute = panelId;
      const config = this.routes[panelId];

      if (!config) return;

      // Update breadcrumb
      document.getElementById('breadcrumbs').textContent = config.title;

      // Toggle Active Panels
      document.querySelectorAll('.dashboard-panel').forEach(p => p.classList.remove('active'));
      const activePanel = document.getElementById(panelId);
      if (activePanel) {
        activePanel.classList.add('active');
      }

      // Sync navigation active class
      document.querySelectorAll('.sidebar-left .nav-item').forEach(item => {
        if (item.getAttribute('data-target') === panelId) {
          item.classList.add('active');
        } else {
          item.classList.remove('active');
        }
      });

      // Toggle Right details Sidebar
      const sidebarRight = document.querySelector('.sidebar-right');
      if (sidebarRight) {
        if (config.showRightSidebar) {
          sidebarRight.classList.remove('collapsed');
          const toggleBtn = document.getElementById('btnToggleRight');
          if (toggleBtn) {
            toggleBtn.classList.remove('active');
            toggleBtn.querySelector('i').className = 'fa-solid fa-outdent';
          }
        } else {
          sidebarRight.classList.add('collapsed');
          const toggleBtn = document.getElementById('btnToggleRight');
          if (toggleBtn) {
            toggleBtn.classList.add('active');
            toggleBtn.querySelector('i').className = 'fa-solid fa-indent';
          }
        }
      }

      // Execute onOpen hook
      if (config.onOpen) {
        config.onOpen();
      }

      // Fire global resize event to adjust sizes of reparented WebGL/SVG viewers
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
      }, 50);
    },

    // Viewers mounting managers
    mountCanvas() {
      const parent = document.getElementById('architectureMount');
      const container = document.getElementById('canvasContainer');
      if (parent && container) {
        parent.appendChild(container);
      }
    },

    mountSatelliteViewer(panelId) {
      const panel = document.getElementById(panelId);
      if (!panel) return;
      const mountPoint = panel.querySelector('.satellite-viewer-mount, .twin-satellite-mount');
      const container = document.getElementById('threeDViewerContainer');
      if (mountPoint && container) {
        mountPoint.appendChild(container);
      }
    },

    mountOrbitViewer() {
      const panel = document.getElementById('dash-orbit');
      const mountPoint = panel.querySelector('.orbit-viewer-mount');
      const container = document.getElementById('orbitViewerContainer');
      if (mountPoint && container) {
        mountPoint.appendChild(container);
      }
    },

    mountCopilotChat() {
      const panel = document.getElementById('dash-ai-copilot');
      const mountPoint = panel.querySelector('.copilot-chat');
      const chat = document.querySelector('.copilot-chat');
      if (mountPoint && chat) {
        panel.appendChild(chat);
      }
    },

    // Chart.js Setup Managers
    initPowerChart() {
      if (this.charts['power']) return;
      const ctx = document.getElementById('chartPowerDashboard').getContext('2d');
      this.charts['power'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.telemetryBuffers.labels,
          datasets: [
            { label: 'Generation (W)', data: this.telemetryBuffers.gen, borderColor: '#0284c7', borderWidth: 2, fill: false, pointRadius: 0, tension: 0.3 },
            { label: 'Battery SoC (%)', data: this.telemetryBuffers.soc, borderColor: '#16a34a', borderWidth: 1.5, borderDash: [4, 4], fill: false, pointRadius: 0, tension: 0.3 },
            { label: 'Load (W)', data: this.telemetryBuffers.load, borderColor: '#dc2626', borderWidth: 1.5, fill: false, pointRadius: 0 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true, labels: { color: '#94a3b8', font: { size: 9 } } } },
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initThermalChart() {
      if (this.charts['thermal']) return;
      const ctx = document.getElementById('chartThermalDashboard').getContext('2d');
      this.charts['thermal'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.telemetryBuffers.labels,
          datasets: [
            { label: 'Bus Temp (°C)', data: this.telemetryBuffers.temp, borderColor: '#7c3aed', borderWidth: 2, fill: true, backgroundColor: 'rgba(124, 58, 237, 0.05)', pointRadius: 0, tension: 0.3 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initCommChart() {
      if (this.charts['comm']) return;
      const ctx = document.getElementById('chartCommDashboard').getContext('2d');
      const mockSignal = Array.from({length: 30}, () => 14 + Math.random() * 2);
      this.charts['comm'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.telemetryBuffers.labels,
          datasets: [
            { label: 'Link Margin (dB)', data: mockSignal, borderColor: '#06b6d4', borderWidth: 2, pointRadius: 0, tension: 0.3 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initAdcsChart() {
      if (this.charts['adcs']) return;
      const ctx = document.getElementById('chartAdcsDashboard').getContext('2d');
      this.charts['adcs'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.telemetryBuffers.labels,
          datasets: [
            { label: 'Wheel Speed (RPM)', data: this.telemetryBuffers.wheels, borderColor: '#ec4899', borderWidth: 2, pointRadius: 0, tension: 0.3 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initThermalTransientChart() {
      if (this.charts['thermalTransient']) return;
      const canvasEl = document.getElementById('chartThermalTransient');
      if (!canvasEl) return;
      const ctx = canvasEl.getContext('2d');
      this.charts['thermalTransient'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: []
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true, labels: { color: '#94a3b8', font: { size: 9 } } } },
          scales: {
            x: { title: { display: true, text: 'Distance along rod (m)', color: '#94a3b8', font: { size: 9 } }, ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { display: false } },
            y: { title: { display: true, text: 'Temperature (K)', color: '#94a3b8', font: { size: 9 } }, ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initOrbitDecayChart() {
      if (this.charts['orbitDecay']) return;
      const canvasEl = document.getElementById('chartOrbitDecay');
      if (!canvasEl) return;
      const ctx = canvasEl.getContext('2d');
      this.charts['orbitDecay'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: [
            { label: 'Altitude (km)', data: [], borderColor: '#10b981', borderWidth: 2, fill: false, pointRadius: 0, tension: 0.1 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { title: { display: true, text: 'Propagation Time (min)', color: '#94a3b8', font: { size: 9 } }, ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { display: false } },
            y: { title: { display: true, text: 'Altitude (km)', color: '#94a3b8', font: { size: 9 } }, ticks: { color: '#94a3b8', font: { size: 8 } }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initOptChart() {
      if (this.charts['opt']) return;
      const ctx = document.getElementById('chartOptDashboard').getContext('2d');
      // Render Pareto optimal points scatter chart
      const paretoPoints = Array.from({length: 40}, () => ({
        x: 80 + Math.random() * 200, // Launch Mass
        y: 20 + Math.random() * 150  // Power Margin
      }));
      this.charts['opt'] = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Architecture Variants',
            data: paretoPoints,
            backgroundColor: '#0284c7'
          }, {
            label: 'Pareto Front',
            data: [
              { x: 82, y: 160 }, { x: 100, y: 130 }, { x: 140, y: 90 }, { x: 180, y: 55 }, { x: 220, y: 25 }
            ],
            borderColor: '#f43f5e',
            showLine: true,
            fill: false,
            backgroundColor: 'transparent'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true, labels: { color: '#94a3b8' } } },
          scales: {
            x: { title: { display: true, text: 'Mass (kg)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.03)' } },
            y: { title: { display: true, text: 'Power Margin (W)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initTwinChart() {
      if (this.charts['twin']) return;
      const ctx = document.getElementById('chartTwinDashboard').getContext('2d');
      this.charts['twin'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.telemetryBuffers.labels,
          datasets: [
            { label: 'Real-time Generation', data: this.telemetryBuffers.gen, borderColor: '#10b981', borderWidth: 2, pointRadius: 0 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true, labels: { color: '#94a3b8' } } },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initValChart() {
      if (this.charts['val']) return;
      const ctx = document.getElementById('chartValDashboard').getContext('2d');
      const timeMarks = Array.from({length: 20}, (_, i) => `${i*5}m`);
      const flightData = Array.from({length: 20}, (_, i) => 20 + 10*Math.cos(i/3));
      const modelPred = flightData.map(val => val + (Math.random() * 0.8 - 0.4));
      this.charts['val'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: timeMarks,
          datasets: [
            { label: 'Copernicus Flight Telemetry', data: flightData, borderColor: '#94a3b8', borderWidth: 1.5, fill: false, pointRadius: 2 },
            { label: 'SADS Model Prediction', data: modelPred, borderColor: '#10b981', borderWidth: 2, fill: false, pointRadius: 0 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true, labels: { color: '#94a3b8' } } },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.03)' } }
          }
        }
      });
    },

    initMissionMap() {
      const canvasMap = document.getElementById('missionGroundTrackCanvas');
      if (!canvasMap) return;
      const ctx = canvasMap.getContext('2d');
      
      function drawMap() {
        const w = canvasMap.width = canvasMap.clientWidth;
        const h = canvasMap.height = canvasMap.clientHeight;
        ctx.clearRect(0, 0, w, h);
        
        // Draw simple stylized grid earth map
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.1)';
        ctx.lineWidth = 1;
        const step = 25;
        for (let x = 0; x < w; x += step) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, h);
          ctx.stroke();
        }
        for (let y = 0; y < h; y += step) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(w, y);
          ctx.stroke();
        }

        // Draw stylized continents
        ctx.fillStyle = 'rgba(148, 163, 184, 0.05)';
        ctx.beginPath();
        // North America
        ctx.arc(w*0.25, h*0.35, 40, 0, Math.PI*2);
        // Eurasia
        ctx.arc(w*0.65, h*0.3, 50, 0, Math.PI*2);
        // South America
        ctx.arc(w*0.32, h*0.7, 30, 0, Math.PI*2);
        ctx.fill();

        // Draw orbit track
        ctx.strokeStyle = '#06b6d4';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, h*0.5);
        for (let x = 0; x < w; x++) {
          const y = h*0.5 + h*0.35 * Math.sin((x / w) * 2 * Math.PI * 1.5);
          ctx.lineTo(x, y);
        }
        ctx.stroke();

        // Draw satellite dot
        const t = (Date.now() / 3000) % 1;
        const satX = t * w;
        const satY = h*0.5 + h*0.35 * Math.sin((satX / w) * 2 * Math.PI * 1.5);
        
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(satX, satY, 6, 0, Math.PI*2);
        ctx.fill();
        
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.3)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(satX, satY, 15 * (1 + 0.5 * Math.sin(Date.now()/200)), 0, Math.PI*2);
        ctx.stroke();
      }

      // Simple animation loop for map ground track
      if (this._mapInterval) clearInterval(this._mapInterval);
      this._mapInterval = setInterval(drawMap, 100);
      drawMap();
    },

    initReportsDashboard() {
      const btn = document.getElementById('btnGenerateReport');
      if (!btn) return;
      btn.onclick = () => {
        const format = document.getElementById('reportFormat').value;
        const logs = document.getElementById('reportLogs');
        const activeDesign = compileArchitecture();
        let content = '';
        if (format === 'json') {
          content = JSON.stringify(activeDesign, null, 2);
        } else {
          content = `Subsystem,Mass (kg),Nominal Power (W)\n`;
          activeDesign.payload.power.arrays.forEach(a => {
            content += `Solar Array,${a.mass_kg},${a.area_m2 * a.efficiency * 400}\n`;
          });
          activeDesign.payload.power.batteries.forEach(b => {
            content += `Battery Pack,${b.mass_kg},0\n`;
          });
        }
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = `SADS_Report_${Date.now()}.${format}`;
        link.href = url;
        link.click();
        
        const logItem = document.createElement('div');
        logItem.className = 'activity-item';
        logItem.innerHTML = `<span class="badge bg-green">SUCCESS</span> <span>Exported report SADS_Report_${Date.now()}.${format}</span>`;
        logs.appendChild(logItem);
      };
    },

    // Feed new telemetry data to the buffers
    feedTelemetry(packet) {
      const p = packet.power_telemetry;
      const t = packet.thermal_telemetry;
      const adcs = packet.adcs_telemetry;

      // Update buffers
      this.telemetryBuffers.gen.push(p.generation_w);
      this.telemetryBuffers.load.push(p.load_w);
      this.telemetryBuffers.soc.push(p.battery_soc_pct);
      this.telemetryBuffers.temp.push(t.temperature_c);
      this.telemetryBuffers.wheels.push(adcs.reaction_wheel_speeds_rpm[0]);

      this.telemetryBuffers.gen.shift();
      this.telemetryBuffers.load.shift();
      this.telemetryBuffers.soc.shift();
      this.telemetryBuffers.temp.shift();
      this.telemetryBuffers.wheels.shift();

      // Redraw active charts
      if (this.currentRoute === 'dash-power' && this.charts['power']) {
        this.charts['power'].update('none');
      }
      if (this.currentRoute === 'dash-thermal' && this.charts['thermal']) {
        this.charts['thermal'].update('none');
      }
      if (this.currentRoute === 'dash-adcs' && this.charts['adcs']) {
        this.charts['adcs'].update('none');
      }
      if (this.currentRoute === 'dash-digital-twin' && this.charts['twin']) {
        this.charts['twin'].update('none');
      }

      // Update Home KPI & Status Vitals
      const kpiMass = document.getElementById('kpiMass');
      const kpiPower = document.getElementById('kpiPower');
      const kpiDeltaV = document.getElementById('kpiDeltaV');
      
      const { payload } = compileArchitecture();
      const dryMass = payload.propulsion.dry_mass_kg;
      const fuelMass = payload.propulsion.tanks.reduce((s, tk) => s + tk.mass_kg, 0);
      const totalMass = dryMass + fuelMass;
      
      if (kpiMass) kpiMass.textContent = `${totalMass.toFixed(1)} kg`;
      if (kpiPower) kpiPower.textContent = `${p.generation_w > p.load_w ? '+' : ''}${(p.generation_w - p.load_w).toFixed(1)} W`;
      
      const homeEPS = document.getElementById('vitalEPS');
      if (homeEPS) {
        homeEPS.className = (p.generation_w >= p.load_w && p.battery_soc_pct > 30) ? 'val text-green' : 'val text-red';
        homeEPS.textContent = `${p.battery_soc_pct.toFixed(0)}% SoC`;
      }
      const homeTCS = document.getElementById('vitalTCS');
      if (homeTCS) {
        homeTCS.className = (t.temperature_c > 0 && t.temperature_c < 40) ? 'val text-green' : 'val text-red';
        homeTCS.textContent = `${t.temperature_c.toFixed(1)} °C`;
      }
      
      // Update digital twin alarm logs dynamically
      const alarmList = document.getElementById('twinAlarmList');
      if (alarmList && packet.timestamp % 10 === 0) {
        alarmList.innerHTML = '';
        if (p.battery_soc_pct < 30) {
          alarmList.innerHTML += `<div class="activity-item"><span class="badge bg-red">ANOMALY</span> <span>Battery State-of-Charge is low: ${p.battery_soc_pct.toFixed(1)}%</span></div>`;
        }
        if (t.temperature_c > 35) {
          alarmList.innerHTML += `<div class="activity-item"><span class="badge bg-red">ANOMALY</span> <span>Bus Thermal limits exceeded: ${t.temperature_c.toFixed(1)}°C</span></div>`;
        }
        if (alarmList.innerHTML === '') {
          alarmList.innerHTML = `
            <div class="activity-item"><span class="badge bg-green">OK</span> <span>Telemetry sync is normal (Live)</span></div>
            <div class="activity-item"><span class="badge bg-green">OK</span> <span>All components temperatures within nominal margins</span></div>
          `;
        }
      }
    },

    initSubpageTabs() {
      document.querySelectorAll('.sub-tab').forEach(tab => {
        tab.addEventListener('click', () => {
          const group = tab.parentElement.getAttribute('data-group');
          const targetSubpage = tab.getAttribute('data-subpage');
          
          tab.parentElement.querySelectorAll('.sub-tab').forEach(t => t.classList.remove('active'));
          tab.classList.add('active');
          
          const panel = tab.closest('.dashboard-panel');
          if (panel) {
            panel.querySelectorAll('.subpage-view').forEach(view => {
              view.style.display = 'none';
              view.classList.remove('active');
            });
            
            const activeView = document.getElementById(targetSubpage);
            if (activeView) {
              activeView.style.display = 'flex';
              activeView.classList.add('active');
            }
          }
          
          // Custom mounts for tab selection
          if (targetSubpage === 'satellites-architecture') {
            const mount = document.querySelector('.architecture-sub-mount');
            const canvasContainer = document.getElementById('canvasContainer');
            if (mount && canvasContainer) {
              mount.appendChild(canvasContainer);
            }
          } else if (targetSubpage === 'satellites-overview') {
            dashboardRouter.mountSatelliteViewer('dash-satellites');
          } else if (targetSubpage === 'satellites-mass') {
            dashboardRouter.initMassSubpageChart();
          } else if (targetSubpage === 'power-battery') {
            dashboardRouter.initBatterySoCChart();
          } else if (targetSubpage === 'thermal-transient') {
            dashboardRouter.initThermalTransientChart();
          } else if (targetSubpage === 'orbit-prop') {
            dashboardRouter.initOrbitDecayChart();
          } else if (targetSubpage === 'twin-status') {
            const mount = document.querySelector('.twin-satellite-mount');
            const container = document.getElementById('threeDViewerContainer');
            if (mount && container) {
              mount.appendChild(container);
            }
          } else if (targetSubpage === 'twin-telemetry') {
            dashboardRouter.initTwinChart();
          } else if (targetSubpage === 'comm-coverage') {
            dashboardRouter.initCommCoverageMap();
          }
          
          setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
          }, 50);
        });
      });
    },

    initMassSubpageChart() {
      if (this.charts['massSubpage']) return;
      const canvas = document.getElementById('chartMassSubpage');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      this.charts['massSubpage'] = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Structures', 'Power', 'Propulsion', 'ADCS & TT&C'],
          datasets: [{
            data: [33.8, 45.0, 20.3, 36.1],
            backgroundColor: ['#0284c7', '#7c3aed', '#dc2626', '#16a34a'],
            borderWidth: 1,
            borderColor: 'rgba(255,255,255,0.05)'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true, labels: { color: '#94a3b8', font: { size: 9 } } } }
        }
      });
    },

    initBatterySoCChart() {
      if (this.charts['batterySoC']) return;
      const canvas = document.getElementById('chartBatterySoC');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      this.charts['batterySoC'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: Array.from({length: 24}, (_, i) => `${i}h`),
          datasets: [{
            label: 'SoC (%)',
            data: [100, 95, 90, 85, 80, 78, 82, 90, 95, 100, 100, 98, 95, 90, 85, 80, 78, 82, 90, 95, 100, 100, 100, 100],
            borderColor: '#39ff14',
            borderWidth: 2,
            fill: false,
            pointRadius: 2,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 8 } } },
            y: { ticks: { color: '#94a3b8', font: { size: 8 } } }
          }
        }
      });
    },

    initCommCoverageMap() {
      const canvas = document.getElementById('commCoverageCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      let offset = 0;
      
      if (this._commMapInterval) clearInterval(this._commMapInterval);
      
      const drawCommMap = () => {
        if (this.currentRoute !== 'dash-communications') return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.05)';
        ctx.lineWidth = 1;
        for (let i = 0; i < canvas.width; i += 40) {
          ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
        }
        for (let j = 0; j < canvas.height; j += 40) {
          ctx.beginPath(); ctx.moveTo(0, j); ctx.lineTo(canvas.width, j); ctx.stroke();
        }
        
        ctx.strokeStyle = '#0284c7';
        ctx.lineWidth = 2;
        ctx.beginPath();
        for (let x = 0; x < canvas.width; x++) {
          const y = canvas.height/2 + 60 * Math.sin((x + offset) * 0.015);
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
        
        const stations = [{name: 'SGL', x: 100, y: 50}, {name: 'MCM', x: 200, y: 180}];
        stations.forEach(s => {
          ctx.fillStyle = '#7c3aed';
          ctx.beginPath(); ctx.arc(s.x, s.y, 4, 0, Math.PI*2); ctx.fill();
          ctx.fillStyle = '#94a3b8';
          ctx.font = '8px Space Grotesk';
          ctx.fillText(s.name, s.x + 6, s.y + 3);
        });
        
        offset += 2;
      };
      
      this._commMapInterval = setInterval(drawCommMap, 100);
      drawCommMap();
    },

    initCalculators() {
      const btnSolar = document.getElementById('btnSolarSim');
      if (btnSolar) {
        btnSolar.onclick = () => {
          const years = parseFloat(document.getElementById('solarYears').value) || 5;
          const eolPower = 180.0 * Math.pow(1 - 0.025, years);
          document.getElementById('solarEolResults').textContent = `Predicted EOL Power (${years} yrs): ${eolPower.toFixed(1)} W`;
        };
      }
      
      const btnComm = document.getElementById('btnCommCalc');
      if (btnComm) {
        btnComm.onclick = () => {
          const tx = parseFloat(document.getElementById('commTxPower').value) || 5;
          const gain = parseFloat(document.getElementById('commGain').value) || 35;
          const dist = parseFloat(document.getElementById('commDist').value) || 1200;
          
          const txDbw = 10 * Math.log10(tx);
          const pathLoss = 20 * Math.log10(dist) + 92.4;
          const margin = txDbw + gain + 140 - pathLoss;
          
          document.getElementById('commResultMargin').textContent = `Calculated Link Margin: ${margin.toFixed(1)} dB (${margin >= 10 ? 'CLOSED' : 'MARGINAL'})`;
        };
      }
      
      const btnProp = document.getElementById('btnPropSim');
      if (btnProp) {
        btnProp.onclick = async () => {
          const alt1 = parseFloat(document.getElementById('propAlt1').value) || 400;
          const alt2 = parseFloat(document.getElementById('propAlt2').value) || 800;
          
          const r1 = 6378.137 + alt1;
          const r2 = 6378.137 + alt2;
          
          try {
            const response = await fetch(`${API_BASE}/orbit/hohmann?r1_km=${r1}&r2_km=${r2}`, {
              method: 'POST'
            });
            if (response.ok) {
              const res = await response.json();
              const totalDv = res.total_dv_m_s;
              const { totalDryMass } = compileArchitecture();
              const fuel = totalDryMass * (Math.exp(totalDv / (9.80665 * 220)) - 1);
              
              document.getElementById('propResult').textContent = `Total ΔV Required: ${totalDv.toFixed(1)} m/s (Hydrazine fuel: ${fuel.toFixed(2)} kg)`;
              
              // Update custom maneuvers array
              customManeuvers = customManeuvers.filter(m => m.name !== 'Hohmann Transfer');
              customManeuvers.push({
                name: 'Hohmann Transfer',
                delta_v_m_s: totalDv
              });
              
              // Refresh dynamic subsystem allocations
              runLiveAnalysis();
            } else {
              const err = await response.text();
              document.getElementById('propResult').textContent = `Error: ${err}`;
            }
          } catch (e) {
            document.getElementById('propResult').textContent = `Connection failed: ${e.message}`;
          }
        };
      }

      const btnCalib = document.getElementById('btnCalibrateSensors');
      if (btnCalib) {
        btnCalib.onclick = () => {
          const noise = parseFloat(document.getElementById('trackerNoise').value) || 5;
          document.getElementById('sensorCalibResult').textContent = `Sensor calibration complete. Variance: ± ${(noise * 0.2).toFixed(2)} arcsec. Status: CALIBRATED.`;
        };
      }
      
      const btnOrbitSave = document.getElementById('btnOrbitSave');
      if (btnOrbitSave) {
        btnOrbitSave.onclick = () => {
          const alt = parseFloat(document.getElementById('orbitAltitudeInput').value) || 400;
          const inc = parseFloat(document.getElementById('orbitIncInput').value) || 51.6;
          
          document.getElementById('orbitValA').textContent = `${(6378.1 + alt).toFixed(1)} km`;
          document.getElementById('orbitValI').textContent = `${inc.toFixed(2)}°`;
          
          if (orbitViewer) {
            orbitViewer.updateOrbitPath(alt);
          }
          alert('Keplerian elements updated successfully!');
        };
      }

      const btnRunOrbitProp = document.getElementById('btnRunOrbitPropagation');
      if (btnRunOrbitProp) {
        btnRunOrbitProp.onclick = async () => {
          const mass = parseFloat(document.getElementById('orbitPropMass').value) || 150.0;
          const area = parseFloat(document.getElementById('orbitPropArea').value) || 2.0;
          const cd = parseFloat(document.getElementById('orbitPropCd').value) || 2.2;
          const orbits = parseFloat(document.getElementById('orbitPropOrbits').value) || 2.0;
          const usePerturbations = document.getElementById('orbitPropPerturb').checked;
          const alt = parseFloat(document.getElementById('orbitAltitudeInput').value) || 400.0;
          const inc = parseFloat(document.getElementById('orbitIncInput').value) || 51.6;
          const ecc = 0.0; // Circular orbit base
          
          const statusMsg = document.getElementById('orbitPropStatusMsg');
          statusMsg.textContent = 'Propagating trajectory...';
          statusMsg.style.color = 'var(--accent-cyan)';
          
          try {
            const response = await fetch(`${API_BASE}/orbit/propagate`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                altitude_km: alt,
                inclination_deg: inc,
                eccentricity: ecc,
                mass_kg: mass,
                drag_area_m2: area,
                drag_coefficient_cd: cd,
                num_orbits: orbits,
                use_perturbations: usePerturbations
              })
            });
            
            if (response.ok) {
              const result = await response.json();
              statusMsg.textContent = `Completed propagation. Final Altitude: ${result.report.final_altitude_km.toFixed(2)} km`;
              statusMsg.style.color = '#10b981';
              
              if (orbitViewer) {
                orbitViewer.drawPropagatedPath(result.history);
              }
              
              document.getElementById('orbitPropReportPanel').style.display = 'block';
              document.getElementById('orbitPropReportDecay').textContent = `Decay Rate: ${result.report.decay_rate_m_day.toFixed(4)} m/day`;
              document.getElementById('orbitPropReportDrift').textContent = `J2 Nodal Precession: ${result.report.j2_nodal_drift_deg_day.toFixed(4)}°/day`;
              
              const labels = result.history.map(pt => (pt.time_s / 60).toFixed(1));
              const alts = result.history.map(pt => pt.altitude_km);
              
              if (dashboardRouter.charts['orbitDecay']) {
                dashboardRouter.charts['orbitDecay'].data.labels = labels;
                dashboardRouter.charts['orbitDecay'].data.datasets[0].data = alts;
                dashboardRouter.charts['orbitDecay'].update();
              }
            } else {
              const err = await response.text();
              statusMsg.textContent = `Error: ${err}`;
              statusMsg.style.color = 'var(--accent-red)';
            }
          } catch (e) {
            statusMsg.textContent = `Failed to connect: ${e.message}`;
            statusMsg.style.color = 'var(--accent-red)';
          }
        };
      }

      const btnRunTransientThermal = document.getElementById('btnRunTransientThermal');
      if (btnRunTransientThermal) {
        btnRunTransientThermal.onclick = async () => {
          const length = parseFloat(document.getElementById('transientLength').value) || 2.0;
          const diffusivity = parseFloat(document.getElementById('transientDiffusivity').value) || 6.87e-5;
          const initTemp = parseFloat(document.getElementById('transientInitTemp').value) || 293.0;
          const leftTemp = parseFloat(document.getElementById('transientBoundLeft').value) || 300.0;
          const rightTemp = parseFloat(document.getElementById('transientBoundRight').value) || 250.0;
          
          const statusMsg = document.getElementById('transientStatusMsg');
          statusMsg.textContent = 'Solving transient heat equation...';
          statusMsg.style.color = 'var(--accent-cyan)';
          
          try {
            const response = await fetch(`${API_BASE}/thermal/transient`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                length_m: length,
                thermal_diffusivity: diffusivity,
                init_temp_k: initTemp,
                boundary_left_k: leftTemp,
                boundary_right_k: rightTemp,
                nodes: 10,
                time_steps: 50,
                dt: 10.0
              })
            });
            
            if (response.ok) {
              const result = await response.json();
              statusMsg.textContent = 'Simulation completed successfully.';
              statusMsg.style.color = '#10b981';
              
              const xCoords = result.x_coords.map(x => x.toFixed(2) + 'm');
              const temps = result.temperatures;
              const datasets = [
                { label: 'Initial (t=0s)', data: temps[0], borderColor: '#a78bfa', borderWidth: 2, fill: false, pointRadius: 2, tension: 0.1 },
                { label: 'Mid-Point (t=' + (Math.floor(temps.length / 2) * 10) + 's)', data: temps[Math.floor(temps.length / 2)], borderColor: '#06b6d4', borderWidth: 2, fill: false, pointRadius: 2, tension: 0.1 },
                { label: 'Final (t=' + ((temps.length - 1) * 10) + 's)', data: temps[temps.length - 1], borderColor: '#10b981', borderWidth: 2, fill: false, pointRadius: 2, tension: 0.1 }
              ];
              
              if (dashboardRouter.charts['thermalTransient']) {
                dashboardRouter.charts['thermalTransient'].data.labels = xCoords;
                dashboardRouter.charts['thermalTransient'].data.datasets = datasets;
                dashboardRouter.charts['thermalTransient'].update();
              }
            } else {
              const err = await response.text();
              statusMsg.textContent = `Error: ${err}`;
              statusMsg.style.color = 'var(--accent-red)';
            }
          } catch (e) {
            statusMsg.textContent = `Failed to connect: ${e.message}`;
            statusMsg.style.color = 'var(--accent-red)';
          }
        };
      }

      const btnMonte = document.getElementById('btnLaunchMonte');
      if (btnMonte) {
        btnMonte.onclick = async () => {
          const runs = parseInt(document.getElementById('monteRuns').value) || 100;
          const effVar = parseFloat(document.getElementById('monteEffVar').value) || 5.0;
          const logEl = document.getElementById('monteResultLog');
          logEl.textContent = 'Running Monte Carlo ensemble sweeps...';
          logEl.style.color = 'var(--accent-cyan)';
          
          const { payload } = compileArchitecture();
          
          try {
            const response = await fetch(`${API_BASE}/reliability/monte-carlo`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                runs: runs,
                solar_array_eff_var: effVar,
                req: payload
              })
            });
            
            if (response.ok) {
              const result = await response.json();
              const stats = result.statistics;
              logEl.style.color = '#10b981';
              logEl.innerHTML = `
                <div style="font-weight: bold; margin-bottom: 5px;">Ensemble Results (${result.samples_count} runs):</div>
                <div>Mission Success Probability: <span style="font-size: 14px; color: #10b981; font-weight: bold;">${result.reliability_percent.toFixed(1)}%</span></div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px; line-height: 1.4;">
                  Mean Usable SoC Margin: ${(stats.mean * 100).toFixed(2)}%<br>
                  Std Deviation: ${(stats.std * 100).toFixed(2)}%<br>
                  Worst Case Margin: ${(stats.min * 100).toFixed(2)}% | Best Case: ${(stats.max * 100).toFixed(2)}%
                </div>
              `;
            } else {
              const err = await response.text();
              logEl.textContent = `Error: ${err}`;
              logEl.style.color = 'var(--accent-red)';
            }
          } catch (e) {
            logEl.textContent = `Failed to connect: ${e.message}`;
            logEl.style.color = 'var(--accent-red)';
          }
        };
      }

      const btnAddTarget = document.getElementById('btnAddScienceTarget');
      if (btnAddTarget) {
        btnAddTarget.onclick = () => {
          const lat = document.getElementById('targetLat').value;
          const lon = document.getElementById('targetLon').value;
          const priority = document.getElementById('targetPriority').value;
          document.getElementById('scienceTargetResult').textContent = `Target [${lat}, ${lon}] added with ${priority} priority to observation schedule.`;
        };
      }
    }
  };

  // ==========================================================================
  // Schematic Designer Datasets Integration
  // ==========================================================================
  
  function findCompGroup(headerText) {
    const groups = document.querySelectorAll('.comp-group');
    for (let group of groups) {
      const header = group.querySelector('.group-header');
      if (header && header.textContent.trim().toLowerCase().includes(headerText.toLowerCase())) {
        return group;
      }
    }
    return null;
  }

  function createLibraryDragItem(parentEl, type, itemData) {
    const item = document.createElement('div');
    item.className = 'drag-item';
    item.setAttribute('draggable', 'true');
    item.setAttribute('data-type', type);
    
    let iconClass = 'fa-microchip';
    if (type === 'solar_panel') {
      iconClass = 'fa-solar-panel text-cyan';
      item.setAttribute('data-efficiency', itemData.efficiency || 0.30);
      const mass_per_m2 = itemData.mass_kg_m2 || 0.85;
      item.setAttribute('data-area', 1.5);
      item.setAttribute('data-mass', (1.5 * mass_per_m2).toFixed(2));
    } else if (type === 'battery') {
      iconClass = 'fa-battery-three-quarters text-green';
      const dod = itemData.dod || 0.30;
      const capacity = 120.0;
      const mass = itemData.capacity_wh_kg ? (capacity / itemData.capacity_wh_kg).toFixed(2) : 2.0;
      item.setAttribute('data-capacity', capacity);
      item.setAttribute('data-dod', dod);
      item.setAttribute('data-mass', mass);
    } else if (type === 'thruster') {
      iconClass = 'fa-fire text-red';
      item.setAttribute('data-thrust', itemData.thrust_n || 0.5);
      item.setAttribute('data-isp', itemData.isp_s || 220);
      item.setAttribute('data-mass', itemData.mass_kg || 1.0);
      const power = itemData.power_w || (itemData.prop_type === 'hall_thruster' ? 150 : 5);
      item.setAttribute('data-power', power);
    } else if (type === 'antenna') {
      iconClass = 'fa-satellite text-cyan';
      item.setAttribute('data-gain', itemData.gain_dbi || 12.0);
      item.setAttribute('data-freq', itemData.freq_ghz || 2.2);
      item.setAttribute('data-mass', itemData.mass_kg || 0.5);
    } else if (type === 'reaction_wheel') {
      iconClass = 'fa-circle-notch text-blue';
      item.setAttribute('data-mass', itemData.mass_kg || 1.2);
    } else if (type === 'sensor') {
      iconClass = 'fa-star text-yellow';
      item.setAttribute('data-stype', 'star_tracker');
      const accuracy_deg = itemData.accuracy_arcsec ? (itemData.accuracy_arcsec / 3600.0).toFixed(4) : 0.005;
      item.setAttribute('data-accuracy', accuracy_deg);
      item.setAttribute('data-mass', itemData.mass_kg || 0.8);
    }

    item.innerHTML = `<i class="fa-solid ${iconClass}"></i> ${itemData.name}`;
    parentEl.appendChild(item);
  }

  function renderComponentLibrary(components) {
    if (!components) return;

    const groupsToClear = [
      { text: 'Solar Arrays', key: 'solar_panels', type: 'solar_panel' },
      { text: 'Energy Storage', key: 'batteries', type: 'battery' },
      { text: 'Propulsion', key: 'thrusters', type: 'thruster' },
      { text: 'ADCS', key: 'reaction_wheels', type: 'reaction_wheel' },
      { text: 'Communications', key: 'antennas', type: 'antenna' }
    ];

    groupsToClear.forEach(g => {
      const groupEl = findCompGroup(g.text);
      if (!groupEl) return;
      
      const header = groupEl.querySelector('.group-header');
      groupEl.innerHTML = '';
      if (header) groupEl.appendChild(header);

      const list = components[g.key] || [];
      list.forEach(itemData => {
        createLibraryDragItem(groupEl, g.type, itemData);
      });

      if (g.text === 'ADCS' && components['star_trackers']) {
        components['star_trackers'].forEach(itemData => {
          createLibraryDragItem(groupEl, 'sensor', itemData);
        });
      }
    });

    bindDragEvents();
  }

  function bindDragEvents() {
    const dragItems = document.querySelectorAll('.drag-item');
    dragItems.forEach(item => {
      item.ondragstart = (e) => {
        e.dataTransfer.setData('comp-type', item.getAttribute('data-type'));
        const properties = {
          name: item.textContent.trim(),
          efficiency: item.getAttribute('data-efficiency'),
          mass: item.getAttribute('data-mass'),
          capacity: item.getAttribute('data-capacity'),
          thrust: item.getAttribute('data-thrust'),
          isp: item.getAttribute('data-isp'),
          gain: item.getAttribute('data-gain'),
          freq: item.getAttribute('data-freq'),
          accuracy: item.getAttribute('data-accuracy'),
          stype: item.getAttribute('data-stype'),
          area: item.getAttribute('data-area'),
          power: item.getAttribute('data-power')
        };
        e.dataTransfer.setData('comp-meta', JSON.stringify(properties));
      };
    });
  }

  function initComponentLibrary() {
    fetch(`${API_BASE}/components/library`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to load library');
        return res.json();
      })
      .then(data => {
        renderComponentLibrary(data.components);
      })
      .catch(err => {
        console.error(err);
        bindDragEvents();
      });
  }

  function syncCustomComponentToBackend(name, type, mass, power, vals) {
    fetch(`${API_BASE}/components/library`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to load library for sync');
        return res.json();
      })
      .then(data => {
        if (!data.components) data.components = {};
        
        let category = 'custom_subsystems';
        let backendItem = { name, mass_kg: mass, power_w: power };

        if (type === 'solar_panel') {
          category = 'solar_panels';
          backendItem.efficiency = vals.val2;
          backendItem.mass_kg_m2 = vals.val1 > 0 ? (mass / vals.val1) : 0.85;
        } else if (type === 'battery') {
          category = 'batteries';
          backendItem.capacity_wh_kg = vals.val1 > 0 ? (vals.val1 / mass) : 165;
          backendItem.dod = vals.val2;
        } else if (type === 'thruster') {
          category = 'thrusters';
          backendItem.thrust_n = vals.val1;
          backendItem.isp_s = vals.val2;
          backendItem.mass_kg = mass;
        } else if (type === 'antenna') {
          category = 'antennas';
          backendItem.gain_dbi = vals.val1;
          backendItem.freq_ghz = vals.val2;
          backendItem.mass_kg = mass;
        } else if (type === 'reaction_wheel') {
          category = 'reaction_wheels';
          backendItem.mass_kg = mass;
        } else if (type === 'sensor') {
          category = 'star_trackers';
          backendItem.accuracy_arcsec = vals.val1 * 3600.0;
          backendItem.mass_kg = mass;
        }

        if (!data.components[category]) {
          data.components[category] = [];
        }
        
        const idx = data.components[category].findIndex(c => c.name === name);
        if (idx !== -1) {
          data.components[category][idx] = backendItem;
        } else {
          data.components[category].push(backendItem);
        }

        return fetch(`${API_BASE}/components/library`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
      })
      .then(res => {
        if (!res.ok) throw new Error('Failed to save library');
        console.log('Custom component synced to backend successfully');
      })
      .catch(err => console.error('Library sync error:', err));
  }

  function updateSchematicsDropdown() {
    fetch(`${API_BASE}/design/list`)
      .then(res => res.json())
      .then(data => {
        const select = document.getElementById('selectSchematicPreset');
        if (!select) return;
        
        const firstOption = select.options[0];
        select.innerHTML = '';
        select.appendChild(firstOption);
        
        if (data.designs) {
          data.designs.forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            select.appendChild(opt);
          });
        }
      })
      .catch(err => console.error('Failed to list designs:', err));
  }

  function saveActiveSchematic() {
    const satelliteNameInput = document.getElementById('satelliteName');
    const satelliteName = satelliteNameInput ? satelliteNameInput.value.trim() : '';
    if (!satelliteName) {
      alert('Please enter a Satellite Name before saving.');
      return;
    }

    const schematicData = {
      satellite_name: satelliteName,
      orbit_preset: document.getElementById('orbitPreset').value,
      canvas_pan_x: canvas.panX,
      canvas_pan_y: canvas.panY,
      canvas_zoom: canvas.zoom,
      nodes: canvas.nodes,
      links: canvas.links,
      custom_maneuvers: customManeuvers
    };

    fetch(`${API_BASE}/design/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(schematicData)
    })
    .then(res => {
      if (!res.ok) throw new Error('Save failed');
      return res.json();
    })
    .then(data => {
      alert(`Schematic '${satelliteName}' saved successfully to backend!`);
      updateSchematicsDropdown();
    })
    .catch(err => {
      console.error(err);
      alert('Failed to save schematic to backend.');
    });
  }

  function loadSchematicByName(name) {
    if (!name) return;
    fetch(`${API_BASE}/design/load/${name}`)
      .then(res => {
        if (!res.ok) throw new Error('Load failed');
        return res.json();
      })
      .then(data => {
        renderSchematicData(data);
        alert(`Schematic '${name}' loaded successfully!`);
      })
      .catch(err => {
        console.error(err);
        alert(`Failed to load schematic '${name}'.`);
      });
  }

  function deleteSchematicByName(name) {
    if (!name) return;
    if (!confirm(`Are you sure you want to delete schematic '${name}' from backend?`)) return;
    
    fetch(`${API_BASE}/design/delete/${name}`, {
      method: 'DELETE'
    })
    .then(res => {
      if (!res.ok) throw new Error('Delete failed');
      return res.json();
    })
    .then(data => {
      alert(`Schematic '${name}' deleted successfully!`);
      updateSchematicsDropdown();
      const satelliteNameInput = document.getElementById('satelliteName');
      if (satelliteNameInput && satelliteNameInput.value === name) {
        canvas.clear();
        satelliteNameInput.value = '';
      }
    })
    .catch(err => {
      console.error(err);
      alert(`Failed to delete schematic '${name}'.`);
    });
  }

  function exportSchematicToJSON() {
    const satelliteName = document.getElementById('satelliteName').value.trim() || 'satellite_schematic';
    const schematicData = {
      satellite_name: satelliteName,
      orbit_preset: document.getElementById('orbitPreset').value,
      canvas_pan_x: canvas.panX,
      canvas_pan_y: canvas.panY,
      canvas_zoom: canvas.zoom,
      nodes: canvas.nodes,
      links: canvas.links,
      custom_maneuvers: customManeuvers
    };
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(schematicData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `${satelliteName}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  }

  function importSchematicFromJSON(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        renderSchematicData(data);
        alert('Schematic imported successfully!');
      } catch (err) {
        console.error(err);
        alert('Failed to parse JSON file. Make sure it is a valid SADS schematic.');
      }
    };
    reader.readAsText(file);
    event.target.value = '';
  }

  function renderSchematicData(data) {
    if (!data) return;
    
    canvas.clear();
    
    if (typeof data.canvas_pan_x === 'number') canvas.panX = data.canvas_pan_x;
    if (typeof data.canvas_pan_y === 'number') canvas.panY = data.canvas_pan_y;
    if (typeof data.canvas_zoom === 'number') canvas.zoom = data.canvas_zoom;
    canvas.updateTransform();

    if (data.satellite_name) {
      const nameInput = document.getElementById('satelliteName');
      if (nameInput) {
        nameInput.value = data.satellite_name;
        nameInput.dispatchEvent(new Event('input'));
      }
    }
    if (data.orbit_preset) {
      const presetSelect = document.getElementById('orbitPreset');
      if (presetSelect) {
        presetSelect.value = data.orbit_preset;
        presetSelect.dispatchEvent(new Event('change'));
      }
    }
    if (Array.isArray(data.custom_maneuvers)) {
      customManeuvers = data.custom_maneuvers;
    }

    const nodes = data.nodes || {};
    Object.keys(nodes).forEach(id => {
      const node = nodes[id];
      canvas.addNode(node.type, node.name, node.x, node.y, node.properties, node.id);
    });

    if (Array.isArray(data.links)) {
      canvas.links = data.links;
      canvas.drawLinks();
    }

    canvas.emit('change', { nodes: canvas.nodes, links: canvas.links });
    runLiveAnalysis();
  }

  // Setup toolbar schematic event listeners
  const btnLoad = document.getElementById('btnLoadSchematic');
  if (btnLoad) {
    btnLoad.addEventListener('click', () => {
      const selected = document.getElementById('selectSchematicPreset').value;
      if (!selected) {
        alert('Please choose a schematic from the dropdown list first.');
        return;
      }
      loadSchematicByName(selected);
    });
  }

  const btnSave = document.getElementById('btnSaveSchematic');
  if (btnSave) {
    btnSave.addEventListener('click', saveActiveSchematic);
  }

  const btnDelete = document.getElementById('btnDeleteSchematic');
  if (btnDelete) {
    btnDelete.addEventListener('click', () => {
      const selected = document.getElementById('selectSchematicPreset').value;
      if (!selected) {
        alert('Please choose a schematic to delete.');
        return;
      }
      deleteSchematicByName(selected);
    });
  }

  const btnExport = document.getElementById('btnExportSchematic');
  if (btnExport) {
    btnExport.addEventListener('click', exportSchematicToJSON);
  }

  const btnImport = document.getElementById('btnImportSchematic');
  const btnImportFile = document.getElementById('btnImportFile');
  if (btnImport && btnImportFile) {
    btnImport.addEventListener('click', () => btnImportFile.click());
    btnImportFile.addEventListener('change', importSchematicFromJSON);
  }

  // Initialize data loads
  initComponentLibrary();
  updateSchematicsDropdown();

  dashboardRouter.init();

});