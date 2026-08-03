import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Html, Environment, Bounds } from '@react-three/drei';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import * as THREE from 'three';
import './App.css';

// ─── Types ────────────────────────────────────────────────────────────────────

interface BoneData {
  mesh_id: string;
  common_name: string;
  latin_name?: string;
  nepali_name?: string;
  system?: string;
  description?: string;
  fun_fact?: string;
}

type FetchState = 'idle' | 'loading' | 'found' | 'not_found' | 'error';

// ─── Fetch hook ───────────────────────────────────────────────────────────────

function useBoneData(meshId: string | null) {
  const [state, setState] = useState<FetchState>('idle');
  const [data, setData] = useState<BoneData | null>(null);

  useEffect(() => {
    if (!meshId) { setState('idle'); setData(null); return; }
    setState('loading');
    setData(null);

    const controller = new AbortController();
    fetch(`http://localhost:8000/api/bones/${encodeURIComponent(meshId)}`, {
      signal: controller.signal,
    })
      .then(res => {
        if (res.status === 404) { setState('not_found'); return null; }
        if (!res.ok) throw new Error('Server error');
        return res.json();
      })
      .then(json => { if (json) { setData(json); setState('found'); } })
      .catch(err => { if (err.name !== 'AbortError') setState('error'); });

    return () => controller.abort();
  }, [meshId]);

  return { state, data };
}

// ─── Skeleton model ───────────────────────────────────────────────────────────

function SkeletonModel({ 
  onBoneClick, 
  selectedId,
  onBoneHover,
}: { 
  onBoneClick: (name: string) => void;
  selectedId: string | null;
  onBoneHover: (name: string | null) => void;
}) {
  const { scene } = useGLTF('/ct_derived_human_skeleton.glb');
  
  // Clone the scene so we can modify materials without affecting the cached version
  const clonedScene = React.useMemo(() => {
    const clone = scene.clone();
    
    // We need to store original materials so we can revert them
    clone.userData.originalMaterials = new Map();

    clone.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        // Clone the material so highlighting one bone doesn't highlight others sharing it
        mesh.material = (mesh.material as THREE.Material).clone();
        clone.userData.originalMaterials.set(mesh.name, (mesh.material as THREE.MeshStandardMaterial).color.clone());
      }
    });
    return clone;
  }, [scene]);

  // Handle highlighting when selectedId changes
  useEffect(() => {
    clonedScene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        const mat = mesh.material as THREE.MeshStandardMaterial;
        const origColor = clonedScene.userData.originalMaterials.get(mesh.name);
        
        if (selectedId && mesh.name === selectedId) {
          mat.color.set('#f59e0b'); // Amber/Orange highlight
          mat.emissive.set('#92400e');
          mat.emissiveIntensity = 0.5;
        } else if (origColor) {
          mat.color.copy(origColor);
          mat.emissive.set('#000000');
          mat.emissiveIntensity = 0;
        }
      }
    });
  }, [selectedId, clonedScene]);

  return (
    <primitive 
      object={clonedScene} 
      scale={1} 
      onClick={(e: any) => {
        e.stopPropagation();
        onBoneClick(e.object.name || 'Unknown Bone');
      }}
      onPointerOver={(e: any) => {
        e.stopPropagation();
        document.body.style.cursor = 'pointer';
        onBoneHover(e.object.name || null);
      }}
      onPointerOut={(e: any) => {
        e.stopPropagation();
        document.body.style.cursor = 'auto';
        onBoneHover(null);
      }}
    />
  );
}
useGLTF.preload('/ct_derived_human_skeleton.glb');

// ─── Isolated bone model ──────────────────────────────────────────────────────

function IsolatedBoneModel({ selectedId }: { selectedId: string }) {
  const { scene } = useGLTF('/ct_derived_human_skeleton.glb');
  
  const isolatedGroup = React.useMemo(() => {
    let targetMesh: THREE.Mesh | null = null;
    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh && child.name === selectedId) {
        targetMesh = child as THREE.Mesh;
      }
    });

    const group = new THREE.Group();
    if (targetMesh !== null) {
      const mesh = targetMesh as THREE.Mesh;
      const clonedMesh = mesh.clone();
      clonedMesh.geometry = mesh.geometry.clone();
      clonedMesh.geometry.center(); // Center the geometry locally
      clonedMesh.position.set(0, 0, 0);
      clonedMesh.rotation.set(0, 0, 0);
      clonedMesh.scale.set(1, 1, 1);
      
      clonedMesh.material = new THREE.MeshStandardMaterial({
        color: '#e8edf5',
        roughness: 0.3,
        metalness: 0.1,
      });
      group.add(clonedMesh);
    }
    return group;
  }, [scene, selectedId]);

  return <primitive object={isolatedGroup} />;
}

