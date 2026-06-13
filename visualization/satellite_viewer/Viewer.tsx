import React, { useEffect, useRef, useState } from "react";
import { SceneManager } from "./SceneManager";
import { CADLoader, CADModel } from "./CADLoader";
import { MaterialEngine } from "./MaterialEngine";
import { CameraController } from "./CameraController";
import { MeasurementTool } from "./MeasurementTool";
import { AnnotationSystem, Annotation } from "./AnnotationSystem";

interface ViewerProps {
  modelUrl?: string;
  materialName?: string;
}

export const Viewer: React.FC<ViewerProps> = ({
  modelUrl = "/models/cubesat_3u.gltf",
  materialName = "gold_foil"
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [model, setModel] = useState<CADModel | null>(null);
  const [loadingProgress, setLoadingProgress] = useState<number>(0);
  const [distance, setDistance] = useState<number | null>(null);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);

  const sceneManagerRef = useRef<SceneManager | null>(null);
  const cadLoaderRef = useRef<CADLoader>(new CADLoader());
  const materialEngineRef = useRef<MaterialEngine>(new MaterialEngine());
  const cameraControllerRef = useRef<CameraController>(new CameraController());
  const measurementToolRef = useRef<MeasurementTool>(new MeasurementTool());
  const annotationSystemRef = useRef<AnnotationSystem>(new AnnotationSystem());

  useEffect(() => {
    if (!containerRef.current) return;

    const manager = new SceneManager(containerRef.current);
    sceneManagerRef.current = manager;
    manager.init();
    manager.startLoop();

    cadLoaderRef.current.load(modelUrl, (progress) => {
      setLoadingProgress(progress);
    }).then((loadedModel) => {
      setModel(loadedModel);
      materialEngineRef.current.apply("mesh_obc_001", materialName);
    });

    cameraControllerRef.current.setTarget(0, 0, 0);

    annotationSystemRef.current.addAnnotation("gps_ant", "GPS Patch Antenna", [0.1, 0.2, 0.3]);
    setAnnotations(annotationSystemRef.current.getAnnotations());

    return () => {
      if (sceneManagerRef.current) {
        sceneManagerRef.current.stopLoop();
      }
    };
  }, [modelUrl, materialName]);

  const handleZoomIn = () => {
    cameraControllerRef.current.zoom(-0.2);
  };

  const handleZoomOut = () => {
    cameraControllerRef.current.zoom(0.2);
  };

  const handleReset = () => {
    cameraControllerRef.current.reset();
  };

  const handleMeasure = () => {
    const dist = measurementToolRef.current.measure([0.1, 0.2, 0.3], [-0.1, -0.2, -0.3]);
    setDistance(dist);
  };

  return (
    <div style={{ width: "100%", height: "100%", position: "relative", backgroundColor: "#0f172a", color: "#f8fafc", fontFamily: "sans-serif" }}>
      <div ref={containerRef} style={{ width: "100%", height: "400px", borderRadius: "8px", overflow: "hidden" }}>
        {/* Mock WebGL Canvas Element */}
      </div>

      <div style={{ padding: "16px", background: "#1e293b", borderRadius: "8px", marginTop: "12px" }}>
        <h3>SADS 3D Satellite CAD Assembly Viewer</h3>
        
        {model ? (
          <div>
            <p><strong>Model Status</strong>: Loaded ({model.verticesCount} vertices, {model.facesCount} faces)</p>
            <p><strong>URL</strong>: {model.url}</p>
            {model.centerOfMass && (
              <p style={{ color: "#34d399" }}><strong>Center of Mass (CoM)</strong>: [{model.centerOfMass.map(v => v.toFixed(4)).join(", ")}] m</p>
            )}
          </div>
        ) : (
          <p>Loading CAD Geometry Model... ({loadingProgress}%)</p>
        )}

        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "12px" }}>
          <button onClick={handleZoomIn} style={btnStyle}>Zoom In</button>
          <button onClick={handleZoomOut} style={btnStyle}>Zoom Out</button>
          <button onClick={handleReset} style={btnStyle}>Reset Camera</button>
          <button onClick={handleMeasure} style={btnStyle}>Measure Distance</button>
        </div>

        {distance !== null && (
          <p style={{ marginTop: "12px", color: "#38bdf8" }}>
            <strong>Measured Distance</strong>: {distance.toFixed(4)} meters
          </p>
        )}

        <div style={{ marginTop: "16px" }}>
          <h4>Assembly Coordinate Annotations:</h4>
          <ul>
            {annotations.map((ann) => (
              <li key={ann.id}>
                <strong>{ann.label}</strong> at [{ann.position.join(", ")}]
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

const btnStyle: React.CSSProperties = {
  background: "#0284c7",
  color: "#ffffff",
  border: "none",
  padding: "8px 16px",
  borderRadius: "4px",
  cursor: "pointer",
  fontWeight: "bold"
};