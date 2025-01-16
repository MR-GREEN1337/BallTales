import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { Vector3 } from 'three';

const BaseballBat = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      powerPreference: "high-performance"
    });
    
    renderer.setSize(200, 200);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);

    // Create bat geometry
    const createBat = () => {
      const batGroup = new THREE.Group();
      
      // Barrel (main part)
      const barrelGeometry = new THREE.CylinderGeometry(0.15, 0.12, 2, 32, 32);
      const barrelMaterial = new THREE.MeshPhysicalMaterial({
        color: 0x8B4513,
        roughness: 0.3,
        metalness: 0.1,
        clearcoat: 0.3,
        clearcoatRoughness: 0.2
      });
      const barrel = new THREE.Mesh(barrelGeometry, barrelMaterial);
      
      // Handle
      const handleGeometry = new THREE.CylinderGeometry(0.08, 0.12, 0.8, 32, 32);
      const handleMaterial = new THREE.MeshPhysicalMaterial({
        color: 0x8B4513,
        roughness: 0.2,
        metalness: 0.1,
        clearcoat: 0.4,
        clearcoatRoughness: 0.1
      });
      const handle = new THREE.Mesh(handleGeometry, handleMaterial);
      
      // Knob at the end
      const knobGeometry = new THREE.SphereGeometry(0.12, 32, 32);
      const knobMaterial = new THREE.MeshPhysicalMaterial({
        color: 0x8B4513,
        roughness: 0.2,
        metalness: 0.15,
        clearcoat: 0.5,
        clearcoatRoughness: 0.1
      });
      const knob = new THREE.Mesh(knobGeometry, knobMaterial);
      
      // Position the parts
      barrel.position.y = 1.4;
      handle.position.y = 0.4;
      knob.position.y = 0;
      
      // Add wood grain effect
      const woodTexture = new THREE.TextureLoader().load('/wood-texture.jpg');
      [barrel.material, handle.material, knob.material].forEach(material => {
        if (material instanceof THREE.MeshPhysicalMaterial) {
          material.normalMap = woodTexture;
          material.normalScale.set(0.5, 0.5);
        }
      });
      
      // Combine all parts
      batGroup.add(barrel);
      batGroup.add(handle);
      batGroup.add(knob);
      
      // Add subtle imperfections
      batGroup.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          child.geometry.vertices?.forEach((vertex: { x: number; y: number; z: number; }) => {
            vertex.x += (Math.random() - 0.5) * 0.005;
            vertex.y += (Math.random() - 0.5) * 0.005;
            vertex.z += (Math.random() - 0.5) * 0.005;
          });
          if (child.geometry.vertices) child.geometry.verticesNeedUpdate = true;
        }
      });
      
      return batGroup;
    };

    const bat = createBat();
    scene.add(bat);

    // Lighting setup
    const createLights = () => {
      // Key light
      const keyLight = new THREE.SpotLight(0xffffff, 1);
      keyLight.position.set(5, 5, 5);
      keyLight.angle = Math.PI / 4;
      keyLight.penumbra = 0.5;
      keyLight.castShadow = true;
      scene.add(keyLight);

      // Fill light
      const fillLight = new THREE.SpotLight(0x8888ff, 0.5);
      fillLight.position.set(-5, 0, 5);
      fillLight.angle = Math.PI / 4;
      fillLight.penumbra = 0.5;
      scene.add(fillLight);

      // Rim light
      const rimLight = new THREE.SpotLight(0xffffaa, 0.8);
      rimLight.position.set(0, 5, -5);
      rimLight.angle = Math.PI / 4;
      rimLight.penumbra = 0.5;
      scene.add(rimLight);

      // Ambient light
      const ambient = new THREE.AmbientLight(0xffffff, 0.2);
      scene.add(ambient);
    };

    createLights();

    // Camera positioning
    camera.position.set(0, 0, 5);
    camera.lookAt(new Vector3(0, 0, 0));

    // Animation
    let frameId: number;
    const rotationAxis = new THREE.Vector3(1, 2, 1).normalize();
    let time = 0;

    const animate = () => {
      frameId = requestAnimationFrame(animate);
      time += 0.01;

      // Complex rotation animation
      bat.setRotationFromAxisAngle(rotationAxis, time);
      
      // Add subtle floating motion
      bat.position.y = Math.sin(time) * 0.1;
      
      // Dynamic camera movement
      camera.position.x = Math.sin(time * 0.5) * 1;
      camera.position.z = 5 + Math.cos(time * 0.5) * 1;
      camera.lookAt(new Vector3(0, 0, 0));

      renderer.render(scene, camera);
    };

    animate();

    // Handle cleanup
    return () => {
      cancelAnimationFrame(frameId);
      mountRef.current?.removeChild(renderer.domElement);
      
      // Clean up Three.js resources
      scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose();
          if (object.material instanceof THREE.Material) {
            object.material.dispose();
          }
        }
      });
      renderer.dispose();
    };
  }, []);

  return (
    <div 
      ref={mountRef} 
      className="w-48 h-48 relative"
      style={{
        perspective: '1000px',
        transformStyle: 'preserve-3d'
      }}
    />
  );
};

export default BaseballBat;