// ─── Info panel ───────────────────────────────────────────────────────────────

function InfoPanel({
  fetchState,
  data,
  selectedId,
  onClose,
}: {
  fetchState: FetchState;
  data: BoneData | null;
  selectedId: string | null;
  onClose: () => void;
}) {
  if (!selectedId) {
    return null;
  }

  if (fetchState === 'loading') {
    return (
      <div className="info-panel">
        <div className="panel-loading">
          <div className="spinner" />
          <p>Loading bone data…</p>
        </div>
      </div>
    );
  }

  if (fetchState === 'not_found' || fetchState === 'error') {
    return (
      <div className="info-panel">
        <div className="panel-not-found">
          <div className="not-found-icon">🔍</div>
          <div className="not-found-title">No data for this bone yet</div>
          <div className="not-found-mesh">Mesh ID: {selectedId}</div>
          <p style={{fontSize: '0.75rem', color: '#888', marginTop: '10px'}}>
            (This mesh hasn't been mapped in the database yet.)
          </p>
          <button className="close-btn" style={{marginTop: '15px'}} onClick={onClose}>Dismiss</button>
        </div>
      </div>
    );
  }

  if (fetchState === 'found' && data) {
    return (
      <div className="info-panel">
        <div className="panel-header">
          <div className="panel-system-tag">
            🦴 {data.system || 'Skeletal System'}
          </div>
          <h2 className="panel-bone-name">{data.common_name}</h2>
          {data.latin_name && (
            <p className="panel-latin-name">{data.latin_name}</p>
          )}
        </div>

        <div className="panel-body">
          {data.nepali_name && (
            <div className="nepali-badge">
              <span className="nepali-badge-label">नेपाली</span>
              <span className="nepali-badge-text">{data.nepali_name}</span>
            </div>
          )}

          {data.description && (
            <p className="panel-description">{data.description}</p>
          )}

          {data.fun_fact && (
            <div className="fun-fact-box">
              <span className="fun-fact-icon">💡</span>
              <p className="fun-fact-text">{data.fun_fact}</p>
            </div>
          )}

        </div>
      </div>
    );
  }

  return null;
}

// ─── Scene wrappers ─────────────

function SkeletonScene({
  selectedId,
  onBoneClick,
  onBoneHover,
}: {
  selectedId: string | null;
  onBoneClick: (id: string) => void;
  onBoneHover: (name: string | null) => void;
}) {
  return (
    <>
      <Environment preset="city" />
      <ambientLight intensity={0.4} />
      <directionalLight position={[3, 5, 3]} intensity={1.2} castShadow />
      <directionalLight position={[-3, 2, -3]} intensity={0.4} color="#4f6ef7" />
      <pointLight position={[0, 2, 2]} intensity={0.5} color="#60a5fa" />

      <SkeletonModel onBoneClick={onBoneClick} selectedId={selectedId} onBoneHover={onBoneHover} />
    </>
  );
}

function IsolatedScene({
  selectedId,
}: {
  selectedId: string;
}) {
  return (
    <>
      <Environment preset="city" />
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 5, 5]} intensity={1.5} castShadow />
      <directionalLight position={[-5, 2, -5]} intensity={0.5} color="#4f6ef7" />
      
      <Bounds fit clip observe margin={1.2}>
        <IsolatedBoneModel selectedId={selectedId} />
      </Bounds>
    </>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [hoveredBone, setHoveredBone] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'skeleton' | 'isolated'>('skeleton');
  const controlsRef = useRef<OrbitControlsImpl | null>(null);
  const { state: fetchState, data: boneData } = useBoneData(selectedId);

  const handleBoneClick = useCallback((id: string) => {
    setSelectedId(id);
    setViewMode('isolated');
  }, []);

  const handleBack = useCallback(() => {
    setViewMode('skeleton');
    setSelectedId(null);
  }, []);

  const handleBoneHover = useCallback((name: string | null) => {
    setHoveredBone(name);
  }, []);

  // Zoom controls for +/- buttons
  const handleZoom = useCallback((direction: 'in' | 'out') => {
    const controls = controlsRef.current;
    if (!controls) return;
    const factor = direction === 'in' ? 0.75 : 1.35;
    const camera = controls.object as THREE.PerspectiveCamera;
    const offset = new THREE.Vector3().subVectors(camera.position, controls.target);
    offset.multiplyScalar(factor);
    camera.position.copy(controls.target).add(offset);
    controls.update();
  }, []);

  // Format hovered mesh name for tooltip display
  const formatBoneName = (meshId: string) => {
    return meshId
      .replace(/__0$/, '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase())
      .replace(/^L\s/, 'Left ')
      .replace(/^R\s/, 'Right ');
  };

  return (
    <div className="app-wrapper">
      {/* Main Area: 3D Canvas + Header */}
      <div className="main-area">
        <div className="canvas-layer">
          <Canvas
            shadows
            camera={{ position: [0, 0.2, 3.5], fov: 45, near: 0.001, far: 200 }}
            gl={{ antialias: true, alpha: false }}
          >
            <React.Suspense fallback={
              <Html center>
                <div style={{
                  background: 'rgba(5,10,20,0.9)',
                  border: '1px solid rgba(99,102,241,0.3)',
                  borderRadius: 12,
                  padding: '16px 28px',
                  color: '#a5b4fc',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 14,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                }}>
                  <div style={{
                    width: 18, height: 18,
                    border: '2px solid rgba(99,102,241,0.2)',
                    borderTopColor: '#6366f1',
                    borderRadius: '50%',
                    animation: 'spin 0.7s linear infinite',
                  }} />
                  Loading 3D Model…
                </div>
              </Html>
            }>
              {viewMode === 'skeleton' ? (
                <SkeletonScene
                  selectedId={selectedId}
                  onBoneClick={handleBoneClick}
                  onBoneHover={handleBoneHover}
                />
              ) : (
                <IsolatedScene selectedId={selectedId!} />
              )}
            </React.Suspense>

            <OrbitControls
              ref={controlsRef}
              makeDefault
              enablePan
              panSpeed={0.8}
              zoomSpeed={1.2}
              minDistance={viewMode === 'skeleton' ? 0.15 : 0.05}
              maxDistance={viewMode === 'skeleton' ? 8 : 10}
              minPolarAngle={0}
              maxPolarAngle={Math.PI}
              enableDamping
              dampingFactor={0.08}
            />
          </Canvas>
        </div>

        {/* Hover tooltip that follows cursor */}
        {hoveredBone && viewMode === 'skeleton' && (
          <HoverTooltip boneName={formatBoneName(hoveredBone)} />
        )}

        {/* UI Overlay for Header */}
        <div className="ui-layer">
          <header className="app-header">
            <div className="logo">
              <div className="logo-icon">🦴</div>
              <h1>Anatomy <span>Explorer</span></h1>
            </div>
            {viewMode === 'isolated' ? (
              <button className="nav-pill active" onClick={handleBack} style={{ fontSize: '1rem', padding: '8px 20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>←</span> Back to Skeleton
              </button>
            ) : (
              <nav className="nav-pills">
                <button className="nav-pill active">Skeleton</button>
                <button className="nav-pill" disabled title="Coming in Phase 3">Muscles</button>
              </nav>
            )}
          </header>
        </div>

        {/* Zoom controls */}
        <div className="zoom-controls">
          <button className="zoom-btn" onClick={() => handleZoom('in')} title="Zoom in">+</button>
          <button className="zoom-btn" onClick={() => handleZoom('out')} title="Zoom out">−</button>
        </div>

        {/* Zoom hint — skeleton mode only */}
        {viewMode === 'skeleton' && !selectedId && (
          <div className="zoom-hint">
            <span className="zoom-hint-icon">🔍</span>
            Scroll to zoom in · Click any bone · Right-drag to pan
          </div>
        )}
      </div>

      {/* Side Panel */}
      {selectedId && (
        <div className="side-panel-area">
          <InfoPanel
            fetchState={fetchState}
            data={boneData}
            selectedId={selectedId}
            onClose={handleBack}
          />
        </div>
      )}
    </div>
  );
}

// ─── Hover tooltip ──────────────────────────────────────────────────────────

function HoverTooltip({ boneName }: { boneName: string }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      setPos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handler);
    return () => window.removeEventListener('mousemove', handler);
  }, []);

  return (
    <div
      className="bone-hover-tooltip"
      style={{
        left: pos.x + 14,
        top: pos.y - 10,
      }}
    >
      {boneName}
    </div>
  );
}
