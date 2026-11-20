import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Html, Environment } from '@react-three/drei';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import * as THREE from 'three';
import './App.css';
import { API_BASE_URL } from './config';

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

function useBoneData(meshId: string | null, allBones: BoneData[]) {
  const [state, setState] = useState<FetchState>('idle');
  const [data, setData] = useState<BoneData | null>(null);

  useEffect(() => {
    if (!meshId) {
      setState('idle');
      setData(null);
      return;
    }

    // Fast-path: Instant in-memory lookup from pre-fetched allBones (0ms latency!)
    const cleanId = meshId.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').toLowerCase();
    const localMatch = allBones.find(b => {
      const bClean = b.mesh_id.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').toLowerCase();
      return b.mesh_id === meshId || bClean === cleanId || b.common_name.toLowerCase() === cleanId || bClean.includes(cleanId) || cleanId.includes(bClean);
    });

    if (localMatch) {
      setData(localMatch);
      setState('found');
      return;
    }

    // Fallback: Fetch from backend API if not in memory
    setState('loading');
    setData(null);

    const controller = new AbortController();
    fetch(`${API_BASE_URL}/api/bones/${encodeURIComponent(meshId)}`, {
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
  }, [meshId, allBones]);

  return { state, data };
}

// ─── Skeleton model ───────────────────────────────────────────────────────────

function SkeletonModel({ 
  onBoneClick, 
  selectedId,
  wrongId,
  onBoneHover,
}: { 
  onBoneClick: (name: string) => void;
  selectedId: string | null;
  wrongId?: string | null;
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
        
        const normalizedMeshName = mesh.name.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').toLowerCase();
        const normalizedSelectedId = selectedId ? selectedId.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').toLowerCase() : null;
        const normalizedWrongId = wrongId ? wrongId.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').toLowerCase() : null;
        
        const isSelected = selectedId && (mesh.name === selectedId || normalizedMeshName === normalizedSelectedId || mesh.name.replace(/_/g, ' ').toLowerCase().includes(normalizedSelectedId || ''));
        const isWrong = wrongId && (mesh.name === wrongId || normalizedMeshName === normalizedWrongId || mesh.name.replace(/_/g, ' ').toLowerCase().includes(normalizedWrongId || ''));
        
        if (isSelected) {
          mat.color.set('#22c55e'); // Green highlight
          mat.emissive.set('#166534');
          mat.emissiveIntensity = 0.5;
        } else if (isWrong) {
          mat.color.set('#ef4444'); // Red highlight
          mat.emissive.set('#7f1d1d');
          mat.emissiveIntensity = 0.5;
        } else if (origColor) {
          mat.color.copy(origColor);
          mat.emissive.set('#000000');
          mat.emissiveIntensity = 0;
        }
      }
    });
  }, [selectedId, wrongId, clonedScene]);

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
    const cleanId = selectedId.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').trim().toLowerCase();

    // Priority 1: Exact match on mesh name or normalized ID
    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh && !targetMesh) {
        const childClean = child.name.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').trim().toLowerCase();
        if (child.name.toLowerCase() === selectedId.toLowerCase() || childClean === cleanId) {
          targetMesh = child as THREE.Mesh;
        }
      }
    });

    // Priority 2: Substring / keyword boundary match
    if (!targetMesh) {
      scene.traverse((child) => {
        if ((child as THREE.Mesh).isMesh && !targetMesh) {
          const childClean = child.name.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').trim().toLowerCase();
          if (childClean.includes(cleanId) || cleanId.includes(childClean)) {
            targetMesh = child as THREE.Mesh;
          }
        }
      });
    }

    const group = new THREE.Group();
    if (targetMesh !== null) {
      const mesh = targetMesh as THREE.Mesh;
      const clonedMesh = mesh.clone();
      const geom = mesh.geometry.clone();
      
      // Compute bounding box and dimensions before centering
      geom.computeBoundingBox();
      const box = geom.boundingBox || new THREE.Box3();
      const size = new THREE.Vector3();
      box.getSize(size);
      
      // Center geometry around [0, 0, 0]
      geom.center();
      clonedMesh.geometry = geom;

      // Auto-scale so bone fills the viewport at perfect inspection size (2.2 units)
      const maxDim = Math.max(size.x, size.y, size.z);
      const targetSize = 2.2;
      const scaleFactor = maxDim > 0 ? targetSize / maxDim : 1.0;

      clonedMesh.scale.set(scaleFactor, scaleFactor, scaleFactor);
      clonedMesh.position.set(0, 0, 0);
      clonedMesh.rotation.set(0, 0, 0);

      // Realistic anatomical bone shader with double-sided rendering for hollow landmarks
      clonedMesh.material = new THREE.MeshStandardMaterial({
        color: '#f4efe6',
        roughness: 0.35,
        metalness: 0.05,
        side: THREE.DoubleSide,
      });

      group.add(clonedMesh);
    } else {
      // Safe fallback box to prevent any empty group
      const fallbackGeo = new THREE.BoxGeometry(0.8, 0.8, 0.8);
      const fallbackMat = new THREE.MeshStandardMaterial({ color: '#6366f1', wireframe: true });
      group.add(new THREE.Mesh(fallbackGeo, fallbackMat));
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
  onCollapse,
  onInspect3D,
  viewMode,
}: {
  fetchState: FetchState;
  data: BoneData | null;
  selectedId: string | null;
  onClose: () => void;
  onCollapse?: () => void;
  onInspect3D: () => void;
  viewMode: 'skeleton' | 'isolated' | 'quiz';
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
        <div className="panel-not-found" style={{ position: 'relative' }}>
          <div className="panel-header-actions">
            {onCollapse && (
              <button 
                type="button" 
                className="panel-collapse-btn" 
                onClick={onCollapse} 
                title="Hide details (drag down)"
                aria-label="Hide details"
              >
                ▼
              </button>
            )}
            <button 
              type="button" 
              className="panel-close-btn" 
              onClick={onClose} 
              title="Close panel"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
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
        <div className="panel-header" style={{ position: 'relative' }}>
          <div className="panel-header-actions">
            {onCollapse && (
              <button 
                type="button" 
                className="panel-collapse-btn" 
                onClick={onCollapse} 
                title="Hide details (drag down)"
                aria-label="Hide details"
              >
                ▼
              </button>
            )}
            <button 
              type="button" 
              className="panel-close-btn" 
              onClick={onClose} 
              title="Close panel"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
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

          {viewMode !== 'isolated' && (
            <button className="inspect-bone-btn" onClick={onInspect3D}>
              🔬 Inspect in 3D Isolation
            </button>
          )}
        </div>
      </div>
    );
  }

  return null;
}


