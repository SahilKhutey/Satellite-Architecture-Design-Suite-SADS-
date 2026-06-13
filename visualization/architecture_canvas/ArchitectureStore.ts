/**
 * SADS — Architecture Canvas Store
 * Centralized state management using Zustand with CRDT support.
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import * as Y from 'yjs';
import { Node, Edge, Architecture, Position } from './types';

interface CanvasState {
  state: {
    nodes: Node[];
    edges: Edge[];
    selectedNodeId: string | null;
    selectedEdgeId: string | null;
    layers: { id: string; name: string; visible: boolean; locked: boolean }[];
  };
  pan: Position;
  zoom: number;
  ydoc: Y.Doc;
  addNode: (node: Node) => void;
  removeNode: (id: string) => void;
  updateNode: (id: string, patch: Partial<Node>) => void;
  addEdge: (edge: Edge) => void;
  removeEdge: (id: string) => void;
  selectNode: (id: string | null) => void;
  dispatch: (action: { type: string; payload?: any }) => void;
  save: () => Architecture;
  load: (arch: Architecture) => void;
  exportJSON: () => string;
  importJSON: (json: string) => void;
}

export const useCanvasStore = create<CanvasState>()(
  subscribeWithSelector((set, get) => {
    const ydoc = new Y.Doc();
    const yNodes = ydoc.getMap<Node>('nodes');
    const yEdges = ydoc.getMap<Edge>('edges');
    const yMeta = ydoc.getMap('meta');

    // Sync Y.js to local state
    yNodes.observe(() => {
      set((s) => ({ state: { ...s.state, nodes: Array.from(yNodes.values()) } }));
    });
    yEdges.observe(() => {
      set((s) => ({ state: { ...s.state, edges: Array.from(yEdges.values()) } }));
    });

    return {
      state: {
        nodes: [],
        edges: [],
        selectedNodeId: null,
        selectedEdgeId: null,
        layers: [{ id: 'main', name: 'Main', visible: true, locked: false }],
      },
      pan: { x: 0, y: 0 },
      zoom: 1.0,
      ydoc,

      addNode: (node) => {
        yNodes.set(node.id, node);
        set((s) => ({ state: { ...s.state, nodes: [...s.state.nodes, node] } }));
      },

      removeNode: (id) => {
        yNodes.delete(id);
        // Also remove connected edges
        Array.from(yEdges.values()).forEach((e) => {
          if (e.from === id || e.to === id) yEdges.delete(e.id);
        });
      },

      updateNode: (id, patch) => {
        const node = yNodes.get(id);
        if (node) {
          yNodes.set(id, { ...node, ...patch });
        }
      },

      addEdge: (edge) => {
        yEdges.set(edge.id, edge);
      },

      removeEdge: (id) => {
        yEdges.delete(id);
      },

      selectNode: (id) => {
        set((s) => ({ state: { ...s.state, selectedNodeId: id } }));
      },

      dispatch: (action) => {
        const { updateNode } = get();
        switch (action.type) {
          case 'SET_PAN':
            set({ pan: action.payload });
            break;
          case 'SET_ZOOM':
            set({ zoom: action.payload });
            break;
          case 'SET_LAYERS':
            set((s) => ({ state: { ...s.state, layers: action.payload } }));
            break;
          case 'UPDATE_NODE_POSITION':
            updateNode(action.payload.id, { position: action.payload.position });
            break;
        }
      },

      save: () => {
        const s = get();
        return {
          id: (yMeta.get('id') as string) || crypto.randomUUID(),
          name: (yMeta.get('name') as string) || 'Untitled',
          satellite: (yMeta.get('satellite') as any) || { name: '', mission: '', orbit: null },
          nodes: s.state.nodes,
          edges: s.state.edges,
          layers: s.state.layers,
          metadata: {
            created_at: (yMeta.get('created_at') as string) || new Date().toISOString(),
            updated_at: new Date().toISOString(),
            version: '1.0.0',
            author: (yMeta.get('author') as string) || 'unknown',
          },
        };
      },

      load: (arch) => {
        ydoc.transact(() => {
          yNodes.clear();
          yEdges.clear();
          arch.nodes.forEach((n) => yNodes.set(n.id, n));
          arch.edges.forEach((e) => yEdges.set(e.id, e));
          yMeta.set('id', arch.id);
          yMeta.set('name', arch.name);
          yMeta.set('satellite', arch.satellite);
          yMeta.set('author', arch.metadata.author);
          yMeta.set('created_at', arch.metadata.created_at);
        });
      },

      exportJSON: () => {
        return JSON.stringify(get().save(), null, 2);
      },

      importJSON: (json) => {
        try {
          const arch = JSON.parse(json) as Architecture;
          get().load(arch);
        } catch (e) {
          console.error('Invalid JSON', e);
        }
      },
    };
  })
);
