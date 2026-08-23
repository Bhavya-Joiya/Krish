import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// ─── Grass blade geometry ──────────────────────────────────────────────────
// A tapered plane with `segments` horizontal strips for smooth GPU bending.
function createBlade(segments = 5, width = 0.055, height = 1.0): THREE.BufferGeometry {
  const geo = new THREE.BufferGeometry();
  const positions: number[] = [];
  const uvs: number[] = [];
  const indices: number[] = [];

  for (let i = 0; i <= segments; i++) {
    const t  = i / segments;
    const y  = t * height;
    const w  = width * (1.0 - t * 0.78);  // taper toward tip
    const lx = t * t * 0.055;              // natural forward lean

    positions.push(lx - w / 2, y, 0);
    positions.push(lx + w / 2, y, 0);
    uvs.push(0, t, 1, t);

    if (i < segments) {
      const b = i * 2;
      indices.push(b, b + 1, b + 2, b + 1, b + 3, b + 2);
    }
  }

  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('uv',       new THREE.Float32BufferAttribute(uvs,       2));
  geo.setIndex(indices);
  return geo;
}

// ─── Vertex shader ─────────────────────────────────────────────────────────
const vertexShader = /* glsl */`
precision highp float;

/* Geometry */
attribute vec3  position;
attribute vec2  uv;

/* Per-instance (InstancedBufferAttribute) */
attribute vec3  aOffset;       /* world XYZ of blade root          */
attribute float aRotation;     /* Y-axis spin (blade facing dir)   */
attribute float aScale;        /* height variation                 */
attribute float aWindOffset;   /* per-blade wind phase (0-1)       */

/* Three.js built-in matrices */
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;

/* Custom uniforms */
uniform float uTime;
uniform float uWindStrength;
uniform float uScrollProgress;

varying vec2  vUv;
varying float vFogDepth;
varying float vHeight;
varying float vDepthFactor;  /* 0 = far back, 1 = close to camera */

void main() {
  vUv    = uv;
  vHeight = uv.y;

  vec3 pos = position;

  /* ── Height scale ─────────────────────────────────────── */
  pos.y *= aScale;

  /* ── Wind (quadratic from base so roots are planted) ───────── */
  float phase  = aWindOffset * 6.28318;
  float h      = uv.y * uv.y;                         /* 0 at root → 1 at tip */

  /* Primary sway */
  float wx = sin(uTime * 1.15 + phase) * uWindStrength * h;
  float wz = cos(uTime * 0.72 + phase + 1.047) * uWindStrength * 0.45 * h;

  /* Secondary high-freq micro-rustle */
  float turb = sin(uTime * 3.9  + phase * 2.0) * uWindStrength * 0.10 * h;

  /* Gust wave traveling across the field (scroll-linked intensity) */
  float gust = sin(uTime * 0.6 + aOffset.x * 0.25) * uScrollProgress * 0.3 * h;

  pos.x += wx + turb + gust;
  pos.z += wz;

  /* ── Y-axis rotation (blade facing direction variety) ────── */
  float cr = cos(aRotation);
  float sr = sin(aRotation);
  float rx = pos.x * cr - pos.z * sr;
  float rz = pos.x * sr + pos.z * cr;
  pos.x = rx;
  pos.z = rz;

  /* ── World placement ──────────────────────────────── */
  pos += aOffset;

  /* Scroll: gently push the camera forward into the field */
  pos.z += uScrollProgress * -3.0;

  /* Depth factor: grass close to camera (z ~ 9) gets factor ~1.0,
     grass far away (z ~ -12) gets factor ~0.0                      */
  vDepthFactor = clamp((aOffset.z + 12.0) / 21.0, 0.0, 1.0);

  vec4 mvPos  = modelViewMatrix * vec4(pos, 1.0);
  vFogDepth   = -mvPos.z;
  gl_Position = projectionMatrix * mvPos;
}
`;