// ─── Search and Quiz Components ───────────────────────────────────────────────

function useAllBones() {
  const [bones, setBones] = useState<BoneData[]>([]);
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/bones`)
      .then(res => res.json())
      .then(data => setBones(data))
      .catch(err => console.error('Failed to fetch bones:', err));
  }, []);
  return bones;
}

function SearchBar({ bones, onSelect }: { bones: BoneData[], onSelect: (id: string) => void }) {
  const [query, setQuery] = useState('');
  const [isOpenMobile, setIsOpenMobile] = useState(false);

  const filtered = query.length > 0 ? bones.filter(b => 
    b.common_name.toLowerCase().includes(query.toLowerCase()) || 
    b.mesh_id.toLowerCase().includes(query.toLowerCase()) ||
    (b.latin_name && b.latin_name.toLowerCase().includes(query.toLowerCase()))
  ) : bones; // show all when empty

  return (
    <>
      <button 
        type="button"
        className="mobile-search-toggle" 
        onClick={() => setIsOpenMobile(prev => !prev)}
        aria-label="Search bones"
      >
        <span>🔍</span>
        <span className="mobile-search-text">Search Bones</span>
      </button>

      <div className={`search-panel ${isOpenMobile ? 'mobile-open' : ''}`}>
        <div className="search-panel-header">
          <h3 className="search-panel-title">Explore Bones</h3>
          <button 
            type="button"
            className="search-close-mobile-btn" 
            onClick={() => setIsOpenMobile(false)}
            aria-label="Close search"
          >
            ✕
          </button>
        </div>
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Search bones..." 
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="search-results">
          {filtered.length === 0 ? (
            <div className="search-result-item empty">No results found</div>
          ) : (
            filtered.map(b => (
              <div 
                key={b.mesh_id} 
                className="search-result-item"
                onClick={() => {
                  onSelect(b.mesh_id);
                  setIsOpenMobile(false);
                }}
              >
                <div className="search-result-name">{b.common_name}</div>
                <div className="search-result-system">{b.system || 'Skeletal System'}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}

function QuizPanel({
  targetBone,
  score,
  onSkip,
  onExit,
  feedback
}: {
  targetBone: BoneData | null;
  score: number;
  onSkip: () => void;
  onExit: () => void;
  feedback: 'correct' | 'incorrect' | null;
}) {
  return (
    <div className="quiz-panel">
      <div className="quiz-header">
        <h3>Quiz Mode</h3>
        <div className="quiz-score">Score: {score}</div>
      </div>
      
      <div className="quiz-body">
        <p className="quiz-prompt">Find and click the:</p>
        <h2 className="quiz-target">{targetBone?.common_name || '...'}</h2>
        
        {feedback === 'correct' && <div className="quiz-feedback correct">Correct! 🎉</div>}
        {feedback === 'incorrect' && <div className="quiz-feedback incorrect">Try again! ❌</div>}
      </div>

      <div className="quiz-footer">
        <button className="quiz-btn skip" onClick={onSkip}>Skip</button>
        <button className="quiz-btn exit" onClick={onExit}>Exit Quiz</button>
      </div>
    </div>
  );
}


// ─── Scene wrappers ─────────────

function SkeletonScene({
  selectedId,
  wrongId,
  onBoneClick,
  onBoneHover,
}: {
  selectedId: string | null;
  wrongId?: string | null;
  onBoneClick: (id: string) => void;
  onBoneHover: (name: string | null) => void;
}) {
  return (
    <SkeletonModel onBoneClick={onBoneClick} selectedId={selectedId} wrongId={wrongId} onBoneHover={onBoneHover} />
  );
}

function IsolatedScene({
  selectedId,
}: {
  selectedId: string;
}) {
  return (
    <>
      <ambientLight intensity={0.65} />
      <directionalLight position={[4, 5, 4]} intensity={1.8} castShadow />
      <directionalLight position={[-4, 2, -2]} intensity={0.7} color="#a5b4fc" />
      <directionalLight position={[0, -3, 3]} intensity={0.4} color="#e2e8f0" />
      <directionalLight position={[0, 4, -4]} intensity={0.6} color="#ffffff" />
      <pointLight position={[0, 2, 3]} intensity={0.6} color="#60a5fa" />

      <IsolatedBoneModel selectedId={selectedId} />
    </>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [hoveredBone, setHoveredBone] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'skeleton' | 'isolated' | 'quiz'>('skeleton');
  const allBones = useAllBones();
  const [quizTarget, setQuizTarget] = useState<BoneData | null>(null);
  const [quizScore, setQuizScore] = useState(0);
  const [quizFeedback, setQuizFeedback] = useState<'correct' | 'incorrect' | null>(null);
  const [wrongClickId, setWrongClickId] = useState<string | null>(null);

  // Hideable / collapsible detail panel states and drag gesture
  const [isDetailCollapsed, setIsDetailCollapsed] = useState(false);
  const [dragY, setDragY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const startYRef = useRef(0);
  const collapsedStartYRef = useRef(0);

  useEffect(() => {
    if (selectedId) {
      setIsDetailCollapsed(false);
      setDragY(0);
    }
  }, [selectedId]);

  const handleDragStart = useCallback((e: React.PointerEvent) => {
    try {
      (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    } catch {}
    startYRef.current = e.clientY;
    setIsDragging(true);
  }, []);

  const handleDragMove = useCallback((e: React.PointerEvent) => {
    if (!isDragging) return;
    const deltaY = e.clientY - startYRef.current;
    if (deltaY > 0) {
      setDragY(deltaY);
    } else {
      setDragY(deltaY * 0.15);
    }
  }, [isDragging]);

  const handleDragEnd = useCallback((e: React.PointerEvent) => {
    if (!isDragging) return;
    try {
      (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {}
    setIsDragging(false);
    const deltaY = e.clientY - startYRef.current;
    if (deltaY > 50) {
      setIsDetailCollapsed(true);
    }
    setDragY(0);
  }, [isDragging]);

  const handleDragCancel = useCallback((e: React.PointerEvent) => {
    if (!isDragging) return;
    try {
      (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {}
    setIsDragging(false);
    setDragY(0);
  }, [isDragging]);

  const handleCollapsedPointerDown = useCallback((e: React.PointerEvent) => {
    try {
      (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    } catch {}
    collapsedStartYRef.current = e.clientY;
  }, []);

  const handleCollapsedPointerUp = useCallback((e: React.PointerEvent) => {
    try {
      (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {}
    const deltaY = e.clientY - collapsedStartYRef.current;
    // Tapping or swiping up expands it
    if (deltaY < -15 || Math.abs(deltaY) < 12) {
      setIsDetailCollapsed(false);
    }
  }, []);

  const nextQuizQuestion = useCallback(() => {
    if (allBones.length === 0) return;
    const randomBone = allBones[Math.floor(Math.random() * allBones.length)];
    setQuizTarget(randomBone);
    setQuizFeedback(null);
    setWrongClickId(null);
  }, [allBones]);

  const handleStartQuiz = useCallback(() => {
    setViewMode('quiz');
    setQuizScore(0);
    setSelectedId(null);
    nextQuizQuestion();
  }, [nextQuizQuestion]);

  const handleExitQuiz = useCallback(() => {
    setViewMode('skeleton');
    setQuizTarget(null);
    setQuizFeedback(null);
    setWrongClickId(null);
  }, []);
  const controlsRef = useRef<OrbitControlsImpl | null>(null);
  const { state: fetchState, data: boneData } = useBoneData(selectedId, allBones);

  const handleBoneClick = useCallback((id: string) => {
    if (viewMode === 'quiz') {
      if (!quizTarget || quizFeedback === 'correct') return;
      
      const normalizedId = id.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').toLowerCase();
      const normalizedTarget = quizTarget.mesh_id.replace(/_[a-zA-Z]+_\d+$/, '').replace(/__\d+$/, '').replace(/_/g, ' ').toLowerCase();
      
      const isCorrect = id === quizTarget.mesh_id || normalizedId === normalizedTarget || id.replace(/_/g, ' ').toLowerCase().includes(normalizedTarget);
      
      if (isCorrect) {
        setQuizFeedback('correct');
        setQuizScore(s => s + 1);
        setWrongClickId(null);
        setTimeout(() => {
          nextQuizQuestion();
        }, 1500);
      } else {
        setQuizFeedback('incorrect');
        setWrongClickId(id);
        setTimeout(() => {
          setQuizFeedback(null);
          setWrongClickId(null);
        }, 1000);
      }
      return;
    }

    // Normal exploration: simply select the bone
    setSelectedId(id);
    setIsDetailCollapsed(false);
  }, [viewMode, quizTarget, nextQuizQuestion, quizFeedback]);

  const handleInspect3D = useCallback(() => {
    if (selectedId) {
      setViewMode('isolated');
      if (controlsRef.current) {
        const controls = controlsRef.current;
        controls.target.set(0, 0, 0);
        const camera = controls.object as THREE.PerspectiveCamera;
        camera.near = 0.01;
        camera.far = 100;
        camera.zoom = 1;
        camera.position.set(0, 0.4, 3.2);
        camera.updateProjectionMatrix();
        controls.update();
      }
    }
  }, [selectedId]);

  const handleClosePanel = useCallback(() => {
    setSelectedId(null);
    setIsDetailCollapsed(false);
    if (viewMode === 'isolated') {
      setViewMode('skeleton');
    }
    if (controlsRef.current) {
      const controls = controlsRef.current;
      const camera = controls.object as THREE.PerspectiveCamera;
      camera.near = 0.001;
      camera.far = 200;
      camera.zoom = 1;
      camera.position.set(0, 0.2, 3.5);
      camera.updateProjectionMatrix();
      controls.target.set(0, 0, 0);
      controls.update();
    }
  }, [viewMode]);

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

  // Pan controls for D-pad buttons
  const handlePan = useCallback((direction: 'up' | 'down' | 'left' | 'right') => {
    const controls = controlsRef.current;
    if (!controls) return;
    const camera = controls.object as THREE.PerspectiveCamera;
    
    // Ensure the camera's matrixWorld is up to date
    camera.updateMatrixWorld();
    
    // Calculate the right and up vectors from the camera
    const right = new THREE.Vector3();
    const up = new THREE.Vector3();
    camera.matrixWorld.extractBasis(right, up, new THREE.Vector3());
    
    // Amount to pan based on distance to target
    const distance = camera.position.distanceTo(controls.target);
    const panAmount = Math.max(0.01, distance * 0.1); 
    
    const panOffset = new THREE.Vector3();
    
    switch (direction) {
      case 'up':
        panOffset.copy(up).multiplyScalar(panAmount);
        break;
      case 'down':
        panOffset.copy(up).multiplyScalar(-panAmount);
        break;
      case 'left':
        panOffset.copy(right).multiplyScalar(-panAmount);
        break;
      case 'right':
        panOffset.copy(right).multiplyScalar(panAmount);
        break;
    }
    
    camera.position.add(panOffset);
    controls.target.add(panOffset);
    controls.update();
  }, []);

  // Format hovered mesh name for tooltip display
  const formatBoneName = (meshId: string) => {
    return meshId
      .replace(/_[a-zA-Z]+_0$/, '')  // Strip Three.js material suffix (e.g. _beige_0)
      .replace(/__0$/, '')            // Strip original GLB suffix
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
            onPointerMissed={() => {
              if (viewMode === 'skeleton') {
                setSelectedId(null);
              }
            }}
          >
            <Environment preset="city" />
            <ambientLight intensity={0.5} />
            <directionalLight position={[3, 5, 3]} intensity={1.3} castShadow />
            <directionalLight position={[-3, 2, -3]} intensity={0.4} color="#4f6ef7" />
            <pointLight position={[0, 2, 2]} intensity={0.5} color="#60a5fa" />

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
              <group visible={viewMode !== 'isolated'}>
                <SkeletonScene
                  selectedId={viewMode === 'quiz' ? null : selectedId}
                  wrongId={wrongClickId}
                  onBoneClick={handleBoneClick}
                  onBoneHover={handleBoneHover}
                />
              </group>

              {viewMode === 'isolated' && selectedId && (
                <IsolatedScene selectedId={selectedId} />
              )}
            </React.Suspense>

            <OrbitControls
              ref={(ref) => {
                controlsRef.current = ref;
                if (ref) {
                  // Enable zoom-to-cursor: scroll zooms toward where your mouse points
                  (ref as any).zoomToCursor = true;
                }
              }}
              makeDefault
              enablePan
              panSpeed={1.0}
              zoomSpeed={1.5}
              autoRotate={viewMode === 'isolated'}
              autoRotateSpeed={1.0}
              minDistance={0.1}
              maxDistance={15}
              minPolarAngle={0}
              maxPolarAngle={Math.PI}
              enableDamping
              dampingFactor={0.08}
              // Right-click = pan, left-click = rotate, scroll = zoom
              mouseButtons={{
                LEFT: THREE.MOUSE.ROTATE,
                MIDDLE: THREE.MOUSE.DOLLY,
                RIGHT: THREE.MOUSE.PAN,
              }}
            />
          </Canvas>
        </div>

        {viewMode !== 'isolated' && <SearchBar bones={allBones} onSelect={handleBoneClick} />}
        
        {/* Floating banner when in 3D Isolated mode */}
        {viewMode === 'isolated' && boneData && (
          <div className="isolated-mode-banner">
            <div className="isolated-banner-badge">🔬 3D Inspection Mode</div>
            <h2 className="isolated-banner-title">{boneData.common_name}</h2>
            {boneData.latin_name && <p className="isolated-banner-latin">{boneData.latin_name}</p>}
            {boneData.nepali_name && (
              <span className="isolated-banner-nepali">{boneData.nepali_name}</span>
            )}
            <div className="isolated-banner-hint">
              Drag to rotate 360° · Scroll to zoom · Auto-turntable active
            </div>
            <button className="isolated-back-btn" onClick={handleClosePanel}>
              ← Back to Full Skeleton
            </button>
          </div>
        )}
        
        {viewMode === 'quiz' && (
          <QuizPanel 
            targetBone={quizTarget} 
            score={quizScore} 
            onSkip={nextQuizQuestion} 
            onExit={handleExitQuiz}
            feedback={quizFeedback}
          />
        )}

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
              <button className="nav-pill active" onClick={handleClosePanel} style={{ fontSize: '1rem', padding: '8px 20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>←</span> Back to Skeleton
              </button>
            ) : (
              <nav className="nav-pills">
                <button className={`nav-pill ${viewMode === 'skeleton' ? 'active' : ''}`} onClick={handleExitQuiz}>Skeleton</button>
                <button className={`nav-pill ${viewMode === 'quiz' ? 'active' : ''}`} onClick={handleStartQuiz} disabled={allBones.length === 0}>Quiz</button>
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

        {/* Pan controls */}
        <div className="pan-controls">
          <button className="pan-btn up" onClick={() => handlePan('up')} title="Pan Up">↑</button>
          <div className="pan-row">
            <button className="pan-btn left" onClick={() => handlePan('left')} title="Pan Left">←</button>
            <button className="pan-btn down" onClick={() => handlePan('down')} title="Pan Down">↓</button>
            <button className="pan-btn right" onClick={() => handlePan('right')} title="Pan Right">→</button>
          </div>
        </div>

        {/* Zoom hint — skeleton mode only */}
        {(viewMode === 'skeleton' || viewMode === 'quiz') && !selectedId && (
          <div className="zoom-hint">
            <span className="zoom-hint-icon">🔍</span>
            Scroll to zoom in · Click any bone · Right-drag to pan
          </div>
        )}
      </div>

      {/* Side Panel / Bottom Sheet (Hideable / Draggable) */}
      {selectedId && !isDetailCollapsed && (
        <div 
          className="side-panel-area"
          style={{
            transform: isDragging && dragY > 0 ? `translateY(${dragY}px)` : undefined,
            transition: isDragging ? 'none' : 'transform 0.28s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        >
          {/* Drag Handle & Collapse Bar */}
          <div 
            className="drawer-drag-header"
            onPointerDown={handleDragStart}
            onPointerMove={handleDragMove}
            onPointerUp={handleDragEnd}
            onPointerCancel={handleDragCancel}
            onClick={() => {
              if (dragY === 0) setIsDetailCollapsed(true);
            }}
            title="Drag down or tap to hide details"
          >
            <div className="drawer-drag-pill" />
            <div className="drawer-drag-row">
              <span className="drawer-drag-hint">▼ Drag down or tap to hide</span>
              <button 
                type="button" 
                className="drawer-collapse-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsDetailCollapsed(true);
                }}
                title="Hide details"
              >
                ▼ Hide
              </button>
            </div>
          </div>

          <InfoPanel
            fetchState={fetchState}
            data={boneData}
            selectedId={selectedId}
            onClose={handleClosePanel}
            onCollapse={() => setIsDetailCollapsed(true)}
            onInspect3D={handleInspect3D}
            viewMode={viewMode}
          />
        </div>
      )}

      {/* Collapsed Floating Mini Bar (when detail is hidden) */}
      {selectedId && isDetailCollapsed && (
        <div 
          className="detail-collapsed-bar"
          onPointerDown={handleCollapsedPointerDown}
          onPointerUp={handleCollapsedPointerUp}
          title="Drag up or tap to view details"
        >
          <div className="collapsed-bar-handle" />
          <div className="collapsed-bar-content">
            <div className="collapsed-bar-info">
              <span className="collapsed-bar-icon">🦴</span>
              <span className="collapsed-bar-title">{boneData?.common_name || formatBoneName(selectedId)}</span>
              {boneData?.nepali_name && (
                <span className="collapsed-bar-nepali">{boneData.nepali_name}</span>
              )}
            </div>
            <div className="collapsed-bar-actions">
              <button 
                type="button"
                className="collapsed-expand-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsDetailCollapsed(false);
                }}
                title="View bone details"
              >
                ▲ Details
              </button>
              <button 
                type="button"
                className="collapsed-close-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  handleClosePanel();
                }}
                title="Deselect bone"
              >
                ✕
              </button>
            </div>
          </div>
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
