export class MeasurementTool {
  public static calculateDistance(p1: [number, number, number], p2: [number, number, number]): number {
    const dx = p2[0] - p1[0];
    const dy = p2[1] - p1[1];
    const dz = p2[2] - p1[2];
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  public measure(p1: [number, number, number], p2: [number, number, number]): number {
    const dist = MeasurementTool.calculateDistance(p1, p2);
    console.log(`Measured distance between [${p1}] and [${p2}]: ${dist.toFixed(3)} meters`);
    return dist;
  }
}