// ─── Fragment shader ───────────────────────────────────────────────────────
const fragmentShader = /* glsl */`
precision highp float;

uniform vec3  uBaseColor;   /* very dark forest root             */
uniform vec3  uMidColor;    /* mid forest green                  */
uniform vec3  uTipColor;    /* lighter emerald tip               */
uniform vec3  uFogColor;
uniform float uFogDensity;
uniform float uTime;

varying vec2  vUv;
varying float vFogDepth;
varying float vHeight;
varying float vDepthFactor;  /* 0 = far, 1 = near                */

void main() {
  float h = vUv.y;

  /* 3-stop gradient: base → mid → tip */
  vec3 col;
  if (h < 0.45) {
    col = mix(uBaseColor, uMidColor, h / 0.45);
  } else {
    col = mix(uMidColor, uTipColor, (h - 0.45) / 0.55);
  }

  /* Ambient occlusion at base (shadows inside dense grass) */
  float ao = smoothstep(0.0, 0.20, h) * 0.60 + 0.40;
  col *= ao;

  /* ── DEPTH-BASED BRIGHTNESS ────────────────────────────────
     Foreground grass is noticeably brighter than background.
     darkFar=0.38 means far blades are 38% brightness.
     brightNear=1.55 gives near blades a subtle luminous pop.     */
  float darkFar    = 0.36;
  float brightNear = 1.55;
  float depthBrightness = mix(darkFar, brightNear, vDepthFactor);
  col *= depthBrightness;

  /* Subtle shimmer / light-catch at tips — like backlit leaf edges */
  float shimmer = sin(uTime * 1.6 + vUv.y * 9.0) * 0.045 + 1.0;
  col *= mix(1.0, shimmer, pow(h, 2.0));

  /* Exponential depth fog — matches scene.fogExp2 */
  float fogFactor = 1.0 - exp(-uFogDensity * vFogDepth * 0.038);
  col = mix(col, uFogColor, clamp(fogFactor, 0.0, 0.92));

  /* Soft alpha fade at very tip (thin, wispy edge) */
  float alpha = 1.0 - pow(h, 7.0) * 0.45;

  gl_FragColor = vec4(col, alpha);
}
`;

