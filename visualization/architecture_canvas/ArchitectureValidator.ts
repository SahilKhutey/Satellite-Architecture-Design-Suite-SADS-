/**
 * SADS — Architecture Validator
 * Verifies the design graph against systems engineering requirements.
 */

import { Node, Edge } from './types';

export interface ValidationIssue {
  severity: 'error' | 'warning' | 'info';
  message: string;
  nodeId?: string;
  edgeId?: string;
}

export class ArchitectureValidator {
  static validate(nodes: Node[], edges: Edge[]): ValidationIssue[] {
    const issues: ValidationIssue[] = [];

    // Rule 1: SADS satellites require at least one power source (solar panel or battery)
    const powerSources = nodes.filter(n => n.type === 'solar_panel' || n.type === 'battery');
    if (powerSources.length === 0) {
      issues.push({
        severity: 'error',
        message: 'Spacecraft architecture requires at least one power source (Solar Panel or Battery).',
      });
    }

    // Rule 2: Components that consume power must have a path connected to a power source
    const powerConsumers = nodes.filter(n => n.type !== 'solar_panel' && n.type !== 'battery' && n.type !== 'subsystem' && n.type !== 'satellite');
    powerConsumers.forEach(consumer => {
      const isConnected = edges.some(e => e.type === 'power' && (e.from === consumer.id || e.to === consumer.id));
      if (!isConnected) {
        issues.push({
          severity: 'warning',
          message: `Component "${consumer.label || consumer.type}" has no electrical connection.`,
          nodeId: consumer.id,
        });
      }
    });

    // Rule 3: Propulsion thrusters require a propellant tank connection
    const thrusters = nodes.filter(n => n.type === 'thruster');
    thrusters.forEach(thruster => {
      const hasTank = edges.some(e => e.type === 'fluid' && (e.from === thruster.id || e.to === thruster.id));
      if (!hasTank) {
        issues.push({
          severity: 'error',
          message: `Thruster "${thruster.label || 'Thruster'}" is not connected to a fuel tank.`,
          nodeId: thruster.id,
        });
      }
    });

    // Rule 4: Cycle/loop check in hierarchy (check for recursive parent structures)
    nodes.forEach(node => {
      let currentParent = node.parent;
      const visited = new Set<string>();
      while (currentParent) {
        if (visited.has(currentParent)) {
          issues.push({
            severity: 'error',
            message: `Hierarchical loop detected containing node "${node.label || node.id}".`,
            nodeId: node.id,
          });
          break;
        }
        visited.add(currentParent);
        const parentNode = nodes.find(n => n.id === currentParent);
        currentParent = parentNode ? parentNode.parent : null;
      }
    });

    return issues;
  }
}
