import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

export class SceneManager {
  private container: HTMLElement;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private controls: OrbitControls;
  private renderCallbacks: Array<() => void> = [];
  private isAnimating: boolean = false;

  constructor(container: HTMLElement) {
    this.container = container;
    this.scene = new THREE.Scene();
    
    const aspect = container.clientWidth / container.clientHeight || 1;
    this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100);
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
  }

  public init(): void {
    console.log("SADS 3D Engine: Initializing WebGL Renderer Context");
    this.scene.background = new THREE.Color(0x0f172a);
    
    this.camera.position.set(5, 5, 5);
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.container.appendChild(this.renderer.domElement);
    
    this.setupLighting();
  }

  private setupLighting(): void {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(10, 10, 10);
    this.scene.add(dirLight);
  }

  public registerRenderCallback(cb: () => void): void {
    this.renderCallbacks.push(cb);
  }

  public startLoop(): void {
    this.isAnimating = true;
    const loop = () => {
      if (!this.isAnimating) return;
      this.render();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  public stopLoop(): void {
    this.isAnimating = false;
  }

  public render(): void {
    this.controls.update();
    for (const cb of this.renderCallbacks) {
      cb();
    }
    this.renderer.render(this.scene, this.camera);
  }

  public resize(width: number, height: number): void {
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
}