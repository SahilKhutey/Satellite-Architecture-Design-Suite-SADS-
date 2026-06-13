/**
 * SADS — Architecture Serializer
 * Serializes SADS design graphs to various schemas.
 */

import { Architecture } from './types';

export class ArchitectureSerializer {
  static toJSON(arch: Architecture): string {
    return JSON.stringify(arch, null, 2);
  }

  static fromJSON(json: string): Architecture {
    const parsed = JSON.parse(json);
    if (!parsed.id || !parsed.nodes || !parsed.edges) {
      throw new Error("Invalid SADS Architecture schema.");
    }
    return parsed as Architecture;
  }

  static toCSV(arch: Architecture): string {
    let csv = "ID,Type,Label,X,Y,Properties\n";
    arch.nodes.forEach(n => {
      const props = JSON.stringify(n.properties).replace(/"/g, '""');
      csv += `${n.id},${n.type},\"${n.label || ''}\",${n.position.x},${n.position.y},\"${props}\"\n`;
    });
    return csv;
  }
}
