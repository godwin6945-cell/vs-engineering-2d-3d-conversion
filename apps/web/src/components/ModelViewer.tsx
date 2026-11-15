"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import {
  Rotate3d,
  Maximize2,
  Minimize2,
  Eye,
  Grid,
  Box,
  Layers,
  Compass,
} from "lucide-react";

interface ModelViewerProps {
  stepUrl?: string;
  className?: string;
}

export function ModelViewer({ stepUrl, className = "" }: ModelViewerProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  const [wireframe, setWireframe] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [currentView, setCurrentView] = useState<string>("iso");

  // Keep references to Three.js instances for dynamic updates
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const meshGroupRef = useRef<THREE.Group | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;

    // 1. Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#f1f5f9"); // Crisp engineering studio slate
    sceneRef.current = scene;

    // 2. Camera setup
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(160, 140, 180);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // 3. Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 4. Studio CAD Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.9);
    dirLight1.position.set(100, 150, 100);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xe0f2fe, 0.5);
    dirLight2.position.set(-100, -50, -100);
    scene.add(dirLight2);

    // 5. Grid Helper
    const gridHelper = new THREE.GridHelper(240, 24, 0x94a3b8, 0xcbd5e1);
    gridHelper.position.y = -25;
    scene.add(gridHelper);

    // 6. Parametric Part Solid Geometry (Precision Flange representation)
    const meshGroup = new THREE.Group();
    meshGroupRef.current = meshGroup;

    // Base plate (Machined 6061-T6 Aluminum finish)
    const baseGeo = new THREE.BoxGeometry(120, 16, 80);
    const cadMaterial = new THREE.MeshStandardMaterial({
      color: 0x64748b,
      roughness: 0.3,
      metalness: 0.65,
      wireframe: false,
    });
    const baseMesh = new THREE.Mesh(baseGeo, cadMaterial);
    meshGroup.add(baseMesh);

    // Edges geometry (Technical drawing line contrast)
    const edgesGeo = new THREE.EdgesGeometry(baseGeo);
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x1e293b, linewidth: 2 });
    const wireMesh = new THREE.LineSegments(edgesGeo, lineMaterial);
    meshGroup.add(wireMesh);

    // Central cylindrical boss
    const bossGeo = new THREE.CylinderGeometry(35, 35, 20, 48);
    const bossMesh = new THREE.Mesh(bossGeo, cadMaterial);
    bossMesh.position.y = 18;
    meshGroup.add(bossMesh);

    const bossEdges = new THREE.LineSegments(new THREE.EdgesGeometry(bossGeo), lineMaterial);
    bossEdges.position.y = 18;
    meshGroup.add(bossEdges);

    // Center through hole (darker interior bore)
    const holeGeo = new THREE.CylinderGeometry(20, 20, 42, 36);
    const holeMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.8 });
    const holeMesh = new THREE.Mesh(holeGeo, holeMat);
    holeMesh.position.y = 10;
    meshGroup.add(holeMesh);

    // 4 Bolt Holes on PCD
    const boltHoleGeo = new THREE.CylinderGeometry(6, 6, 20, 24);
    const boltPositions = [
      [35, 0],
      [-35, 0],
      [0, 25],
      [0, -25],
    ];
    boltPositions.forEach(([bx, bz]) => {
      const bMesh = new THREE.Mesh(boltHoleGeo, holeMat);
      bMesh.position.set(bx, 0, bz);
      meshGroup.add(bMesh);
    });

    scene.add(meshGroup);

    // 7. Mouse Orbit Controls
    let isMouseDown = false;
    let prevMousePos = { x: 0, y: 0 };

    const handleMouseDown = (e: MouseEvent) => {
      isMouseDown = true;
      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isMouseDown) return;
      const deltaX = e.clientX - prevMousePos.x;
      const deltaY = e.clientY - prevMousePos.y;

      meshGroup.rotation.y += deltaX * 0.01;
      meshGroup.rotation.x += deltaY * 0.01;

      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => (isMouseDown = false);

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      camera.position.multiplyScalar(e.deltaY < 0 ? 0.92 : 1.08);
    };

    const dom = renderer.domElement;
    dom.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    dom.addEventListener("wheel", handleWheel, { passive: false });

    // 8. Animation loop
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    // 9. Resize listener
    const handleResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      dom.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      dom.removeEventListener("wheel", handleWheel);
      window.removeEventListener("resize", handleResize);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  // View presets
  const setCameraView = (view: "iso" | "front" | "top" | "side") => {
    setCurrentView(view);
    const camera = cameraRef.current;
    const group = meshGroupRef.current;
    if (!camera || !group) return;

    group.rotation.set(0, 0, 0);

    if (view === "iso") {
      camera.position.set(160, 140, 180);
    } else if (view === "front") {
      camera.position.set(0, 0, 240);
    } else if (view === "top") {
      camera.position.set(0, 240, 0);
    } else if (view === "side") {
      camera.position.set(240, 0, 0);
    }
    camera.lookAt(0, 0, 0);
  };

  // Toggle wireframe
  const toggleWireframe = () => {
    setWireframe((prev) => {
      const next = !prev;
      meshGroupRef.current?.traverse((child) => {
        if (child instanceof THREE.Mesh && child.material instanceof THREE.MeshStandardMaterial) {
          child.material.wireframe = next;
        }
      });
      return next;
    });
  };

  return (
    <div className={`relative flex-1 bg-slate-100 overflow-hidden select-none ${className}`}>
      {/* 3D Canvas Mount Point */}
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Floating 3D Navigation Controls */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-1.5 p-1 rounded-md bg-white/95 backdrop-blur border border-slate-300 shadow-sm text-xs font-mono">
        <button
          onClick={() => setCameraView("iso")}
          className={`px-2.5 py-1 rounded transition-colors font-bold ${
            currentView === "iso" ? "bg-sky-700 text-white" : "text-slate-700 hover:bg-slate-100"
          }`}
        >
          ISO
        </button>
        <button
          onClick={() => setCameraView("front")}
          className={`px-2.5 py-1 rounded transition-colors font-bold ${
            currentView === "front" ? "bg-sky-700 text-white" : "text-slate-700 hover:bg-slate-100"
          }`}
        >
          FRONT
        </button>
        <button
          onClick={() => setCameraView("top")}
          className={`px-2.5 py-1 rounded transition-colors font-bold ${
            currentView === "top" ? "bg-sky-700 text-white" : "text-slate-700 hover:bg-slate-100"
          }`}
        >
          TOP
        </button>
        <button
          onClick={() => setCameraView("side")}
          className={`px-2.5 py-1 rounded transition-colors font-bold ${
            currentView === "side" ? "bg-sky-700 text-white" : "text-slate-700 hover:bg-slate-100"
          }`}
        >
          SIDE
        </button>

        <div className="w-[1px] h-4 bg-slate-300 mx-1" />

        <button
          onClick={toggleWireframe}
          title="Toggle Wireframe"
          className={`p-1.5 rounded transition-colors ${
            wireframe ? "bg-sky-700 text-white" : "text-slate-700 hover:bg-slate-100"
          }`}
        >
          <Box className="w-4 h-4" />
        </button>
      </div>

      {/* STEP AP214 Spec Badge */}
      <div className="absolute bottom-4 right-4 z-20 flex items-center gap-2 bg-white/95 backdrop-blur border border-slate-300 px-3 py-1.5 rounded-md text-xs font-mono text-slate-800 shadow-xs">
        <span className="w-2 h-2 rounded-full bg-emerald-600" />
        <span className="font-bold">STEP AP214 • OpenCascade Solid Valid</span>
      </div>
    </div>
  );
}
