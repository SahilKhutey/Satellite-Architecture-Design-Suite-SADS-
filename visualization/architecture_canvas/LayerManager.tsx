/**
 * SADS — Layer Manager Panel
 */

import React from 'react';
import { useCanvasStore } from './ArchitectureStore';

export const LayerManager: React.FC = () => {
  const { state, dispatch } = useCanvasStore();

  const toggleVisibility = (id: string) => {
    const nextLayers = state.layers.map(l =>
      l.id === id ? { ...l, visible: !l.visible } : l
    );
    dispatch({ type: 'SET_LAYERS', payload: nextLayers });
  };

  const toggleLock = (id: string) => {
    const nextLayers = state.layers.map(l =>
      l.id === id ? { ...l, locked: !l.locked } : l
    );
    dispatch({ type: 'SET_LAYERS', payload: nextLayers });
  };

  return (
    <div className="absolute top-4 right-4 bg-gray-900/95 border border-gray-800 rounded p-2.5 shadow-lg w-48 text-white">
      <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-850 pb-1">
        Layers
      </div>
      <div className="space-y-1">
        {state.layers.map(layer => (
          <div key={layer.id} className="flex items-center justify-between text-xs p-1 hover:bg-gray-850 rounded">
            <span className="truncate max-w-[100px]">{layer.name}</span>
            <div className="flex gap-2 text-gray-400">
              <button 
                onClick={() => toggleVisibility(layer.id)}
                className={`hover:text-white ${layer.visible ? 'text-blue-400' : 'opacity-40'}`}
              >
                👁
              </button>
              <button 
                onClick={() => toggleLock(layer.id)}
                className={`hover:text-white ${layer.locked ? 'text-red-400' : 'opacity-40'}`}
              >
                🔒
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
