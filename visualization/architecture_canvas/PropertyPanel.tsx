/**
 * SADS — Property Panel
 * Edits properties of the selected component.
 */

import React from 'react';
import { useCanvasStore } from './ArchitectureStore';
import { PropertySchema } from './types';
import { ComponentLibraryData } from './ComponentLibrary';

export const PropertyPanel: React.FC = () => {
  const { state, updateNode } = useCanvasStore();
  const node = state.nodes.find(n => n.id === state.selectedNodeId);

  if (!node) {
    return (
      <aside className="w-72 bg-gray-900 border-l border-gray-800 p-4 text-white">
        <div className="text-gray-400 text-sm">
          Select a component to edit properties
        </div>
      </aside>
    );
  }

  const definition = ComponentLibraryData.get(node.type);
  if (!definition) {
    return <aside className="w-72 bg-gray-900 p-4 text-white">Unknown component</aside>;
  }

  return (
    <aside className="w-72 bg-gray-900 text-white border-l border-gray-800 overflow-y-auto">
      <div className="p-3 border-b border-gray-800">
        <h3 className="text-sm font-semibold text-blue-400 uppercase tracking-wider">
          {definition.name}
        </h3>
        <div className="text-xs text-gray-400 mt-1">{definition.description}</div>
      </div>

      <div className="p-3 space-y-3">
        <div>
          <label className="text-xs text-gray-400 block mb-1">Label</label>
          <input
            type="text"
            value={node.label || ''}
            onChange={(e) => updateNode(node.id, { label: e.target.value })}
            className="w-full px-2 py-1 bg-gray-800 border border-gray-700 rounded text-sm text-white focus:outline-none"
          />
        </div>

        <div>
          <label className="text-xs text-gray-400 block mb-1">ID</label>
          <input
            type="text"
            value={node.id}
            disabled
            className="w-full px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs font-mono text-gray-400"
          />
        </div>

        <div className="border-t border-gray-800 pt-3">
          <h4 className="text-xs uppercase text-gray-400 mb-2 font-bold">Properties</h4>
          {definition.schema.map((prop) => (
            <PropertyField
              key={prop.key}
              node={node}
              schema={prop}
              onChange={(value) => updateNode(node.id, {
                properties: { ...node.properties, [prop.key]: value }
              })}
            />
          ))}
        </div>
      </div>
    </aside>
  );
};

const PropertyField: React.FC<{
  node: any;
  schema: PropertySchema;
  onChange: (value: any) => void;
}> = ({ schema, onChange, node }) => {
  const value = node.properties[schema.key] ?? schema.default;
  return (
    <div className="mb-2">
      <label className="text-xs text-gray-400 block mb-1">
        {schema.label} {schema.unit && <span className="opacity-60 font-mono">[{schema.unit}]</span>}
      </label>
      {schema.type === 'number' ? (
        <input
          type="number"
          value={value ?? ''}
          min={schema.min}
          max={schema.max}
          step={(schema.max! - schema.min!) / 1000 || 0.001}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full px-2 py-1 bg-gray-800 border border-gray-700 rounded text-sm font-mono text-white focus:outline-none"
        />
      ) : schema.type === 'enum' ? (
        <select
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-2 py-1 bg-gray-800 border border-gray-700 rounded text-sm text-white focus:outline-none"
        >
          {schema.options?.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      ) : schema.type === 'boolean' ? (
        <input
          type="checkbox"
          checked={!!value}
          onChange={(e) => onChange(e.target.checked)}
          className="rounded border-gray-700 text-blue-500 focus:ring-0"
        />
      ) : (
        <input
          type="text"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-2 py-1 bg-gray-800 border border-gray-700 rounded text-sm text-white focus:outline-none"
        />
      )}
    </div>
  );
};
