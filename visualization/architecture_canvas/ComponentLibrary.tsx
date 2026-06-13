/**
 * SADS — Component Library sidebar.
 * Drag-and-drop source for spacecraft components.
 */

import React from 'react';
import { ComponentDefinition, ComponentType } from './types';

const DEFINITIONS: ComponentDefinition[] = [
  // Power
  {
    type: 'solar_panel', category: 'power', name: 'Solar Panel',
    icon: '☀', description: 'Photovoltaic array',
    defaults: { area: 0.5, efficiency: 0.30, mount: 'body' },
    schema: [
      { key: 'area', label: 'Area', type: 'number', unit: 'm²', min: 0.001, max: 100, required: true },
      { key: 'efficiency', label: 'Efficiency', type: 'number', min: 0.05, max: 0.45, required: true },
      { key: 'mount', label: 'Mount', type: 'enum', options: ['body', 'deployed', 'rotating'], required: false },
    ],
  },
  {
    type: 'battery', category: 'power', name: 'Battery',
    icon: '🔋', description: 'Energy storage',
    defaults: { capacity_wh: 50, dod_limit: 0.30, chemistry: 'li_ion' },
    schema: [
      { key: 'capacity_wh', label: 'Capacity', type: 'number', unit: 'Wh', min: 1, max: 50000, required: true },
      { key: 'dod_limit', label: 'Max DoD', type: 'number', min: 0.1, max: 0.8, required: true },
      { key: 'chemistry', label: 'Chemistry', type: 'enum', options: ['li_ion', 'li_po', 'ni_h2'], required: false },
    ],
  },
  // Comms
  {
    type: 'antenna', category: 'comms', name: 'Antenna',
    icon: '📡', description: 'RF antenna',
    defaults: { diameter: 0.3, frequency: 8.4e9, efficiency: 0.55 },
    schema: [
      { key: 'diameter', label: 'Diameter', type: 'number', unit: 'm', min: 0.01, max: 5, required: true },
      { key: 'frequency', label: 'Frequency', type: 'number', unit: 'Hz', min: 1e8, max: 1e11, required: true },
      { key: 'efficiency', label: 'Efficiency', type: 'number', min: 0.3, max: 0.7, required: true },
    ],
  },
  // Propulsion
  {
    type: 'thruster', category: 'propulsion', name: 'Thruster',
    icon: '🚀', description: 'Propulsive element',
    defaults: { isp_s: 220, thrust_n: 1.0, prop_type: 'monopropellant' },
    schema: [
      { key: 'isp_s', label: 'Isp', type: 'number', unit: 's', min: 50, max: 10000, required: true },
      { key: 'thrust_n', label: 'Thrust', type: 'number', unit: 'N', min: 0.001, max: 1000, required: true },
      { key: 'prop_type', label: 'Type', type: 'enum', options: ['monopropellant', 'bipropellant', 'hall', 'ion', 'cold_gas'], required: true },
    ],
  },
  {
    type: 'tank', category: 'propulsion', name: 'Propellant Tank',
    icon: '🛢', description: 'Stores propellant',
    defaults: { mass: 5.0, density: 1.0 },
    schema: [
      { key: 'mass', label: 'Propellant Mass', type: 'number', unit: 'kg', min: 0.1, max: 5000, required: true },
      { key: 'density', label: 'Density', type: 'number', unit: 'kg/L', min: 0.5, max: 3.0, required: false },
    ],
  },
  // ADCS
  {
    type: 'reaction_wheel', category: 'adcs', name: 'Reaction Wheel',
    icon: '⚙', description: 'Rotational actuator',
    defaults: { max_torque_nm: 0.02, max_momentum_nms: 0.05 },
    schema: [
      { key: 'max_torque_nm', label: 'Max Torque', type: 'number', unit: 'N·m', min: 0.0001, max: 100, required: true },
      { key: 'max_momentum_nms', label: 'Max Momentum', type: 'number', unit: 'N·m·s', min: 0.001, max: 1000, required: true },
    ],
  },
  {
    type: 'star_tracker', category: 'adcs', name: 'Star Tracker',
    icon: '⭐', description: 'Attitude sensor',
    defaults: { accuracy_arcsec: 10 },
    schema: [
      { key: 'accuracy_arcsec', label: 'Accuracy', type: 'number', unit: 'arcsec', min: 0.5, max: 60, required: true },
    ],
  },
  // Payload
  {
    type: 'payload', category: 'payload', name: 'Payload',
    icon: '📦', description: 'Mission payload',
    defaults: { power: 10, mass: 5 },
    schema: [
      { key: 'power', label: 'Power', type: 'number', unit: 'W', min: 0.1, max: 10000, required: true },
      { key: 'mass', label: 'Mass', type: 'number', unit: 'kg', min: 0.1, max: 5000, required: true },
    ],
  },
  // Thermal
  {
    type: 'heater', category: 'thermal', name: 'Heater',
    icon: '🔥', description: 'Resistive heater',
    defaults: { power: 5 },
    schema: [
      { key: 'power', label: 'Power', type: 'number', unit: 'W', min: 0.1, max: 100, required: true },
    ],
  },
  {
    type: 'radiator', category: 'thermal', name: 'Radiator',
    icon: '❄', description: 'Heat rejection surface',
    defaults: { area: 0.2, emissivity: 0.85 },
    schema: [
      { key: 'area', label: 'Area', type: 'number', unit: 'm²', min: 0.01, max: 10, required: true },
      { key: 'emissivity', label: 'Emissivity', type: 'number', min: 0.05, max: 0.95, required: true },
    ],
  },
];

export const ComponentLibraryData = {
  get(type: ComponentType): ComponentDefinition | undefined {
    return DEFINITIONS.find(d => d.type === type);
  },
  all(): ComponentDefinition[] {
    return DEFINITIONS;
  },
};

export const ComponentLibrary: React.FC = () => {
  const categories = [
    { name: 'Power', category: 'power' },
    { name: 'Communications', category: 'comms' },
    { name: 'Propulsion', category: 'propulsion' },
    { name: 'ADCS', category: 'adcs' },
    { name: 'Payload', category: 'payload' },
    { name: 'Thermal', category: 'thermal' },
  ];

  return (
    <aside className="w-56 bg-gray-900 text-white border-r border-gray-800 overflow-y-auto p-3 flex flex-col gap-4">
      <div className="border-b border-gray-800 pb-2">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-blue-400">
          Components
        </h2>
      </div>
      {categories.map(cat => {
        const items = DEFINITIONS.filter(d => d.category === cat.category);
        return (
          <div key={cat.name} className="flex flex-col gap-1">
            <h3 className="text-xs text-gray-400 uppercase font-bold px-1">{cat.name}</h3>
            {items.map(item => (
              <div
                key={item.type}
                draggable
                onDragStart={(e) => {
                  e.dataTransfer.setData('component/type', item.type);
                  e.dataTransfer.effectAllowed = 'copy';
                }}
                className="flex items-center gap-2 p-2 rounded cursor-grab
                           bg-gray-800 hover:bg-gray-700 transition-colors
                           active:cursor-grabbing"
              >
                <span className="text-lg">{item.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold truncate">{item.name}</div>
                  <div className="text-[10px] text-gray-400 truncate">{item.description}</div>
                </div>
              </div>
            ))}
          </div>
        );
      })}
    </aside>
  );
};
