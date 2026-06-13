/**
 * SADS — Infinite Engineering Canvas
 * Aerospace equivalent of Figma for satellite systems.
 */

import React, { useEffect, useRef, useState } from 'react';
import { useCanvasStore } from './ArchitectureStore';
import { ComponentLibraryData } from './ComponentLibrary';
import { ComponentType, Position, Node, Edge } from './types';

const ZOOM_MIN = 0.1;
const ZOOM_MAX = 4.0;
const GRID_SIZE = 20;

export const InfiniteCanvas: React.FC = () => {
  const {
    state, dispatch,
    addNode, addEdge, selectNode, pan, zoom,
  } = useCanvasStore();

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<Position>({ x: 0, y: 0 });
  const [mousePos, setMousePos] = useState<Position>({ x: 0, y: 0 });
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null);

  // Render loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;

    const render = () => {
      const w = canvas.width = canvas.clientWidth * window.devicePixelRatio;
      const h = canvas.height = canvas.clientHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

      // Background
      ctx.fillStyle = '#0a0e1a';
      ctx.fillRect(0, 0, w, h);

      // Grid (with zoom)
      drawGrid(ctx, w, h, pan, zoom);

      // Save transform
      ctx.save();
      ctx.translate(pan.x, pan.y);
      ctx.scale(zoom, zoom);

      // Draw edges
      state.edges.forEach(edge => drawEdge(ctx, edge, state.nodes, zoom));

      // Draw nodes
      state.nodes.forEach(node => drawNode(ctx, node, zoom, state.selectedNodeId === node.id));

      // Draw connection in progress
      if (connectingFrom) {
        const fromNode = state.nodes.find(n => n.id === connectingFrom);
        if (fromNode) {
          const to = screenToWorld(mousePos, pan, zoom);
          ctx.strokeStyle = '#4fc3f7';
          ctx.setLineDash([4, 4]);
          ctx.lineWidth = 2 / zoom;
          ctx.beginPath();
          ctx.moveTo(fromNode.position.x, fromNode.position.y);
          ctx.lineTo(to.x, to.y);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }

      ctx.restore();
    };

    let animId = requestAnimationFrame(render);
    const handleLoop = () => {
      render();
      animId = requestAnimationFrame(handleLoop);
    };
    return () => cancelAnimationFrame(animId);
  }, [state, pan, zoom, mousePos, connectingFrom]);

  // Mouse handlers
  const onMouseDown = (e: React.MouseEvent) => {
    const rect = canvasRef.current!.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const clientY = e.clientY - rect.top;
    const world = screenToWorld({ x: clientX, y: clientY }, pan, zoom);
    const node = findNodeAt(world, state.nodes);

    if (e.shiftKey && node) {
      setConnectingFrom(node.id);
      return;
    }

    if (node) {
      selectNode(node.id);
      setIsDragging(true);
      setDragStart(world);
      node._dragOffset = { x: world.x - node.position.x, y: world.y - node.position.y };
    } else {
      selectNode(null);
      setIsDragging(true);
      setDragStart({ x: clientX - pan.x, y: clientY - pan.y });
    }
  };

  const onMouseMove = (e: React.MouseEvent) => {
    const rect = canvasRef.current!.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const clientY = e.clientY - rect.top;
    setMousePos({ x: clientX, y: clientY });
    if (isDragging) {
      const world = screenToWorld({ x: clientX, y: clientY }, pan, zoom);
      const node = state.nodes.find(n => n.id === state.selectedNodeId);
      if (node) {
        dispatch({
          type: 'UPDATE_NODE_POSITION',
          payload: { id: node.id, position: { x: world.x - (node._dragOffset?.x || 0), y: world.y - (node._dragOffset?.y || 0) } }
        });
      } else {
        dispatch({ type: 'SET_PAN', payload: { x: clientX - dragStart.x, y: clientY - dragStart.y } });
      }
    }
  };

  const onMouseUp = (e: React.MouseEvent) => {
    if (connectingFrom) {
      const rect = canvasRef.current!.getBoundingClientRect();
      const clientX = e.clientX - rect.left;
      const clientY = e.clientY - rect.top;
      const world = screenToWorld({ x: clientX, y: clientY }, pan, zoom);
      const target = findNodeAt(world, state.nodes);
      if (target && target.id !== connectingFrom) {
        addEdge({
          id: `edge-${Date.now()}`,
          from: connectingFrom,
          to: target.id,
          type: 'power',
        });
      }
      setConnectingFrom(null);
    }
    setIsDragging(false);
  };

  const onWheel = (e: React.WheelEvent) => {
    const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
    const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, zoom * factor));
    const rect = canvasRef.current!.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    const newPan = {
      x: mx - (mx - pan.x) * (newZoom / zoom),
      y: my - (my - pan.y) * (newZoom / zoom),
    };
    dispatch({ type: 'SET_ZOOM', payload: newZoom });
    dispatch({ type: 'SET_PAN', payload: newPan });
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const compType = e.dataTransfer.getData('component/type') as ComponentType;
    if (!compType) return;
    const rect = canvasRef.current!.getBoundingClientRect();
    const world = screenToWorld(
      { x: e.clientX - rect.left, y: e.clientY - rect.top },
      pan, zoom
    );
    const definition = ComponentLibraryData.get(compType);
    addNode({
      id: `node-${Date.now()}`,
      type: compType,
      position: snapToGrid(world),
      properties: definition ? { ...definition.defaults } : {},
      parent: null,
      layer: 'main',
    });
  };

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-crosshair block"
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onWheel={onWheel}
        onDrop={onDrop}
        onDragOver={(e) => e.preventDefault()}
      />
    </div>
  );
};

