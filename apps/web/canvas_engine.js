/* SADS - 2D Canvas Engine
   Implements an interactive 2D Figma-like node layout canvas.
   Supports custom nodes, drag-and-drop, connection ports, panning, and zoom.
*/

class CanvasEngine {
  constructor(containerId, svgId, domLayerId) {
    this.container = document.getElementById(containerId);
    this.svg = document.getElementById(svgId);
    this.domLayer = document.getElementById(domLayerId);
    
    this.nodes = {};
    this.links = [];
    this.selectedNodeId = null;
    
    // Pan & Zoom state
    this.panX = 0;
    this.panY = 0;
    this.zoom = 1;
    this.isPanning = false;
    this.startX = 0;
    this.startY = 0;
    
    // Connection state
    this.activePort = null; // { nodeId, type: 'input'|'output' }
    this.tempLine = null;
    
    this.nodeCounter = 0;
    
    // Event listeners registration
    this.listeners = {};
    
    this.init();
  }

  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }

  init() {
    // Canvas background drag-to-pan
    this.container.addEventListener('mousedown', (e) => {
      if (e.target === this.container || e.target === this.svg) {
        this.isPanning = true;
        this.container.style.cursor = 'grabbing';
        this.startX = e.clientX - this.panX;
        this.startY = e.clientY - this.panY;
      }
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isPanning) {
        this.panX = e.clientX - this.startX;
        this.panY = e.clientY - this.startY;
        this.updateTransform();
      } else if (this.activePort) {
        this.updateTempLine(e.clientX, e.clientY);
      }
    });

    window.addEventListener('mouseup', (e) => {
      if (this.isPanning) {
        this.isPanning = false;
        this.container.style.cursor = 'grab';
      }
      if (this.activePort) {
        this.cancelTempConnection();
      }
    });

    // Zoom listener (mouse wheel)
    this.container.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = 1.08;
      const prevZoom = this.zoom;
      
      if (e.deltaY < 0) {
        this.zoom = Math.min(2.5, this.zoom * zoomFactor);
      } else {
        this.zoom = Math.max(0.4, this.zoom / zoomFactor);
      }

      // Zoom towards mouse pointer
      const rect = this.container.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      this.panX = mouseX - (mouseX - this.panX) * (this.zoom / prevZoom);
      this.panY = mouseY - (mouseY - this.panY) * (this.zoom / prevZoom);
      
      this.updateTransform();
      this.emit('zoom', Math.round(this.zoom * 100));
    });

    // Setup drag over and drop events from the component library
    this.container.addEventListener('dragover', (e) => {
      e.preventDefault();
    });

    this.container.addEventListener('drop', (e) => {
      e.preventDefault();
      const type = e.dataTransfer.getData('comp-type');
      if (!type) return;

      const rect = this.container.getBoundingClientRect();
      // Calculate coordinates relative to zoomed/panned canvas
      const x = (e.clientX - rect.left - this.panX) / this.zoom;
      const y = (e.clientY - rect.top - this.panY) / this.zoom;

      const meta = JSON.parse(e.dataTransfer.getData('comp-meta') || '{}');
      this.addNode(type, meta.name || type, x, y, meta);
    });
  }

  updateTransform() {
    this.domLayer.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.zoom})`;
    this.drawLinks();
  }

  addNode(type, name, x, y, properties = {}) {
    this.nodeCounter++;
    const id = `node_${type}_${this.nodeCounter}`;
    
    // Core parameters based on type
    const defaultProps = {
      mass_kg: parseFloat(properties.mass) || 1.0,
      nominal_power_w: parseFloat(properties.power) || 0.0,
      efficiency: parseFloat(properties.efficiency) || 0.0,
      capacity_wh: parseFloat(properties.capacity) || 0.0,
      dod_limit: parseFloat(properties.dod) || 0.30,
      thrust_n: parseFloat(properties.thrust) || 0.0,
      isp_s: parseFloat(properties.isp) || 0.0,
      gain_dbi: parseFloat(properties.gain) || 0.0,
      frequency_hz: (parseFloat(properties.freq) || 8.4) * 1e9,
      accuracy_deg: parseFloat(properties.accuracy) || 0.01,
      absorptivity: 0.3,
      emissivity: 0.85,
      area_m2: 1.0
    };

    const mergedProps = Object.assign({}, defaultProps, properties);

    // Delete temporary/draggable transfer properties to avoid duplication in Details panel
    const tempKeys = ['mass', 'power', 'efficiency', 'capacity', 'dod', 'thrust', 'isp', 'gain', 'freq', 'accuracy', 'stype', 'name'];
    tempKeys.forEach(k => delete mergedProps[k]);

    const node = {
      id,
      type,
      name,
      x,
      y,
      properties: mergedProps
    };

    this.nodes[id] = node;
    this.renderNodeDom(node);
    this.selectNode(id);
    this.emit('change', { nodes: this.nodes, links: this.links });
    return id;
  }

  renderNodeDom(node) {
    const el = document.createElement('div');
    el.className = 'sads-node';
    el.id = node.id;
    el.style.left = `${node.x}px`;
    el.style.top = `${node.y}px`;

    // Visual configuration
    let iconClass = 'fa-microchip';
    if (node.type === 'solar_panel') iconClass = 'fa-solar-panel text-cyan';
    if (node.type === 'battery') iconClass = 'fa-battery-three-quarters text-green';
    if (node.type === 'thruster') iconClass = 'fa-fire text-red';
    if (node.type === 'tank') iconClass = 'fa-circle-nodes text-purple';
    if (node.type === 'antenna') iconClass = 'fa-satellite text-cyan';
    if (node.type === 'reaction_wheel') iconClass = 'fa-circle-notch text-blue';
    if (node.type === 'sensor') iconClass = 'fa-star text-yellow';
    if (node.type === 'instrument') iconClass = 'fa-microscope text-purple';
    if (node.type === 'camera') iconClass = 'fa-camera text-yellow';
    if (node.type === 'software') iconClass = 'fa-file-code text-green';
    if (node.type === 'module') iconClass = 'fa-cubes text-blue';

    el.innerHTML = `
      <div class="node-title"><i class="fa-solid ${iconClass}"></i> <span class="node-label">${node.name}</span></div>
      <div class="node-details">
        ${node.type === 'solar_panel' ? `Area: ${node.properties.area_m2}m²` : ''}
        ${node.type === 'battery' ? `Cap: ${node.properties.capacity_wh}Wh` : ''}
        ${node.type === 'thruster' ? `Thrust: ${node.properties.thrust_n}N` : ''}
        ${node.type === 'tank' ? `Fuel: ${node.properties.mass_kg}kg` : ''}
        ${node.type === 'antenna' ? `Gain: ${node.properties.gain_dbi}dBi` : ''}
        ${node.type === 'reaction_wheel' ? `Wheels: 1` : ''}
        ${node.type === 'sensor' ? `Acc: ${node.properties.accuracy_deg}°` : ''}
        ${['instrument', 'camera', 'software', 'module'].includes(node.type) ? `Mass: ${node.properties.mass_kg}kg | Power: ${node.properties.nominal_power_w}W` : ''}
      </div>
      <!-- Ports -->
      <div class="node-port port-input" data-node="${node.id}" data-type="input"></div>
      <div class="node-port port-output" data-node="${node.id}" data-type="output"></div>
    `;

    // Click to select node
    el.addEventListener('mousedown', (e) => {
      e.stopPropagation();
      this.selectNode(node.id);
      
      // Drag node logic
      const rect = this.container.getBoundingClientRect();
      const startNodeX = node.x;
      const startNodeY = node.y;
      const startMouseX = e.clientX;
      const startMouseY = e.clientY;

      const onMouseMove = (moveEv) => {
        const dx = (moveEv.clientX - startMouseX) / this.zoom;
        const dy = (moveEv.clientY - startMouseY) / this.zoom;
        node.x = startNodeX + dx;
        node.y = startNodeY + dy;
        el.style.left = `${node.x}px`;
        el.style.top = `${node.y}px`;
        this.drawLinks();
      };

      const onMouseUp = () => {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        this.emit('change', { nodes: this.nodes, links: this.links });
      };

      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    });

    // Ports link drawing logic
    const ports = el.querySelectorAll('.node-port');
    ports.forEach(port => {
      port.addEventListener('mousedown', (e) => {
        e.stopPropagation();
        e.preventDefault();
        const nodeId = port.getAttribute('data-node');
        const portType = port.getAttribute('data-type');
        this.startTempConnection(nodeId, portType, e);
      });

      port.addEventListener('mouseup', (e) => {
        e.stopPropagation();
        const nodeId = port.getAttribute('data-node');
        const portType = port.getAttribute('data-type');
        this.completeConnection(nodeId, portType);
      });
    });

    this.domLayer.appendChild(el);
  }

  selectNode(id) {
    if (this.selectedNodeId) {
      const prev = document.getElementById(this.selectedNodeId);
      if (prev) prev.classList.remove('selected');
    }
    this.selectedNodeId = id;
    const current = document.getElementById(id);
    if (current) current.classList.add('selected');
    this.emit('nodeSelected', this.nodes[id]);
  }

  clearSelection() {
    if (this.selectedNodeId) {
      const prev = document.getElementById(this.selectedNodeId);
      if (prev) prev.classList.remove('selected');
    }
    this.selectedNodeId = null;
    this.emit('nodeSelected', null);
  }

  deleteSelectedNode() {
    if (!this.selectedNodeId) return;
    
    // Remove element
    const el = document.getElementById(this.selectedNodeId);
    if (el) el.remove();

    // Remove associated links
    this.links = this.links.filter(l => l.from !== this.selectedNodeId && l.to !== this.selectedNodeId);
    
    // Remove from object
    delete this.nodes[this.selectedNodeId];
    this.selectedNodeId = null;
    
    this.drawLinks();
    this.clearSelection();
    this.emit('change', { nodes: this.nodes, links: this.links });
  }

  clear() {
    this.nodes = {};
    this.links = [];
    this.domLayer.innerHTML = '';
    this.nodeCounter = 0;
    this.clearSelection();
    this.drawLinks();
    this.emit('change', { nodes: this.nodes, links: this.links });
  }

  // Links connection logic
  startTempConnection(nodeId, portType, event) {
    this.activePort = { nodeId, type: portType };
    
    // Create temporary path in SVG
    if (!this.tempLine) {
      this.tempLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      this.tempLine.setAttribute('class', 'svg-link active');
      this.svg.appendChild(this.tempLine);
    }
  }

  updateTempLine(clientX, clientY) {
    if (!this.tempLine || !this.activePort) return;
    const startPos = this.getPortCoords(this.activePort.nodeId, this.activePort.type);
    
    const rect = this.svg.getBoundingClientRect();
    const endX = (clientX - rect.left - this.panX) / this.zoom;
    const endY = (clientY - rect.top - this.panY) / this.zoom;
    
    this.setPathCurve(this.tempLine, startPos.x, startPos.y, endX, endY);
  }

  cancelTempConnection() {
    if (this.tempLine) {
      this.tempLine.remove();
      this.tempLine = null;
    }
    this.activePort = null;
  }

  completeConnection(targetNodeId, targetPortType) {
    if (!this.activePort) return;
    const sourceNodeId = this.activePort.nodeId;
    const sourcePortType = this.activePort.type;
    
    // Valid link: from output to input on different nodes
    if (sourceNodeId !== targetNodeId && sourcePortType !== targetPortType) {
      const fromId = sourcePortType === 'output' ? sourceNodeId : targetNodeId;
      const toId = sourcePortType === 'input' ? sourceNodeId : targetNodeId;
      
      // Check duplicate
      const duplicate = this.links.find(l => l.from === fromId && l.to === toId);
      if (!duplicate) {
        this.links.push({ from: fromId, to: toId });
        this.emit('change', { nodes: this.nodes, links: this.links });
      }
    }
    this.cancelTempConnection();
    this.drawLinks();
  }

  getPortCoords(nodeId, portType) {
    const node = this.nodes[nodeId];
    if (!node) return { x: 0, y: 0 };
    
    // Approx relative position of port dot
    const nodeWidth = 170; // min-width + padding
    const nodeHeight = 65;
    
    if (portType === 'output') {
      return { x: node.x + nodeWidth, y: node.y + nodeHeight / 2 };
    } else {
      return { x: node.x, y: node.y + nodeHeight / 2 };
    }
  }

  setPathCurve(pathEl, x1, y1, x2, y2) {
    const dx = Math.abs(x2 - x1) * 0.5;
    const d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
    pathEl.setAttribute('d', d);
  }

  drawLinks() {
    // Clear old links
    const oldPaths = this.svg.querySelectorAll('.svg-link:not(.active)');
    oldPaths.forEach(p => p.remove());

    this.links.forEach(link => {
      const fromPos = this.getPortCoords(link.from, 'output');
      const toPos = this.getPortCoords(link.to, 'input');
      
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('class', 'svg-link');
      this.setPathCurve(path, fromPos.x, fromPos.y, toPos.x, toPos.y);
      this.svg.appendChild(path);
    });
  }

  zoomToFit() {
    const nodeIds = Object.keys(this.nodes);
    if (nodeIds.length === 0) {
      this.panX = 0;
      this.panY = 0;
      this.zoom = 1;
      this.updateTransform();
      return;
    }

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    nodeIds.forEach(id => {
      const node = this.nodes[id];
      minX = Math.min(minX, node.x);
      minY = Math.min(minY, node.y);
      maxX = Math.max(maxX, node.x + 180);
      maxY = Math.max(maxY, node.y + 80);
    });

    const graphWidth = maxX - minX;
    const graphHeight = maxY - minY;
    
    const rect = this.container.getBoundingClientRect();
    const pad = 40;
    
    const zoomX = (rect.width - pad * 2) / graphWidth;
    const zoomY = (rect.height - pad * 2) / graphHeight;
    this.zoom = Math.max(0.5, Math.min(1.5, Math.min(zoomX, zoomY)));
    
    this.panX = rect.width / 2 - (minX + graphWidth / 2) * this.zoom;
    this.panY = rect.height / 2 - (minY + graphHeight / 2) * this.zoom;
    
    this.updateTransform();
    this.emit('zoom', Math.round(this.zoom * 100));
  }
}