// ─── Component ─────────────────────────────────────────────────────────────
export const GrassScene: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const prefersReduced =
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isMobile = window.innerWidth < 768;

    // ── Renderer ──────────────────────────────────────────────────────
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: !isMobile,
      alpha: false,
      powerPreference: 'high-performance',
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    // ── Scene ─────────────────────────────────────────────────────────
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x070D07);
    scene.fog = new THREE.FogExp2(0x0A0E0A, 0.030);

    // ── Camera ────────────────────────────────────────────────────────
    const camera = new THREE.PerspectiveCamera(
      58,
      window.innerWidth / window.innerHeight,
      0.1,
      120,
    );
    camera.position.set(0, 3.0, 9.5);
    camera.lookAt(0, 0.3, 0);

    // ── Lighting ──────────────────────────────────────────────────────
    // Ambient — dark forest-green tint, keeps scene from being pure black
    scene.add(new THREE.AmbientLight(0x0D2010, 3.5));

    // Moonlight — cool silver from upper left, primary light source
    const moon = new THREE.DirectionalLight(0xC5EDD0, 1.1);
    moon.position.set(-5, 12, 4);
    scene.add(moon);

    // Warm horizon backlight (amber) — hits grass tips from behind
    const horizon = new THREE.DirectionalLight(0xF5B94D, 0.55);
    horizon.position.set(1.5, 0.8, 14);
    scene.add(horizon);

    // Hemisphere — deep sky-teal top / near-black ground bottom
    scene.add(new THREE.HemisphereLight(0x0E3020, 0x040905, 1.2));

    // ── Ground plane ──────────────────────────────────────────────────
    const groundGeo = new THREE.PlaneGeometry(90, 60);
    const groundMat = new THREE.MeshLambertMaterial({ color: 0x040C05 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.05;
    scene.add(ground);

    // ── Sky backdrop ──────────────────────────────────────────────────
    // A large quad far behind — gives the impression of a deep sky gradient.
    const skyColors = [
      new THREE.Color(0x060D07),
      new THREE.Color(0x0A1A0C),
      new THREE.Color(0x122016),
    ];
    const skyGeo = new THREE.PlaneGeometry(200, 100, 1, 2);
    const skyColorArr: number[] = [];
    const skyVerts = skyGeo.attributes.position.count;
    for (let i = 0; i < skyVerts; i++) {
      const t = (skyGeo.attributes.position.getY(i) + 50) / 100;
      const c = new THREE.Color().lerpColors(skyColors[0], skyColors[2], t);
      skyColorArr.push(c.r, c.g, c.b);
    }
    skyGeo.setAttribute('color', new THREE.Float32BufferAttribute(skyColorArr, 3));
    const skyMat = new THREE.MeshBasicMaterial({ vertexColors: true });
    const sky = new THREE.Mesh(skyGeo, skyMat);
    sky.position.set(0, 12, -48);
    scene.add(sky);

    // ── Horizon amber glow sprite ─────────────────────────────────────
    const glowGeo = new THREE.PlaneGeometry(80, 20);
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0xF5B94D,
      transparent: true,
      opacity: 0.06,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const glow = new THREE.Mesh(glowGeo, glowMat);
    glow.position.set(0, -2, -40);
    scene.add(glow);

    // ── Grass ─────────────────────────────────────────────────────────
    const COUNT = isMobile ? 9_000 : 30_000;

    const uniforms = {
      uTime:           { value: 0.0 },
      uWindStrength:   { value: 0.28 },
      uScrollProgress: { value: 0.0 },
      // Base: dark root shadow
      uBaseColor:      { value: new THREE.Color(0x040A05) },
      // Mid: visible mid-green
      uMidColor:       { value: new THREE.Color(0x0E2E12) },
      // Tip: vibrant emerald — clearly differentiated from background
      uTipColor:       { value: new THREE.Color(0x28A84A) },
      uFogColor:       { value: new THREE.Color(0x080C08) },
      uFogDensity:     { value: 0.038 },
    };

    const mat = new THREE.RawShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms,
      side:        THREE.DoubleSide,
      transparent: true,
    });

    // Build InstancedBufferGeometry from blade template
    const bladeBase   = createBlade(6, 0.055, 1.0);
    const instancedGeo = new THREE.InstancedBufferGeometry();
    instancedGeo.index             = bladeBase.index;
    instancedGeo.attributes.position = bladeBase.attributes.position;
    instancedGeo.attributes.uv       = bladeBase.attributes.uv;
    instancedGeo.instanceCount        = COUNT;

    const offsets     = new Float32Array(COUNT * 3);
    const rotations   = new Float32Array(COUNT);
    const scales      = new Float32Array(COUNT);
    const windOffsets = new Float32Array(COUNT);

    for (let i = 0; i < COUNT; i++) {
      // Rectangular field distribution with slight density falloff at edges
      let x: number, z: number;
      // Slightly cluster toward center
      x = (Math.random() - 0.5) * 44;
      z = (Math.random() - 0.5) * 22;
      // Thin out very far edges
      if (Math.abs(x) > 18 && Math.random() < 0.4) { x *= 0.6; }
      if (Math.abs(z) > 8  && Math.random() < 0.4) { z *= 0.6; }

      offsets[i * 3]     = x;
      offsets[i * 3 + 1] = 0;
      offsets[i * 3 + 2] = z;

      rotations[i]   = Math.random() * Math.PI * 2;
      scales[i]      = 0.5 + Math.random() * 1.0;
      windOffsets[i] = Math.random();
    }

    instancedGeo.setAttribute('aOffset',
      new THREE.InstancedBufferAttribute(offsets,     3));
    instancedGeo.setAttribute('aRotation',
      new THREE.InstancedBufferAttribute(rotations,   1));
    instancedGeo.setAttribute('aScale',
      new THREE.InstancedBufferAttribute(scales,      1));
    instancedGeo.setAttribute('aWindOffset',
      new THREE.InstancedBufferAttribute(windOffsets, 1));

    const grassMesh = new THREE.Mesh(instancedGeo, mat);
    scene.add(grassMesh);

    // ── Firefly particles ─────────────────────────────────────────────
    const FF = isMobile ? 30 : 80;
    const ffPos = new Float32Array(FF * 3);
    const ffVel = new Float32Array(FF * 3);

    for (let i = 0; i < FF; i++) {
      ffPos[i*3]     = (Math.random() - 0.5) * 30;
      ffPos[i*3 + 1] = 0.4 + Math.random() * 3.2;
      ffPos[i*3 + 2] = (Math.random() - 0.5) * 12;
      ffVel[i*3]     = (Math.random() - 0.5) * 0.003;
      ffVel[i*3 + 1] = 0.0008 + Math.random() * 0.0025;
      ffVel[i*3 + 2] = (Math.random() - 0.5) * 0.002;
    }

    const ffGeo = new THREE.BufferGeometry();
    ffGeo.setAttribute('position', new THREE.BufferAttribute(ffPos, 3));

    const ffMat = new THREE.PointsMaterial({
      color:       0xF5B94D,
      size:        isMobile ? 0.055 : 0.075,
      transparent: true,
      opacity:     0.70,
      blending:    THREE.AdditiveBlending,
      depthWrite:  false,
    });

    const fireflies = new THREE.Points(ffGeo, ffMat);
    scene.add(fireflies);

    // ── Stars (static Points far back) ────────────────────────────────
    const starCount = 200;
    const starPos   = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      starPos[i*3]     = (Math.random() - 0.5) * 120;
      starPos[i*3 + 1] = 5 + Math.random() * 35;
      starPos[i*3 + 2] = -20 - Math.random() * 55;
    }
    const starGeo = new THREE.BufferGeometry();
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({
      color:       0xC8EED8,
      size:        0.12,
      transparent: true,
      opacity:     0.45,
      blending:    THREE.AdditiveBlending,
      depthWrite:  false,
    });
    scene.add(new THREE.Points(starGeo, starMat));

    // ── GSAP ScrollTrigger ────────────────────────────────────────────
    let st: ScrollTrigger | null = null;
    if (!prefersReduced) {
      st = ScrollTrigger.create({
        trigger: document.documentElement,
        start:   'top top',
        end:     'bottom bottom',
        scrub:   1.5,
        onUpdate: (self) => {
          const p = self.progress;

          // Wind grows with scroll — creates "gust as you scroll" feeling
          gsap.to(uniforms.uWindStrength, {
            value: 0.25 + p * 0.60,
            duration: 0.7,
            overwrite: true,
          });

          gsap.to(uniforms.uScrollProgress, {
            value: p,
            duration: 0.35,
            overwrite: true,
          });

          // Camera drifts slightly right + lowers + pushes forward
          gsap.to(camera.position, {
            x:        p * 2.2,
            y:        3.0 - p * 0.65,
            z:        9.5 + p * 1.2,
            duration: 1.1,
            overwrite: true,
            onUpdate: () => camera.lookAt(p * 1.1, 0.3 - p * 0.15, 0),
          });

          // Horizon amber glow intensifies mid-scroll
          glowMat.opacity = 0.06 + Math.sin(p * Math.PI) * 0.08;
        },
      });
    }

    // ── GSAP intro camera push-in (on first load) ─────────────────────
    if (!prefersReduced) {
      gsap.from(camera.position, {
        z:        16,
        y:        5.5,
        duration: 2.8,
        ease:     'power3.out',
        onUpdate: () => camera.lookAt(0, 0.3, 0),
      });
      gsap.from(uniforms.uWindStrength, {
        value:    0.0,
        duration: 2.0,
        ease:     'power2.out',
      });
    }

    // ── Render loop ───────────────────────────────────────────────────
    const clock = new THREE.Clock();
    let animId: number;

    const tick = () => {
      animId = requestAnimationFrame(tick);
      const t = clock.getElapsedTime();
      uniforms.uTime.value = t;

      if (!prefersReduced) {
        // Animate fireflies — slow drift + sine wobble
        const pos = ffGeo.attributes.position.array as Float32Array;
        for (let i = 0; i < FF; i++) {
          pos[i*3]     += ffVel[i*3]     + Math.sin(t * 0.4 + i * 0.85) * 0.0008;
          pos[i*3 + 1] += ffVel[i*3 + 1] + Math.sin(t * 0.3 + i * 1.20) * 0.0006;
          pos[i*3 + 2] += ffVel[i*3 + 2];
          // Wrap within bounds
          if (pos[i*3 + 1] > 4.2)         pos[i*3 + 1] = 0.3;
          if (Math.abs(pos[i*3])     > 16) pos[i*3]     *= -0.92;
          if (Math.abs(pos[i*3 + 2]) > 7)  pos[i*3 + 2] *= -0.92;
        }
        (ffGeo.attributes.position as THREE.BufferAttribute).needsUpdate = true;

        // Firefly opacity breathe
        ffMat.opacity = 0.50 + Math.sin(t * 1.1) * 0.22;
      }

      renderer.render(scene, camera);
    };
    tick();

    // ── Resize ────────────────────────────────────────────────────────
    const onResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', onResize);

    // ── Cleanup ───────────────────────────────────────────────────────
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
      st?.kill();
      renderer.dispose();
      mat.dispose();
      instancedGeo.dispose();
      bladeBase.dispose();
      groundGeo.dispose();
      groundMat.dispose();
      ffGeo.dispose();
      ffMat.dispose();
      skyGeo.dispose();
      skyMat.dispose();
      glowGeo.dispose();
      glowMat.dispose();
      starGeo.dispose();
      starMat.dispose();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 w-full h-full pointer-events-none"
      aria-hidden="true"
    />
  );
};
