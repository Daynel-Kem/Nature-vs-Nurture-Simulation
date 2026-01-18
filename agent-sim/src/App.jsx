import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';

const Sidebar = ({ stats, selectedAgent, setSelectedAgent, isConnected, viewConfigs, activeView }) => {
  return (
    <div className="w-80 bg-gray-800 p-4 overflow-y-auto border-l border-gray-700">
      <h2 className="text-xl font-bold mb-4">Statistics</h2>
    
      <div className="space-y-4">
        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm text-gray-400">Round</div>
          <div className="text-2xl font-bold">{stats.round}</div>
        </div>

        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm text-gray-400">Alive Agents</div>
          <div className="text-2xl font-bold text-green-400">{stats.alive}</div>
        </div>

        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm text-gray-400">Dropouts</div>
          <div className="text-2xl font-bold text-red-400">{stats.dropouts}</div>
        </div>

        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm text-gray-400 mb-2">Avg Confidence by Class</div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-red-400">Low:</span>
              <span>{stats.avgConfidence.Low?.toFixed(3) || '0.000'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-400">Middle:</span>
              <span>{stats.avgConfidence.Middle?.toFixed(3) || '0.000'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-400">High:</span>
              <span>{stats.avgConfidence.High?.toFixed(3) || '0.000'}</span>
            </div>
          </div>
        </div>

        {selectedAgent && (
          <div className="bg-gradient-to-br from-blue-900 to-purple-900 border-2 border-blue-500 p-4 rounded-lg shadow-lg">
            <div className="flex justify-between items-start mb-3">
              <div className="text-lg font-bold text-blue-200">Selected Agent</div>
              <button 
                onClick={() => setSelectedAgent(null)}
                className="text-gray-400 hover:text-white text-xl leading-none"
              >
                ✕
              </button>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Name:</span>
                <span className="text-white">{selectedAgent.name}</span>
              </div>
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Class:</span>
                <span className={`font-bold ${
                  selectedAgent.class === 'High' ? 'text-blue-400' :
                  selectedAgent.class === 'Middle' ? 'text-green-400' :
                  'text-red-400'
                }`}>{selectedAgent.class}</span>
              </div>
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Age:</span>
                <span className="text-white">{selectedAgent.age}</span>
              </div>
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Talent:</span>
                <span className="text-white">{(selectedAgent.talent * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Money:</span>
                <span className="text-green-300 font-mono">${selectedAgent.money?.toFixed(0)}</span>
              </div>
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Confidence:</span>
                <span className="text-white">{(selectedAgent.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Competence:</span>
                <span className="text-white">{(selectedAgent.competence * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Aspiration:</span>
                <span className="text-white">{(selectedAgent.aspiration * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between border-b border-blue-700 pb-1">
                <span className="text-blue-300 font-semibold">Risk Tolerance:</span>
                <span className="text-white">{(selectedAgent['risk tolerance'] * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        )}

        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm text-gray-400 mb-2">Camera Controls</div>
          <div className="space-y-1 text-sm">
            <div>• Click + Drag = Rotate</div>
            <div>• Scroll = Zoom</div>
            <div>• Click Agent = Select</div>
          </div>
        </div>

        <div className="bg-gray-700 p-3 rounded">
          <div className="text-sm text-gray-400 mb-2">Current View</div>
          <div className="space-y-1 text-sm">
            <div>• <strong>X-axis:</strong> {viewConfigs[activeView].xAxis.label}</div>
            <div>• <strong>Y-axis:</strong> {viewConfigs[activeView].yAxis.label}</div>
            <div>• <strong>Z-axis:</strong> {viewConfigs[activeView].zAxis.label}</div>
            <div>• <strong>Size:</strong> Wealth/Money</div>
            <div>• <strong>Color:</strong> Class Identity</div>
          </div>
        </div>

        {!isConnected && (
          <div className="bg-yellow-900 border border-yellow-700 text-yellow-200 p-3 rounded text-sm">
            <p className="font-bold mb-2">Getting Started:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Start Flask backend</li>
              <li>Click "Connect"</li>
              <li>Click "Start"</li>
            </ol>
          </div>
        )}
      </div>
    </div>
  );
};

const SocialMobilityViz = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [agents, setAgents] = useState([]);
  const [stats, setStats] = useState({
    round: 0,
    alive: 0,
    dropouts: 0,
    avgConfidence: { Low: 0, Middle: 0, High: 0 }
  });
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [wsUrl, setWsUrl] = useState('http://localhost:5000');
  const [connectionError, setConnectionError] = useState('');
  const [autoRotate, setAutoRotate] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [cameraAngle, setCameraAngle] = useState({ theta: 0, phi: Math.PI / 4 });
  const [cameraDistance, setCameraDistance] = useState(120);
  const [webglError, setWebglError] = useState(false);
  const [visualMode, setVisualMode] = useState('spiral');
  const [activeView, setActiveView] = useState('self-knowledge');
  const [numAgents, setNumAgents] = useState(100);
  const [numRounds, setNumRounds] = useState(50);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const agentMeshesRef = useRef({});
  const wsRef = useRef(null);
  const animationFrameRef = useRef(null);
  const mouseDownPos = useRef({ x: 0, y: 0 });
  const lastCameraAngle = useRef({ theta: 0, phi: Math.PI / 4 });
  const raycasterRef = useRef(null);
  const mouseRef = useRef(new THREE.Vector2());
  
  const autoRotateRef = useRef(true);
  const isDraggingRef = useRef(false);
  const cameraAngleRef = useRef({ theta: 0, phi: Math.PI / 4 });
  const cameraDistanceRef = useRef(120);
  const visualModeRef = useRef('spiral');
  const activeViewRef = useRef('self-knowledge');

  // View configurations - all three axes used meaningfully
  const viewConfigs = {
    'self-knowledge': {
      name: 'Self-Knowledge',
      question: 'Who knows themselves accurately?',
      xAxis: { 
        label: 'TRUE TALENT', 
        getValue: (a) => a.talent,
        type: 'continuous'
      },
      yAxis: { 
        label: 'SELF BELIEF (Confidence)', 
        getValue: (a) => a.confidence 
      },
      zAxis: { 
        label: 'WEALTH CLASS', 
        getValue: (a) => ({ 'Low': 0.2, 'Middle': 0.5, 'High': 0.8 }[a.class]),
        type: 'categorical',
        categories: ['Low', 'Middle', 'High']
      },
      description: 'Does class affect how accurately people assess their own abilities?'
    },
    'aspiration-outcomes': {
      name: 'Aspiration → Outcomes',
      question: 'Does wanting more actually translate into outcomes?',
      xAxis: { 
        label: 'ASPIRATION', 
        getValue: (a) => a.aspiration,
        type: 'continuous'
      },
      yAxis: { 
        label: 'TOTAL REWARDS', 
        getValue: (a) => Math.min(a.total_rewards / 3000, 1) // Increased scale from 500 to 3000
      },
      zAxis: { 
        label: 'WEALTH CLASS', 
        getValue: (a) => ({ 'Low': 0.2, 'Middle': 0.5, 'High': 0.8 }[a.class]),
        type: 'categorical',
        categories: ['Low', 'Middle', 'High']
      },
      description: 'Do ambitious agents from different classes achieve different outcomes?'
    },
    'risk-behavior': {
      name: 'Risk Profile vs Behavior',
      question: 'Do agents act according to their risk profile?',
      xAxis: { 
        label: 'RISK TOLERANCE', 
        getValue: (a) => a['risk tolerance'],
        type: 'continuous'
      },
      yAxis: { 
        label: 'AVG TASK DIFFICULTY', 
        getValue: (a) => a.avg_task_difficulty || 0
      },
      zAxis: { 
        label: 'FAILURE RATE', 
        getValue: (a) => a.failure_rate || 0,
        type: 'continuous'
      },
      description: 'Are risk-takers choosing harder tasks? Are they failing more?'
    },
    'identity-hardening': {
      name: 'Identity Hardening',
      question: 'How identity hardens over time',
      xAxis: { 
        label: 'AGE', 
        getValue: (a) => a.age / 50,
        type: 'continuous'
      },
      yAxis: { 
        label: 'RISK TOLERANCE', 
        getValue: (a) => a['risk tolerance']
      },
      zAxis: { 
        label: 'ASPIRATION', 
        getValue: (a) => a.aspiration,
        type: 'continuous'
      },
      description: 'Do agents become more conservative and less ambitious as they age?'
    },
    'task-farming': {
      name: 'Task Farming',
      question: 'Who is farming low-risk tasks?',
      xAxis: { 
        label: 'TASK REPEATABILITY', 
        getValue: (a) => Math.min(a.task_repeatability / 20, 1),
        type: 'continuous'
      },
      yAxis: { 
        label: 'REWARD RATE', 
        getValue: (a) => Math.min((a.reward_rate || 0) / 10, 1)
      },
      zAxis: { 
        label: 'AGE', 
        getValue: (a) => a.age / 50,
        type: 'continuous'
      },
      description: 'Are older agents stuck repeating safe tasks for diminishing returns?'
    },
    'class-effect': {
      name: 'Pure Class Effect',
      question: 'What does class alone change?',
      xAxis: { 
        label: 'WEALTH CLASS', 
        getValue: (a) => ({ 'Low': 0.2, 'Middle': 0.5, 'High': 0.8 }[a.class]),
        type: 'categorical',
        categories: ['Low', 'Middle', 'High']
      },
      yAxis: { 
        label: 'FINAL REWARDS', 
        getValue: (a) => Math.min(a.total_rewards / 3000, 1) // Changed from 500 to 3000
      },
      zAxis: { 
        label: 'CONFIDENCE', 
        getValue: (a) => a.confidence,
        type: 'continuous'
      },
      description: 'For agents with similar talent (45-55%), how does class affect outcomes?',
      filter: (a) => a.talent >= 0.45 && a.talent <= 0.55
    }
  };

  const connectWebSocket = async () => {
    try {
      const io = (await import('socket.io-client')).default;
      
      const socket = io(wsUrl, {
        transports: ['websocket', 'polling']
      });
      
      socket.on('connect', () => {
        console.log('Connected to simulation server');
        setIsConnected(true);
        setConnectionError('');
      });
      
      socket.on('agent_update', (data) => {
        setAgents(data.agents);
        updateAgentPositions(data.agents);
      });
      
      socket.on('stats_update', (data) => {
        setStats(data.stats);
      });
      
      socket.on('simulation_complete', () => {
        setSimulationRunning(false);
        console.log('Simulation complete');
      });
      
      socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        setConnectionError('Failed to connect. Is the backend running on ' + wsUrl + '?');
        setIsConnected(false);
      });
      
      socket.on('disconnect', () => {
        console.log('Disconnected from server');
        setIsConnected(false);
      });
      
      wsRef.current = socket;
    } catch (error) {
      console.error('Connection error:', error);
      setConnectionError('Cannot connect to ' + wsUrl);
    }
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (!mountRef.current) return;

    while (mountRef.current.children.length > 0) {
      mountRef.current.removeChild(mountRef.current.lastChild);
    }

    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) {
      setWebglError(true);
      return;
    }

    try {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0a0a0a);
      sceneRef.current = scene;

      const camera = new THREE.PerspectiveCamera(
        75,
        mountRef.current.clientWidth / mountRef.current.clientHeight,
        0.1,
        1000
      );
      camera.position.set(0, 60, 100);
      camera.lookAt(0, 0, 0);
      cameraRef.current = camera;

      const renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true,
        failIfMajorPerformanceCaveat: false
      });
      renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
      mountRef.current.appendChild(renderer.domElement);
      rendererRef.current = renderer;

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
      scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
      directionalLight.position.set(10, 30, 10);
      scene.add(directionalLight);

      const backLight = new THREE.DirectionalLight(0x6666ff, 0.5);
      backLight.position.set(-10, 20, -10);
      scene.add(backLight);

      raycasterRef.current = new THREE.Raycaster();

      let rotationSpeed = 0.0003;
      const animate = () => {
        animationFrameRef.current = requestAnimationFrame(animate);
        
        if (autoRotateRef.current && !isDraggingRef.current) {
          const time = Date.now() * rotationSpeed;
          camera.position.x = Math.sin(time) * cameraDistanceRef.current;
          camera.position.z = Math.cos(time) * cameraDistanceRef.current;
          camera.position.y = 60;
        } else {
          const theta = cameraAngleRef.current.theta;
          const phi = cameraAngleRef.current.phi;
          camera.position.x = cameraDistanceRef.current * Math.sin(phi) * Math.cos(theta);
          camera.position.y = cameraDistanceRef.current * Math.cos(phi);
          camera.position.z = cameraDistanceRef.current * Math.sin(phi) * Math.sin(theta);
        }
        
        camera.lookAt(0, 0, 0);
        renderer.render(scene, camera);
      };
      animate();

      const handleResize = () => {
        if (!mountRef.current) return;
        const width = mountRef.current.clientWidth;
        const height = mountRef.current.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
      };
      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        if (mountRef.current && renderer.domElement) {
          mountRef.current.removeChild(renderer.domElement);
        }
        renderer.dispose();
      };
    } catch (error) {
      console.error('Error initializing Three.js:', error);
      setWebglError(true);
    }
  }, []);

  useEffect(() => {
    if (sceneRef.current) {
      const objectsToRemove = [];
      sceneRef.current.children.forEach(child => {
        if (child.type === 'GridHelper' || child.type === 'Line' || 
            child.type === 'Sprite' || child.type === 'LineSegments') {
          objectsToRemove.push(child);
        }
      });
      objectsToRemove.forEach(obj => {
        sceneRef.current.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (obj.material.map) obj.material.map.dispose();
          obj.material.dispose();
        }
      });

      createGridSystem(sceneRef.current, activeView);
      createAxisLabels(sceneRef.current, activeView);

      if (agents.length > 0) {
        updateAgentPositions(agents);
      }
    }
  }, [activeView]);

  useEffect(() => {
    autoRotateRef.current = autoRotate;
    isDraggingRef.current = isDragging;
    cameraAngleRef.current = cameraAngle;
    cameraDistanceRef.current = cameraDistance;
    visualModeRef.current = visualMode;
    activeViewRef.current = activeView;
  }, [autoRotate, isDragging, cameraAngle, cameraDistance, visualMode, activeView]);

  const createGridSystem = (scene, currentView) => {
    // Horizontal ground grid
    const groundGrid = new THREE.GridHelper(150, 30, 0x444444, 0x222222);
    scene.add(groundGrid);

    // Create axis lines
    const axisLineMaterial = new THREE.LineBasicMaterial({ color: 0x888888, linewidth: 2 });
    
    // X-axis
    const xAxisGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-75, 0, 0),
      new THREE.Vector3(75, 0, 0)
    ]);
    const xAxis = new THREE.Line(xAxisGeometry, axisLineMaterial);
    scene.add(xAxis);

    // Y-axis
    const yAxisGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 40, 0)
    ]);
    const yAxis = new THREE.Line(yAxisGeometry, axisLineMaterial);
    scene.add(yAxis);

    // Z-axis
    const zAxisGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, -60),
      new THREE.Vector3(0, 0, 60)
    ]);
    const zAxis = new THREE.Line(zAxisGeometry, axisLineMaterial);
    scene.add(zAxis);
  };

  const createAxisLabels = (scene, currentView) => {
    const config = viewConfigs[currentView];

    const createTextSprite = (text, size = 6) => {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = 512;
      canvas.height = 128;
      context.fillStyle = '#ffffff';
      context.font = 'Bold 48px Arial';
      context.textAlign = 'center';
      context.fillText(text, 256, 80);
      
      const texture = new THREE.CanvasTexture(canvas);
      texture.needsUpdate = true;
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.scale.set(size, size * 0.25, 1);
      return sprite;
    };

    const createNumberSprite = (text, size = 5) => {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = 256;
      canvas.height = 128;
      context.fillStyle = '#ffffff';
      context.font = 'Bold 56px Arial';
      context.textAlign = 'center';
      context.fillText(text, 128, 80);
      
      const texture = new THREE.CanvasTexture(canvas);
      texture.needsUpdate = true;
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.scale.set(size, size * 0.5, 1);
      return sprite;
    };

    // X-axis label
    const xLabel = createTextSprite(`${config.xAxis.label} →`, 12);
    xLabel.position.set(0, -3, -65);
    scene.add(xLabel);

    // Y-axis label
    const yLabel = createTextSprite(`↑ ${config.yAxis.label}`, 10);
    yLabel.position.set(-85, 20, 0);
    scene.add(yLabel);

    // Z-axis label
    const zLabel = createTextSprite(`← ${config.zAxis.label} →`, 12);
    zLabel.position.set(-85, -3, 0);
    scene.add(zLabel);

    // Y-axis markers (dynamic labels based on metric)
    const yLevels = [
      { value: 0, y: 3 },
      { value: 0.25, y: 11.75 },
      { value: 0.5, y: 20.5 },
      { value: 0.75, y: 29.25 },
      { value: 1.0, y: 38 }
    ];

    // Get appropriate labels for Y-axis based on metric
    const getYAxisLabel = (value) => {
      const label = config.yAxis.label;
      if (label.includes('WEALTH') || label.includes('REWARDS')) {
        return `$${Math.round(value * 3000)}`; // Changed from 500 to 3000
      } else if (label.includes('DIFFICULTY') || label.includes('RATE') || 
                 label.includes('TOLERANCE') || label.includes('BELIEF') ||
                 label.includes('CONFIDENCE') || label.includes('ASPIRATION') ||
                 label.includes('TALENT')) {
        return `${Math.round(value * 100)}%`;
      }
      return `${Math.round(value * 100)}%`;
    };

    yLevels.forEach(level => {
      const marker = createNumberSprite(getYAxisLabel(level.value), 5);
      marker.position.set(-20, level.y, -65); // Pushed from -10 to -20
      scene.add(marker);

      const tickGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-5, level.y, -65),
        new THREE.Vector3(5, level.y, -65)
      ]);
      const tickLine = new THREE.Line(tickGeometry, new THREE.LineBasicMaterial({ color: 0x888888 }));
      scene.add(tickLine);
    });

    // Z-axis markers (or categorical labels)
    if (config.zAxis.type === 'categorical') {
      const positions = [-50, 0, 50];
      config.zAxis.categories.forEach((category, idx) => {
        const marker = createNumberSprite(category, 5);
        marker.position.set(-95, -3, positions[idx]); // Pushed from -85 to -95
        scene.add(marker);
      });
    } else {
      const zLevels = [
        { value: 0, z: -50 },
        { value: 0.25, z: -25 },
        { value: 0.5, z: 0 },
        { value: 0.75, z: 25 },
        { value: 1.0, z: 50 }
      ];

      // Get appropriate labels for Z-axis based on metric
      const getZAxisLabel = (value) => {
        const label = config.zAxis.label;
        if (label.includes('AGE')) {
          return `${Math.round(value * 50)}y`;
        } else if (label.includes('FAILURE')) {
          return `${Math.round(value * 100)}%`;
        } else if (label.includes('ASPIRATION') || label.includes('CONFIDENCE')) {
          return `${Math.round(value * 100)}%`;
        }
        return `${Math.round(value * 100)}%`;
      };

      zLevels.forEach(level => {
        const marker = createNumberSprite(getZAxisLabel(level.value), 5);
        marker.position.set(-95, -3, level.z); // Pushed from -85 to -95
        scene.add(marker);
      });
    }

    // X-axis markers (or categorical labels)
    if (config.xAxis.type === 'categorical') {
      const positions = [-50, 0, 50];
      config.xAxis.categories.forEach((category, idx) => {
        const marker = createNumberSprite(category, 5);
        marker.position.set(positions[idx], -8, -65); // Pushed from -3 to -8
        scene.add(marker);
      });
    } else {
      const xLevels = [
        { value: 0, x: -50 },
        { value: 0.25, x: -25 },
        { value: 0.5, x: 0 },
        { value: 0.75, x: 25 },
        { value: 1.0, x: 50 }
      ];

      // Get appropriate labels for X-axis based on metric
      const getXAxisLabel = (value) => {
        const label = config.xAxis.label;
        if (label.includes('AGE')) {
          return `${Math.round(value * 50)}y`;
        } else if (label.includes('REPEATABILITY')) {
          return `${Math.round(value * 20)}x`;
        } else if (label.includes('TALENT') || label.includes('TOLERANCE') || 
                   label.includes('ASPIRATION')) {
          return `${Math.round(value * 100)}%`;
        }
        return `${Math.round(value * 100)}%`;
      };

      xLevels.forEach(level => {
        const marker = createNumberSprite(getXAxisLabel(level.value), 5);
        marker.position.set(level.x, -8, -65); // Pushed from -3 to -8
        scene.add(marker);
      });
    }
  };

  const calculatePosition = (agent, index, totalAgents) => {
    const config = viewConfigs[activeViewRef.current];
    
    const xValue = config.xAxis.getValue(agent);
    const yValue = config.yAxis.getValue(agent);
    const zValue = config.zAxis.getValue(agent);

    let x, y, z;

    // Map values to 3D space
    x = (xValue - 0.5) * 100;
    y = yValue * 35 + 3;
    z = (zValue - 0.5) * 100;

    // Add small jitter to prevent exact overlaps based on layout mode
    if (visualModeRef.current === 'scatter') {
      const hash = agent.id * 2654435761;
      x += ((hash % 100) / 100 - 0.5) * 3;
      z += (((hash >> 8) % 100) / 100 - 0.5) * 3;
    }

    return { x, y, z };
  };

  const updateAgentPositions = (agentData) => {
    if (!sceneRef.current || !agentData || agentData.length === 0) return;

    const config = viewConfigs[activeViewRef.current];
    
    // Apply filter if exists
    let filteredAgents = agentData;
    if (config.filter) {
      filteredAgents = agentData.filter(a => a.alive && config.filter(a));
    } else {
      filteredAgents = agentData.filter(a => a.alive);
    }

    // Remove agents that don't pass the filter
    agentData.forEach((agent) => {
      if ((!agent.alive || (config.filter && !config.filter(agent))) && agentMeshesRef.current[agent.id]) {
        sceneRef.current.remove(agentMeshesRef.current[agent.id]);
        agentMeshesRef.current[agent.id].geometry.dispose();
        agentMeshesRef.current[agent.id].material.dispose();
        delete agentMeshesRef.current[agent.id];
        return;
      }
    });

    filteredAgents.forEach((agent, index) => {
      let mesh = agentMeshesRef.current[agent.id];

      if (!mesh) {
        const geometry = new THREE.SphereGeometry(2, 16, 16);
        
        let baseColor;
        if (agent.class === 'High') {
          baseColor = new THREE.Color(0x4444ff);
        } else if (agent.class === 'Middle') {
          baseColor = new THREE.Color(0x44ff44);
        } else {
          baseColor = new THREE.Color(0xff4444);
        }
        
        const material = new THREE.MeshStandardMaterial({ 
          color: baseColor,
          emissive: new THREE.Color(0x000000),
          emissiveIntensity: 0,
          metalness: 0.4,
          roughness: 0.6,
          transparent: true,
          opacity: 0.9
        });
        mesh = new THREE.Mesh(geometry, material);
        
        mesh.userData = { agentId: agent.id };
        
        // Calculate initial position and spawn there
        const initialPos = calculatePosition(agent, index, filteredAgents.length);
        mesh.position.set(initialPos.x, initialPos.y, initialPos.z);
        
        // Store initial values for tracking changes
        mesh.userData.lastXValue = config.xAxis.getValue(agent);
        mesh.userData.lastYValue = config.yAxis.getValue(agent);
        mesh.userData.lastZValue = config.zAxis.getValue(agent);
        
        sceneRef.current.add(mesh);
        agentMeshesRef.current[agent.id] = mesh;
      }

      // Get current values
      const currentXValue = config.xAxis.getValue(agent);
      const currentYValue = config.yAxis.getValue(agent);
      const currentZValue = config.zAxis.getValue(agent);

      // Calculate target position
      const pos = calculatePosition(agent, index, filteredAgents.length);
      
      // Only update axes where values have changed (threshold of 0.001)
      const threshold = 0.001;
      
      if (Math.abs(currentXValue - (mesh.userData.lastXValue || 0)) > threshold) {
        // X value changed, update X position
        mesh.position.x += (pos.x - mesh.position.x) * 0.08;
        mesh.userData.lastXValue = currentXValue;
      }
      
      if (Math.abs(currentYValue - (mesh.userData.lastYValue || 0)) > threshold) {
        // Y value changed, update Y position
        mesh.position.y += (pos.y - mesh.position.y) * 0.08;
        mesh.userData.lastYValue = currentYValue;
      }
      
      if (Math.abs(currentZValue - (mesh.userData.lastZValue || 0)) > threshold) {
        // Z value changed, update Z position
        mesh.position.z += (pos.z - mesh.position.z) * 0.08;
        mesh.userData.lastZValue = currentZValue;
      }

      if (selectedAgent && selectedAgent.id === agent.id) {
        mesh.material.emissive.setHex(0xffffff);
        mesh.material.emissiveIntensity = 1.2;
        mesh.material.opacity = 1.0;
      } else {
        mesh.material.emissive.setHex(0x000000);
        mesh.material.emissiveIntensity = 0;
        mesh.material.opacity = 0.85;
      }

      const money = typeof agent.money === 'number' ? agent.money : 50;
      const scale = 1 + (money / 250);
      mesh.scale.setScalar(Math.min(scale, 2.5));
    });
  };

  const startSimulation = () => {
    if (wsRef.current && wsRef.current.connected) {
      Object.values(agentMeshesRef.current).forEach(mesh => {
        if (sceneRef.current) {
          sceneRef.current.remove(mesh);
        }
        mesh.geometry.dispose();
        mesh.material.dispose();
      });
      agentMeshesRef.current = {};
      setSelectedAgent(null);
      
      wsRef.current.emit('message', {
        command: 'start',
        params: {
          num_agents: numAgents,
          num_rounds: numRounds
        }
      });
      setSimulationRunning(true);
    } else {
      setConnectionError('Not connected to server');
    }
  };

  const pauseSimulation = () => {
    if (wsRef.current && wsRef.current.connected) {
      wsRef.current.emit('message', { command: 'pause' });
      setSimulationRunning(false);
    }
  };

  const resetSimulation = () => {
    if (wsRef.current && wsRef.current.connected) {
      wsRef.current.emit('message', { command: 'reset' });
      setSimulationRunning(false);
      
      Object.values(agentMeshesRef.current).forEach(mesh => {
        if (sceneRef.current) {
          sceneRef.current.remove(mesh);
        }
        mesh.geometry.dispose();
        mesh.material.dispose();
      });
      agentMeshesRef.current = {};
      setAgents([]);
      setSelectedAgent(null);
    }
  };

  const handleMouseDown = (e) => {
    if (!isDragging && raycasterRef.current && cameraRef.current && mountRef.current) {
      const rect = mountRef.current.getBoundingClientRect();
      mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      
      raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);
      const meshes = Object.values(agentMeshesRef.current);
      const intersects = raycasterRef.current.intersectObjects(meshes);
      
      if (intersects.length > 0) {
        const clickedMesh = intersects[0].object;
        const agentId = clickedMesh.userData.agentId;
        const agent = agents.find(a => a.id === agentId);
        if (agent) {
          setSelectedAgent(agent);
          return;
        }
      } else {
        setSelectedAgent(null);
      }
    }
    
    if (autoRotate) {
      setAutoRotate(false);
      autoRotateRef.current = false;
    }
    setIsDragging(true);
    isDraggingRef.current = true;
    mouseDownPos.current = { x: e.clientX, y: e.clientY };
    lastCameraAngle.current = { ...cameraAngle };
  };

  const handleMouseMove = (e) => {
    if (!isDragging) {
      if (raycasterRef.current && cameraRef.current && mountRef.current) {
        const rect = mountRef.current.getBoundingClientRect();
        mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        
        raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);
        const meshes = Object.values(agentMeshesRef.current);
        const intersects = raycasterRef.current.intersectObjects(meshes);
        
        if (intersects.length > 0) {
          mountRef.current.style.cursor = 'pointer';
        } else {
          mountRef.current.style.cursor = 'grab';
        }
      }
      return;
    }

    const deltaX = e.clientX - mouseDownPos.current.x;
    const deltaY = e.clientY - mouseDownPos.current.y;

    const newTheta = lastCameraAngle.current.theta - deltaX * 0.01;
    const newPhi = Math.max(0.1, Math.min(Math.PI - 0.1, 
      lastCameraAngle.current.phi + deltaY * 0.01));

    setCameraAngle({ theta: newTheta, phi: newPhi });
    cameraAngleRef.current = { theta: newTheta, phi: newPhi };
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    isDraggingRef.current = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const newDistance = Math.max(40, Math.min(250, cameraDistance + e.deltaY * 0.1));
    setCameraDistance(newDistance);
    cameraDistanceRef.current = newDistance;
  };

  useEffect(() => {
    const canvas = mountRef.current;
    if (!canvas) return;

    canvas.addEventListener('wheel', handleWheel);
    return () => canvas.removeEventListener('wheel', handleWheel);
  });

  useEffect(() => {
    if (selectedAgent) {
      const updatedAgent = agents.find(a => a.id === selectedAgent.id);
      if (updatedAgent) {
        setSelectedAgent(updatedAgent);
      }
    }
  }, [agents]);

  // Handle fullscreen resize
  useEffect(() => {
    if (rendererRef.current && cameraRef.current && mountRef.current) {
      // Small delay to ensure DOM has updated
      setTimeout(() => {
        const width = mountRef.current.clientWidth;
        const height = mountRef.current.clientHeight;
        cameraRef.current.aspect = width / height;
        cameraRef.current.updateProjectionMatrix();
        rendererRef.current.setSize(width, height);
      }, 100);
    }
  }, [isFullscreen]);

  return (
    <div className="w-full h-screen bg-gray-900 text-white flex flex-col">
      {!isFullscreen && (
        <div className="bg-gray-800 p-4 border-b border-gray-700">
          <h1 className="text-2xl font-bold mb-3">Social Mobility Simulation</h1>
          
          <div className="flex items-center gap-3 mb-3">
            <input
              type="text"
              value={wsUrl}
              onChange={(e) => setWsUrl(e.target.value)}
              placeholder="http://localhost:5000"
              className="px-3 py-1 bg-gray-700 rounded text-sm flex-1 max-w-xs text-white"
              disabled={isConnected}
            />
            <button
              onClick={connectWebSocket}
              disabled={isConnected}
              className="px-4 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm"
            >
              {isConnected ? 'Connected' : 'Connect'}
            </button>
          </div>

          <div className="flex items-center gap-3 mb-3">
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-400">Agents:</label>
              <input
                type="number"
                value={numAgents}
                onChange={(e) => setNumAgents(Math.max(1, Math.min(500, parseInt(e.target.value) || 100)))}
                min="1"
                max="500"
                className="px-3 py-1 bg-gray-700 rounded text-sm w-20 text-white"
                disabled={simulationRunning}
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-400">Rounds:</label>
              <input
                type="number"
                value={numRounds}
                onChange={(e) => setNumRounds(Math.max(1, Math.min(200, parseInt(e.target.value) || 50)))}
                min="1"
                max="200"
                className="px-3 py-1 bg-gray-700 rounded text-sm w-20 text-white"
                disabled={simulationRunning}
              />
            </div>
          </div>

          {connectionError && (
            <div className="bg-red-900 border border-red-700 text-red-200 px-3 py-2 rounded mb-3 text-sm">
              {connectionError}
            </div>
          )}
          
          <div className="flex items-center gap-3 flex-wrap mb-3">
            <div className={`px-3 py-1 rounded text-sm ${isConnected ? 'bg-green-600' : 'bg-red-600'}`}>
              {isConnected ? '● Connected' : '○ Disconnected'}
            </div>
            <button
              onClick={startSimulation}
              disabled={!isConnected || simulationRunning}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded"
            >
              Start
            </button>
            <button
              onClick={pauseSimulation}
              disabled={!simulationRunning}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded"
            >
              Pause
            </button>
            <button
              onClick={resetSimulation}
              disabled={!isConnected}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded"
            >
              Reset
            </button>
            <button
              onClick={() => setAutoRotate(!autoRotate)}
              className={`px-4 py-2 rounded ${autoRotate ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'}`}
            >
              {autoRotate ? '🔄 Auto Rotate' : '✋ Manual'}
            </button>
          </div>

          {/* View Tabs */}
          <div className="mb-3">
            <div className="text-sm text-gray-400 mb-2">Research Questions:</div>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
              {Object.entries(viewConfigs).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() => setActiveView(key)}
                  className={`px-3 py-2 rounded text-sm transition-colors text-left ${
                    activeView === key 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <div className="font-semibold">{config.name}</div>
                  <div className="text-xs opacity-75 mt-1">{config.question}</div>
                </button>
              ))}
            </div>
            <div className="mt-2 text-xs text-gray-400 italic">
              {viewConfigs[activeView].description}
            </div>
          </div>

          {/* Layout Mode */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Layout:</span>
            <button
              onClick={() => setVisualMode('spiral')}
              className={`px-3 py-1 rounded text-sm ${visualMode === 'spiral' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            >
              Spiral
            </button>
            <button
              onClick={() => setVisualMode('scatter')}
              className={`px-3 py-1 rounded text-sm ${visualMode === 'scatter' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            >
              Scatter
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden relative">
        {webglError ? (
          <div className="flex-1 flex items-center justify-center bg-gray-900">
            <div className="max-w-md p-6 bg-red-900 border border-red-700 rounded-lg">
              <h2 className="text-xl font-bold mb-3 text-red-200">WebGL Not Supported</h2>
              <p className="text-red-100 mb-4">
                Your browser doesn't support WebGL, which is required for 3D visualization.
              </p>
              <div className="space-y-2 text-sm text-red-200">
                <p><strong>Try:</strong></p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Use Chrome, Firefox, or Edge</li>
                  <li>Update graphics drivers</li>
                  <li>Enable hardware acceleration</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div 
            ref={mountRef} 
            className="flex-1" 
            style={{ minHeight: 0, cursor: 'grab' }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          />
        )}
        
        {/* Fullscreen toggle button - always visible */}
        {!webglError && (
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="absolute top-4 right-4 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded shadow-lg z-10 border border-gray-600"
            title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
          >
            {isFullscreen ? '🗗 Exit Fullscreen' : '🗖 Fullscreen'}
          </button>
        )}

        <Sidebar 
          stats={stats}
          selectedAgent={selectedAgent}
          setSelectedAgent={setSelectedAgent}
          isConnected={isConnected}
          viewConfigs={viewConfigs}
          activeView={activeView}
        />
      </div>
    </div>
  );
};

export default SocialMobilityViz;