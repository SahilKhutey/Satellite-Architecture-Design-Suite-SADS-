/**
 * SADS — Node System Calculations
 */

import { Node, Position } from './types';

export class NodeSystem {
  static getBounds(nodes: Node[]): { minX: number; maxX: number; minY: number; maxY: number } {
    if (nodes.length === 0) return { minX: 0, maxX: 0, minY: 0, maxY: 0 };
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    nodes.forEach(n => {
      minX = Math.min(minX, n.position.x);
      maxX = Math.max(maxX, n.position.x);
      minY = Math.min(minY, n.position.y);
      maxY = Math.max(maxY, n.position.y);
    });
    return { minX, maxX, minY, maxY };
  }

  static alignSelection(nodes: Node[], ids: string[], axis: 'x' | 'y'): Node[] {
    const targets = nodes.filter(n => ids.includes(n.id));
    if (targets.length <= 1) return nodes;

    if (axis === 'x') {
      const avgX = targets.reduce((sum, n) => sum + n.position.x, 0) / targets.length;
      return nodes.map(n => ids.includes(n.id) ? { ...n, position: { ...n.position, x: avgX } } : n);
    } else {
      const avgY = targets.reduce((sum, n) => sum + n.position.y, 0) / targets.length;
      return nodes.map(n => ids.includes(n.id) ? { ...n, position: { ...n.position, y: avgY } } : n);
    }
  }
}
