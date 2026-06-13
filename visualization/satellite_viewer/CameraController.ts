export class CameraController {
  private target: [number, number, number] = [0, 0, 0];
  private position: [number, number, number] = [10, 10, 10];
  private zoomLevel: number = 1.0;

  public setTarget(x: number, y: number, z: number): void {
    this.target = [x, y, z];
    console.log(`Camera target set to: [${x}, ${y}, ${z}]`);
  }

  public zoom(delta: number): void {
    this.zoomLevel = Math.max(0.1, Math.min(5.0, this.zoomLevel + delta));
    console.log(`Camera zoom level: ${this.zoomLevel}`);
  }

  public reset(): void {
    this.target = [0, 0, 0];
    this.position = [10, 10, 10];
    this.zoomLevel = 1.0;
    console.log("Camera Position and Target Reset");
  }
}