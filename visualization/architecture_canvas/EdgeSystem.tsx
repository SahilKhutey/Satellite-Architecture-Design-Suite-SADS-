/**
 * SADS — Edge Routing Calculations
 */

import { Position } from './types';

export class EdgeSystem {
  static getBezierPath(from: Position, to: Position): string {
    const dx = Math.abs(to.x - from.x) * 0.5;
    const ctrl1 = { x: from.x + dx, y: from.y };
    const ctrl2 = { x: to.x - dx, y: to.y };
    return `M ${from.x} ${from.y} C ${ctrl1.x} ${ctrl1.y}, ${ctrl2.x} ${ctrl2.y}, ${to.x} ${to.y}`;
  }

  static getOrthogonalPath(from: Position, to: Position): Position[] {
    const midX = from.x + (to.x - from.x) * 0.5;
    return [
      from,
      { x: midX, y: from.y },
      { x: midX, y: to.y },
      to
    ];
  }
}
