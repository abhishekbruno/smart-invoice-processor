import { useEffect, useRef } from 'react';
import { createFrameLoop } from '../lib/frameLoop';
import { useEffects } from './EffectsProvider';

interface Props {
  onPhaseChange?: (phase: 1 | 2 | 3 | 4 | 5) => void;
  onComplete?: () => void;
  className?: string;
}

interface Particle3D {
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  vz: number;
  size: number;
  alpha: number;
  baseAlpha: number;
  color: string;
  decay: number;
  trail: boolean;
}

interface InwardParticle {
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  speed: number;
  size: number;
  alpha: number;
  color: string;
}

interface ShockwaveRing {
  radius: number;
  maxRadius: number;
  speed: number;
  alpha: number;
  width: number;
  color: string;
}

interface NebulaPuff {
  x: number;
  y: number;
  radius: number;
  maxRadius: number;
  growth: number;
  alpha: number;
  color: string;
}

/**
 * BigBangCanvas — Cinematic Cosmic Genesis
 *
 * Implements the 5-phase Big Bang sequence:
 * Phase 1: The Void (0–250ms) — Deep black abyss, faint distant stars, singularity light spark.
 * Phase 2: Energy Compression (250–550ms) — Gravitational attraction of particles inward, energy rings contracting.
 * Phase 3: The Big Bang (550–950ms) — Luminous violet burst, 3D expanding particles, expanding shockwaves and dust.
 * Phase 4: Universe Formation (950–1350ms) — Physics damping, particles settling into stars/dust, sphere unveiling.
 * Phase 5: Dashboard Reveal (1350ms+) — Overlay fadeout smoothly into persistent cosmic space.
 */
