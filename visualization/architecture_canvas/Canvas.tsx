/**
 * SADS — Canvas Main Layout
 */

import React, { useState } from 'react';
import { ComponentLibrary } from './ComponentLibrary';
import { InfiniteCanvas } from './InfiniteCanvas';
import { PropertyPanel } from './PropertyPanel';
import { useCanvasStore } from './ArchitectureStore';
import { ArchitectureValidator } from './ArchitectureValidator';

export const Canvas: React.FC = () => {
  const { state, exportJSON, importJSON } = useCanvasStore();
  const [showValidation, setShowValidation] = useState(true);

  const issues = ArchitectureValidator.validate(state.nodes, state.edges);

  return (
    <div className="flex flex-col w-full h-screen bg-gray-950 text-white font-sans overflow-hidden">
      {/* Top Navigation Header */}
      <header className="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <span className="text-xl">🛰</span>
          <h1 className="text-md font-bold tracking-wide text-blue-400">
            SADS Architecture Canvas
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              const fileData = exportJSON();
              const blob = new Blob([fileData], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'satellite_architecture.json';
              link.click();
            }}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded text-xs transition-colors font-semibold"
          >
            Export Architecture
          </button>
          <label className="px-3 py-1.5 bg-gray-800 hover:bg-gray-750 rounded text-xs cursor-pointer transition-colors font-semibold border border-gray-700">
            Import JSON
            <input
              type="file"
              accept=".json"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (evt) => {
                  const text = evt.target?.result as string;
                  importJSON(text);
                };
                reader.readAsText(file);
              }}
            />
          </label>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex flex-1 overflow-hidden relative">
        <ComponentLibrary />
        
        <main className="flex-1 h-full relative overflow-hidden bg-gray-950">
          <InfiniteCanvas />
          
          {/* Validation Warning Box */}
          {showValidation && issues.length > 0 && (
            <div className="absolute bottom-4 left-4 max-w-sm bg-gray-900 border border-yellow-500/30 rounded p-3 shadow-lg max-h-48 overflow-y-auto">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-yellow-400 uppercase tracking-wider">
                  Validation Alerts ({issues.length})
                </span>
                <button 
                  onClick={() => setShowValidation(false)}
                  className="text-gray-400 hover:text-white text-xs"
                >
                  ✕
                </button>
              </div>
              <ul className="space-y-1.5">
                {issues.map((issue, idx) => (
                  <li key={idx} className="text-[11px] text-gray-300 leading-relaxed flex gap-1.5">
                    <span className="text-yellow-500">⚠</span>
                    <span>{issue.message}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </main>

        <PropertyPanel />
      </div>
    </div>
  );
};
