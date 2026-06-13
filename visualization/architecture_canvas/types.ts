/**
 * Type definitions for the SADS architecture canvas.
 */

export type ComponentType =
  | 'satellite' | 'subsystem'
  | 'solar_panel' | 'battery'
  | 'antenna' | 'thruster' | 'tank'
  | 'reaction_wheel' | 'star_tracker'
  | 'payload' | 'heater' | 'radiator';

export type ConnectionType = 'power' | 'data' | 'thermal' | 'mechanical' | 'fluid';

export interface Position {
  x: number;
  y: number;
}

export interface Node {
  id: string;
  type: ComponentType;
  label?: string;
  position: Position;
  properties: Record<string, any>;
  parent: string | null;  // hierarchical parent (subsystem → component)
  layer: string;
  _dragOffset?: Position;
}

export interface Edge {
  id: string;
  from: string;
  to: string;
  type: ConnectionType;
  properties?: Record<string, any>;
}

export interface Layer {
  id: string;
  name: string;
  visible: boolean;
  locked: boolean;
  nodes: string[];
}

export interface Architecture {
  id: string;
  name: string;
  satellite: {
    name: string;
    mission: string;
    orbit: any;
  };
  nodes: Node[];
  edges: Edge[];
  layers: Layer[];
  metadata: {
    created_at: string;
    updated_at: string;
    version: string;
    author: string;
  };
}

export type ComponentCategory = 'power' | 'thermal' | 'comms' | 'propulsion' | 'adcs' | 'payload' | 'structure';

export interface ComponentDefinition {
  type: ComponentType;
  category: ComponentCategory;
  name: string;
  icon: string;
  description: string;
  defaults: Record<string, any>;
  schema: PropertySchema[];
}

export interface PropertySchema {
  key: string;
  label: string;
  type: 'number' | 'string' | 'enum' | 'boolean';
  unit?: string;
  min?: number;
  max?: number;
  options?: string[];
  required: boolean;
  default?: any;
}