function drawGrid(
  ctx: CanvasRenderingContext2D, w: number, h: number,
  pan: Position, zoom: number
) {
  const step = GRID_SIZE * zoom;
  const offsetX = pan.x % step;
  const offsetY = pan.y % step;
  ctx.strokeStyle = '#1a2332';
  ctx.lineWidth = 0.5;
  for (let x = offsetX; x < w; x += step) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  for (let y = offsetY; y < h; y += step) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
}

function drawNode(ctx: CanvasRenderingContext2D, node: Node, zoom: number, selected: boolean) {
  const size = componentSize(node.type);
  ctx.fillStyle = selected ? '#1e3a5f' : '#1a2332';
  ctx.strokeStyle = selected ? '#ffeb3b' : '#4fc3f7';
  ctx.lineWidth = (selected ? 3 : 2) / zoom;
  ctx.fillRect(node.position.x, node.position.y, size.w, size.h);
  ctx.strokeRect(node.position.x, node.position.y, size.w, size.h);

  // Icon
  ctx.fillStyle = '#4fc3f7';
  ctx.font = `${14 / zoom}px sans-serif`;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';
  ctx.fillText(getIcon(node.type), node.position.x + size.w / 2, node.position.y + size.h / 2 - 8 / zoom);

  // Label
  ctx.fillStyle = '#e0e6f0';
  ctx.font = `${11 / zoom}px sans-serif`;
  ctx.fillText(node.label || node.type, node.position.x + size.w / 2, node.position.y + size.h / 2 + 10 / zoom);
}

function drawEdge(ctx: CanvasRenderingContext2D, edge: Edge, nodes: Node[], zoom: number) {
  const from = nodes.find(n => n.id === edge.from);
  const to = nodes.find(n => n.id === edge.to);
  if (!from || !to) return;
  const colors: Record<string, string> = {
    power: '#4fc3f7',
    data: '#a5d6a7',
    thermal: '#ef5350',
    mechanical: '#ffd54f',
    fluid: '#ba68c8',
  };
  ctx.strokeStyle = colors[edge.type] || '#4fc3f7';
  ctx.lineWidth = 2 / zoom;
  ctx.beginPath();
  const fromSize = componentSize(from.type);
  const toSize = componentSize(to.type);
  ctx.moveTo(from.position.x + fromSize.w / 2, from.position.y + fromSize.h / 2);
  ctx.lineTo(to.position.x + toSize.w / 2, to.position.y + toSize.h / 2);
  ctx.stroke();
}

function screenToWorld(screen: Position, pan: Position, zoom: number): Position {
  return {
    x: (screen.x - pan.x) / zoom,
    y: (screen.y - pan.y) / zoom,
  };
}

function findNodeAt(world: Position, nodes: Node[]): Node | null {
  for (const n of nodes) {
    const size = componentSize(n.type);
    if (world.x >= n.position.x && world.x <= n.position.x + size.w &&
        world.y >= n.position.y && world.y <= n.position.y + size.h) {
      return n;
    }
  }
  return null;
}

function snapToGrid(p: Position): Position {
  return {
    x: Math.round(p.x / GRID_SIZE) * GRID_SIZE,
    y: Math.round(p.y / GRID_SIZE) * GRID_SIZE,
  };
}

function componentSize(type: ComponentType): { w: number; h: number } {
  const sizes: Record<string, { w: number; h: number }> = {
    satellite: { w: 160, h: 100 },
    subsystem: { w: 120, h: 80 },
    solar_panel: { w: 80, h: 40 },
    battery: { w: 80, h: 40 },
    antenna: { w: 80, h: 40 },
    thruster: { w: 80, h: 40 },
    tank: { w: 80, h: 40 },
    reaction_wheel: { w: 80, h: 40 },
    star_tracker: { w: 80, h: 40 },
    payload: { w: 80, h: 40 },
    heater: { w: 80, h: 40 },
    radiator: { w: 80, h: 40 },
  };
  return sizes[type] || { w: 80, h: 40 };
}

function getIcon(type: ComponentType): string {
  const icons: Record<string, string> = {
    solar_panel: '☀',
    battery: '🔋',
    antenna: '📡',
    thruster: '🚀',
    tank: '🛢',
    reaction_wheel: '⚙',
    star_tracker: '⭐',
    payload: '📦',
    heater: '🔥',
    radiator: '❄',
    satellite: '🛰',
    subsystem: '⊟',
  };
  return icons[type] || '□';
}
