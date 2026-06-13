export interface MaterialProps {
  color: string;
  roughness: number;
  metalness: number;
  emissive?: string;
  opacity?: number;
  transparent?: boolean;
}

export class MaterialEngine {
  private materials: Map<string, MaterialProps> = new Map();

  constructor() {
    this.materials.set("gold_foil", { color: "#ffd700", roughness: 0.2, metalness: 0.9 });
    this.materials.set("solar_cells", { color: "#1a1a3a", roughness: 0.1, metalness: 0.7 });
    this.materials.set("aluminum", { color: "#c0c0c0", roughness: 0.4, metalness: 0.8 });
  }

  public getMaterial(name: string): MaterialProps {
    return this.materials.get(name) || { color: "#ffffff", roughness: 0.5, metalness: 0.5 };
  }

  public apply(meshId: string, materialName: string): void {
    const mat = this.getMaterial(materialName);
    console.log(`Applying material ${materialName} (color: ${mat.color}) to mesh: ${meshId}`);
  }
}