export function BigBangCanvas({ onPhaseChange, onComplete, className = '' }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { reduced, mode } = useEffects();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    if (reduced) {
      onPhaseChange?.(5);
      onComplete?.();
      return;
    }

    let width = 0;
    let height = 0;
    let dpr = 1;
    let elapsed = 0;
    let currentPhase: 1 | 2 | 3 | 4 | 5 = 1;

    // Simulation entity pools
    const distantStars: Array<{ x: number; y: number; r: number; alpha: number; twinkle: number }> = [];
    const inwardParticles: InwardParticle[] = [];
    const explodeParticles: Particle3D[] = [];
    const shockwaves: ShockwaveRing[] = [];
    const nebulaPuffs: NebulaPuff[] = [];

    let hasDetonated = false;
    let hasSettled = false;

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;

      // Generate faint static void stars
      if (distantStars.length === 0) {
        const starCount = mode === 'full' ? 55 : 35;
        for (let i = 0; i < starCount; i++) {
          distantStars.push({
            x: Math.random() * width,
            y: Math.random() * height,
            r: Math.random() * 1.2 + 0.5,
            alpha: Math.random() * 0.25 + 0.08,
            twinkle: Math.random() * Math.PI * 2,
          });
        }
      }
    };

    resize();
    window.addEventListener('resize', resize);

    const triggerDetonation = (cx: number, cy: number) => {
      if (hasDetonated) return;
      hasDetonated = true;

      // 1. Shockwave rings expanding outward
      const ringCount = mode === 'full' ? 4 : 3;
      for (let i = 0; i < ringCount; i++) {
        shockwaves.push({
          radius: 12 + i * 8,
          maxRadius: Math.max(width, height) * (0.8 + i * 0.2),
          speed: 680 + i * 160,
          alpha: 0.85 - i * 0.15,
          width: 3.5 - i * 0.5,
          color: i % 2 === 0 ? '187, 168, 241' : '196, 181, 253',
        });
      }

      // 2. Exploding 3D particles with perspective depth
      const count = mode === 'full' ? 240 : 160;
      const palette = [
        '#FFFFFF',
        '#F3E8FF',
        '#E9D5FF',
        '#C4B5FD',
        '#A78BFA',
        '#8B5CF6',
        '#6D28D9',
        '#DDD6FE',
      ];

      for (let i = 0; i < count; i++) {
        const theta = Math.random() * Math.PI * 2;
        const phi = (Math.random() - 0.5) * Math.PI * 0.8;
        const speed = 240 + Math.random() * 620;

        explodeParticles.push({
          x: cx,
          y: cy,
          z: (Math.random() - 0.5) * 80,
          vx: Math.cos(theta) * Math.cos(phi) * speed,
          vy: Math.sin(theta) * Math.cos(phi) * speed,
          vz: Math.sin(phi) * speed * 0.7,
          size: Math.random() * 2.2 + 0.8,
          alpha: 1.0,
          baseAlpha: Math.random() * 0.4 + 0.6,
          color: palette[Math.floor(Math.random() * palette.length)],
          decay: 0.55 + Math.random() * 0.4,
          trail: Math.random() > 0.45,
        });
      }

      // 3. Volumetric cosmic dust / nebula puffs
      const puffCount = mode === 'full' ? 14 : 9;
      for (let i = 0; i < puffCount; i++) {
        const angle = Math.random() * Math.PI * 2;
        const dist = Math.random() * 45;
        nebulaPuffs.push({
          x: cx + Math.cos(angle) * dist,
          y: cy + Math.sin(angle) * dist,
          radius: 15 + Math.random() * 20,
          maxRadius: 220 + Math.random() * 260,
          growth: 180 + Math.random() * 140,
          alpha: 0.35,
          color: i % 3 === 0 ? '109, 40, 217' : i % 3 === 1 ? '76, 29, 149' : '139, 92, 246',
        });
      }
    };

    // Main animation draw loop
    const draw = (dt: number) => {
      elapsed += dt;
      const cx = width / 2;
      const cy = height / 2;

      // Determine phase according to precision timings:
      // Phase 1 (0 - 0.25s): The Void
      // Phase 2 (0.25 - 0.55s): Energy Compression
      // Phase 3 (0.55 - 0.95s): The Big Bang
      // Phase 4 (0.95 - 1.35s): Universe Formation
      // Phase 5 (1.35s+): Dashboard Reveal
      let nextPhase: 1 | 2 | 3 | 4 | 5 = 1;
      if (elapsed >= 1.35) nextPhase = 5;
      else if (elapsed >= 0.95) nextPhase = 4;
      else if (elapsed >= 0.55) nextPhase = 3;
      else if (elapsed >= 0.25) nextPhase = 2;

      if (nextPhase !== currentPhase) {
        currentPhase = nextPhase;
        onPhaseChange?.(currentPhase);
      }

      // Clear with absolute deep black space
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);

      // Draw faint distant void stars
      ctx.fillStyle = '#FFFFFF';
      for (let i = 0; i < distantStars.length; i++) {
        const star = distantStars[i];
        star.twinkle += dt * 2.5;
        const a = star.alpha * (0.7 + Math.sin(star.twinkle) * 0.3);
        ctx.globalAlpha = a;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
        ctx.fill();
      }

      // -------------------------------------------------------------
      // PHASE 1 & 2: THE SINGULARITY & ENERGY COMPRESSION
      // -------------------------------------------------------------
      if (elapsed < 0.55) {
        const p1Progress = Math.min(1, elapsed / 0.25);
        const p2Progress = Math.max(0, Math.min(1, (elapsed - 0.25) / 0.30));

        // Spawn inward rushing particles during Phase 2
        if (currentPhase === 2 && Math.random() < 0.65) {
          const spawnAngle = Math.random() * Math.PI * 2;
          const spawnDist = 130 + Math.random() * 150;
          inwardParticles.push({
            x: cx + Math.cos(spawnAngle) * spawnDist,
            y: cy + Math.sin(spawnAngle) * spawnDist,
            targetX: cx,
            targetY: cy,
            speed: 360 + Math.random() * 320,
            size: Math.random() * 1.8 + 0.8,
            alpha: 0.85,
            color: Math.random() > 0.5 ? '#BBA8F1' : '#FFFFFF',
          });
        }

        // Render inward rushing particles
        for (let i = inwardParticles.length - 1; i >= 0; i--) {
          const p = inwardParticles[i];
          const dx = p.targetX - p.x;
          const dy = p.targetY - p.y;
          const dist = Math.hypot(dx, dy);

          if (dist < 8) {
            inwardParticles.splice(i, 1);
            continue;
          }

          const move = (p.speed * dt * (1 + (1 - dist / 250) * 2));
          p.x += (dx / dist) * Math.min(dist, move);
          p.y += (dy / dist) * Math.min(dist, move);

          ctx.globalAlpha = p.alpha;
          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
        }

        // Contracting magnetic energy rings around singularity
        if (currentPhase === 2) {
          const ringRadius = 55 * (1 - p2Progress * 0.85);
          ctx.save();
          ctx.translate(cx, cy);
          ctx.rotate(elapsed * 4);
          ctx.strokeStyle = 'rgba(187, 168, 241, ' + (0.35 + p2Progress * 0.45) + ')';
          ctx.lineWidth = 1.2;
          ctx.beginPath();
          ctx.ellipse(0, 0, ringRadius, ringRadius * 0.45, Math.PI / 4, 0, Math.PI * 2);
          ctx.stroke();

          ctx.strokeStyle = 'rgba(196, 181, 253, ' + (0.3 + p2Progress * 0.4) + ')';
          ctx.beginPath();
          ctx.ellipse(0, 0, ringRadius * 1.3, ringRadius * 0.6, -Math.PI / 3, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }

        // Singularity core
        const coreIntensity = p1Progress * 0.5 + p2Progress * 0.5;
        const coreRadius = 2 + coreIntensity * 4.5 + Math.sin(elapsed * 25) * 0.8;

        // Outer violet magnetic halo
        const haloGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreRadius * 8);
        haloGrad.addColorStop(0, 'rgba(196, 181, 253, ' + (0.5 * coreIntensity) + ')');
        haloGrad.addColorStop(0.35, 'rgba(124, 58, 237, ' + (0.25 * coreIntensity) + ')');
        haloGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = haloGrad;
        ctx.beginPath();
        ctx.arc(cx, cy, coreRadius * 8, 0, Math.PI * 2);
        ctx.fill();

        // Singularity bright white core
        ctx.globalAlpha = Math.min(1, 0.4 + coreIntensity * 0.6);
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(cx, cy, coreRadius, 0, Math.PI * 2);
        ctx.fill();
      }

      // -------------------------------------------------------------
      // PHASE 3 & 4: THE BIG BANG DETONATION & UNIVERSE FORMATION
      // -------------------------------------------------------------
      if (elapsed >= 0.55) {
        if (!hasDetonated) {
          triggerDetonation(cx, cy);
        }

        // A. Draw expanding nebula dust clouds
        for (let i = 0; i < nebulaPuffs.length; i++) {
          const puff = nebulaPuffs[i];
          if (puff.radius < puff.maxRadius) {
            puff.radius += puff.growth * dt;
          }
          puff.alpha = Math.max(0, puff.alpha - dt * 0.18);

          if (puff.alpha > 0.01) {
            const grad = ctx.createRadialGradient(puff.x, puff.y, 0, puff.x, puff.y, puff.radius);
            grad.addColorStop(0, `rgba(${puff.color}, ${puff.alpha})`);
            grad.addColorStop(0.5, `rgba(${puff.color}, ${puff.alpha * 0.4})`);
            grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(puff.x, puff.y, puff.radius, 0, Math.PI * 2);
            ctx.fill();
          }
        }

        // B. Draw expanding lavender shockwave rings
        for (let i = 0; i < shockwaves.length; i++) {
          const ring = shockwaves[i];
          ring.radius += ring.speed * dt;
          ring.alpha = Math.max(0, ring.alpha - dt * 1.15);

          if (ring.alpha > 0.01 && ring.radius < ring.maxRadius) {
            ctx.strokeStyle = `rgba(${ring.color}, ${ring.alpha})`;
            ctx.lineWidth = ring.width;
            ctx.beginPath();
            ctx.arc(cx, cy, ring.radius, 0, Math.PI * 2);
            ctx.stroke();
          }
        }

        // C. Update and render 3D perspective expanding particles
        const focalLength = 340;
        const drag = Math.pow(0.35, dt); // Smooth deceleration into universe formation

        for (let i = 0; i < explodeParticles.length; i++) {
          const p = explodeParticles[i];

          // Apply physics
          p.x += p.vx * dt;
          p.y += p.vy * dt;
          p.z += p.vz * dt;

          p.vx *= drag;
          p.vy *= drag;
          p.vz *= drag;

          // Compute perspective projection
          const depth = focalLength + p.z;
          const perspective = depth > 10 ? focalLength / depth : 1;
          const projX = cx + (p.x - cx) * perspective;
          const projY = cy + (p.y - cy) * perspective;
          const projSize = Math.max(0.6, p.size * perspective);

          // Alpha decay: in Phase 4, some particles remain as ambient cosmic dust
          if (elapsed > 0.95 && !hasSettled) {
            p.alpha = Math.max(p.baseAlpha * 0.4, p.alpha - dt * p.decay * 0.4);
          } else {
            p.alpha = Math.max(0.15, p.alpha - dt * p.decay * 0.2);
          }

          if (projX >= -20 && projX <= width + 20 && projY >= -20 && projY <= height + 20) {
            ctx.globalAlpha = p.alpha;
            ctx.fillStyle = p.color;

            // Short trailing streak for high speed particles
            if (p.trail && Math.hypot(p.vx, p.vy) > 120) {
              ctx.lineWidth = projSize;
              ctx.strokeStyle = p.color;
              ctx.beginPath();
              ctx.moveTo(projX, projY);
              ctx.lineTo(projX - p.vx * dt * 0.15, projY - p.vy * dt * 0.15);
              ctx.stroke();
            } else {
              ctx.beginPath();
              ctx.arc(projX, projY, projSize, 0, Math.PI * 2);
              ctx.fill();
            }
          }
        }
      }

      // Check for completion
      if (elapsed >= 1.6 && !hasSettled) {
        hasSettled = true;
        onComplete?.();
      }
    };

    const loop = createFrameLoop(draw, {
      request: (cb) => window.requestAnimationFrame(cb),
      cancel: (id) => window.cancelAnimationFrame(id),
    });

    loop.start();

    return () => {
      loop.dispose();
      window.removeEventListener('resize', resize);
      distantStars.length = 0;
      inwardParticles.length = 0;
      explodeParticles.length = 0;
      shockwaves.length = 0;
      nebulaPuffs.length = 0;
    };
  }, [reduced, mode, onPhaseChange, onComplete]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 pointer-events-none z-10 ${className}`}
      aria-hidden="true"
    />
  );
}

