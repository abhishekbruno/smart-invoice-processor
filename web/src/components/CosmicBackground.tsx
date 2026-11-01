import React, { useEffect, useRef } from 'react';
import { useEffects } from './EffectsProvider';
import { createFrameLoop } from '../lib/frameLoop';

interface Particle {
  x: number;
  y: number;
  originX: number;
  originY: number;
  vx: number;
  vy: number;
  baseDriftX: number;
  baseDriftY: number;
  radius: number;
  baseAlpha: number;
  depth: number;
  layer: 0 | 1 | 2; // 0 = distant star, 1 = cosmic dust, 2 = energy particle
  twinkleSpeed: number;
  twinklePhase: number;
  color: string;
}

interface Spark {
  x: number;
  y: number;
  vx: number;
  vy: number;
  alpha: number;
  maxLife: number;
  life: number;
  size: number;
  color: string;
}

interface ShootingBeam {
  id: number;
  active: boolean;
  x: number;
  y: number;
  vx: number;
  vy: number;
  angle: number;
  speed: number;
  length: number;
  progress: number;
  duration: number;
  glowWidth: number;
  coreWidth: number;
  headGlowSize: number;
  colorTail: string;
  colorMid: string;
  colorHeadGlow: string;
  colorSpark: string;
  sparks: Spark[];
}

/**
 * CosmicBackground
 *
 * High-performance, GPU-accelerated interactive canvas background:
 * - Multi-layered celestial particle system (distant stars, cosmic dust, energy particles).
 * - Smooth cursor-reactive cosmic disturbance field with soft spring restitution.
 * - Subtle scroll parallax for authentic deep-space perspective.
 * - Rare occasional shooting cosmic beam with luminous core and natural fading tail.
 * - Pauses automatically when tab is hidden or element is offscreen.
 * - Zero allocations in animation frames for smooth 60 FPS scrolling.
 */
export const CosmicBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { mode, reduced } = useEffects();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let dpr = 1;
    let time = 0;
    let visible = true;

    // Cursor tracking
    let targetCursorX = -9999;
    let targetCursorY = -9999;
    let cursorX = -9999;
    let cursorY = -9999;
    let cursorActive = false;
    let lastCursorMove = 0;

    // Scroll parallax tracking
    let targetScrollY = window.scrollY;
    let currentScrollY = window.scrollY;

    // Particle pool
    const particleCount = reduced ? 40 : mode === 'full' ? 160 : 95;
    const particles: Particle[] = [];

    const initParticles = (w: number, h: number) => {
      particles.length = 0;
      for (let i = 0; i < particleCount; i++) {
        // Distribute layers: 50% distant stars, 35% cosmic dust, 15% energy sparks
        const layerRatio = i / particleCount;
        let layer: 0 | 1 | 2 = 0;
        let depth = 0.3;
        let radius = 0.75;
        let baseAlpha = 0.35;
        let color = '#E4D9FF';
        let driftSpeed = 3 + Math.random() * 4;

        if (layerRatio > 0.85) {
          // Luminous energy particles (layer 2)
          layer = 2;
          depth = 0.85 + Math.random() * 0.15;
          radius = 1.4 + Math.random() * 1.0;
          baseAlpha = 0.6 + Math.random() * 0.35;
          color = '#F5EDFF';
          driftSpeed = 7 + Math.random() * 8;
        } else if (layerRatio > 0.5) {
          // Soft drifting cosmic dust (layer 1)
          layer = 1;
          depth = 0.5 + Math.random() * 0.3;
          radius = 1.0 + Math.random() * 0.7;
          baseAlpha = 0.25 + Math.random() * 0.3;
          color = i % 2 === 0 ? '#BBA8F1' : '#C7D2FE';
          driftSpeed = 5 + Math.random() * 6;
        } else {
          // Faint distant stars (layer 0)
          layer = 0;
          depth = 0.2 + Math.random() * 0.25;
          radius = 0.55 + Math.random() * 0.4;
          baseAlpha = 0.18 + Math.random() * 0.3;
          color = i % 3 === 0 ? '#C4B5FD' : '#E0E7FF';
          driftSpeed = 2 + Math.random() * 3;
        }

        const px = Math.random() * w;
        const py = Math.random() * h;
        const driftAngle = Math.random() * Math.PI * 2;

        particles.push({
          x: px,
          y: py,
          originX: px,
          originY: py,
          vx: 0,
          vy: 0,
          baseDriftX: Math.cos(driftAngle) * driftSpeed,
          baseDriftY: Math.sin(driftAngle) * driftSpeed,
          radius,
          baseAlpha,
          depth,
          layer,
          twinkleSpeed: 0.8 + Math.random() * 1.6,
          twinklePhase: Math.random() * Math.PI * 2,
          color,
        });
      }
    };

    // Multi-Beam Shooting Cosmic Beams state & pool
    let nextBeamTimer = 2.2; // First beam glides in smoothly after initial entry
    let secondaryBeamTimer = 0; // Occasional complementary staggered beam
    let lastTrajectoryIndex = -1;

    const beamPool: ShootingBeam[] = Array.from({ length: 4 }, (_, i) => ({
      id: i,
      active: false,
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      angle: 0,
      speed: 0,
      length: 0,
      progress: 0,
      duration: 0,
      glowWidth: 4.8,
      coreWidth: 1.6,
      headGlowSize: 10,
      colorTail: 'rgba(99, 102, 241, 0.35)',
      colorMid: 'rgba(192, 132, 252, 0.75)',
      colorHeadGlow: 'rgba(216, 180, 254, 0.6)',
      colorSpark: 'rgba(216, 180, 254, ',
      sparks: [],
    }));

    // Trigger an individual shooting beam from the pre-allocated pool
    const triggerShootingBeam = () => {
      if (reduced || !width || !height) return;

      // Ensure no more than 2 beams are ever visible simultaneously
      const activeCount = beamPool.reduce((acc, b) => acc + (b.active ? 1 : 0), 0);
      if (activeCount >= 2) return;

      // Find first available inactive beam
      const beam = beamPool.find((b) => !b.active);
      if (!beam) return;

      // Select trajectory different from the immediate previous beam
      // 0: Top-Left to Bottom-Right (diagonal down-right)
      // 1: Bottom-Left to Top-Right (diagonal up-right)
      // 2: Top-Right to Bottom-Left (diagonal down-left)
      // 3: Bottom-Right to Top-Left (diagonal up-left)
      const possibleTrajectories = [0, 1, 2, 3].filter((t) => t !== lastTrajectoryIndex);
      const trajectory = possibleTrajectories[Math.floor(Math.random() * possibleTrajectories.length)];
      lastTrajectoryIndex = trajectory;

      let angle = 0;
      let startX = 0;
      let startY = 0;

      if (trajectory === 0) {
        // Top-Left to Bottom-Right
        angle = 0.58 + (Math.random() - 0.5) * 0.28; // ~25° to 41°
        startX = Math.random() * (width * 0.35) - 30;
        startY = -30 + Math.random() * (height * 0.3);
      } else if (trajectory === 1) {
        // Bottom-Left to Top-Right
        angle = -0.58 + (Math.random() - 0.5) * 0.28; // ~ -25° to -41°
        startX = Math.random() * (width * 0.35) - 30;
        startY = height * (0.7 + Math.random() * 0.3) + 20;
      } else if (trajectory === 2) {
        // Top-Right to Bottom-Left
        angle = 2.26 + (Math.random() - 0.5) * 0.28; // ~122° to 138°
        startX = width * (0.65 + Math.random() * 0.35) + 30;
        startY = -30 + Math.random() * (height * 0.3);
      } else {
        // Bottom-Right to Top-Left
        angle = -2.26 + (Math.random() - 0.5) * 0.28; // ~ -122° to -138°
        startX = width * (0.65 + Math.random() * 0.35) + 30;
        startY = height * (0.7 + Math.random() * 0.3) + 20;
      }

      // Beam archetype variation:
      // Type 0: Swift & compact energy dart
      // Type 1: Luminous celestial streamer with soft lingering stardust
      // Type 2: Deep cosmic ray with balanced amethyst glow
      const archetype = Math.floor(Math.random() * 3);

      if (archetype === 0) {
        // Short & fast
        beam.length = 150 + Math.random() * 50;
        beam.speed = 2500 + Math.random() * 600;
        beam.duration = 0.52 + Math.random() * 0.12;
        beam.glowWidth = 3.8;
        beam.coreWidth = 1.3;
        beam.headGlowSize = 8;
        beam.colorTail = 'rgba(99, 102, 241, 0.4)';
        beam.colorMid = 'rgba(167, 139, 250, 0.75)';
        beam.colorHeadGlow = 'rgba(216, 180, 254, 0.6)';
        beam.colorSpark = 'rgba(224, 231, 255, ';
      } else if (archetype === 1) {
        // Longer & soft luminous
        beam.length = 290 + Math.random() * 90;
        beam.speed = 1750 + Math.random() * 450;
        beam.duration = 0.88 + Math.random() * 0.22;
        beam.glowWidth = 5.6;
        beam.coreWidth = 1.9;
        beam.headGlowSize = 13;
        beam.colorTail = 'rgba(139, 92, 246, 0.45)';
        beam.colorMid = 'rgba(192, 132, 252, 0.82)';
        beam.colorHeadGlow = 'rgba(233, 213, 255, 0.75)';
        beam.colorSpark = 'rgba(245, 208, 254, ';
      } else {
        // Balanced starlight ray
        beam.length = 220 + Math.random() * 60;
        beam.speed = 2100 + Math.random() * 500;
        beam.duration = 0.68 + Math.random() * 0.16;
        beam.glowWidth = 4.6;
        beam.coreWidth = 1.5;
        beam.headGlowSize = 10;
        beam.colorTail = 'rgba(79, 70, 229, 0.4)';
        beam.colorMid = 'rgba(147, 51, 234, 0.75)';
        beam.colorHeadGlow = 'rgba(192, 132, 252, 0.65)';
        beam.colorSpark = 'rgba(216, 180, 254, ';
      }

      beam.active = true;
      beam.angle = angle;
      beam.progress = 0;
      beam.x = startX;
      beam.y = startY;
      beam.vx = Math.cos(angle) * beam.speed;
      beam.vy = Math.sin(angle) * beam.speed;
      beam.sparks.length = 0;
    };

    // Resize handler
    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);

      if (particles.length === 0) {
        initParticles(width, height);
      }
    };

    // Pointer listener
    const onPointerMove = (e: PointerEvent) => {
      targetCursorX = e.clientX;
      targetCursorY = e.clientY;
      cursorActive = true;
      lastCursorMove = performance.now();
    };

    const onPointerLeave = () => {
      cursorActive = false;
      targetCursorX = -9999;
      targetCursorY = -9999;
    };

    // Passive scroll listener
    const onScroll = () => {
      targetScrollY = window.scrollY;
    };

    // Main draw loop
    const draw = (dt: number) => {
      if (!width || !height) return;
      time += dt;

      // Smooth cursor interpolation
      const cursorLerp = 1 - Math.exp(-dt * 10);
      cursorX += (targetCursorX - cursorX) * cursorLerp;
      cursorY += (targetCursorY - cursorY) * cursorLerp;

      // Deactivate cursor after inactivity
      if (cursorActive && performance.now() - lastCursorMove > 2400) {
        cursorActive = false;
      }

      // Smooth scroll parallax
      currentScrollY += (targetScrollY - currentScrollY) * (1 - Math.exp(-dt * 6));

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);

      // --- 1. RENDER & UPDATE PARTICLES ---
      const tau = Math.PI * 2;
      const damping = Math.pow(0.86, dt * 60);
      const springK = 4.2;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        if (!reduced) {
          // Cosmic drift of origin
          p.originX += p.baseDriftX * dt;
          p.originY += p.baseDriftY * dt;

          // Wrap origin smoothly
          if (p.originX < -30) p.originX += width + 60;
          else if (p.originX > width + 30) p.originX -= width + 60;
          if (p.originY < -30) p.originY += height + 60;
          else if (p.originY > height + 30) p.originY -= height + 60;

          // Cursor cosmic field disturbance
          if (cursorActive && cursorX > -500) {
            const dx = p.x - cursorX;
            const dy = p.y - cursorY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const radius = 145 * (0.55 + p.depth * 0.45);

            if (dist < radius && dist > 1) {
              const normDist = 1 - dist / radius;
              // Smooth cubic ease curve
              const force = normDist * normDist * (3 - 2 * normDist) * p.depth * 80;
              const angle = Math.atan2(dy, dx);
              const pushX = Math.cos(angle) * force;
              const pushY = Math.sin(angle) * force;

              // Gentle tangential swirl
              const swirlAngle = angle + Math.PI * 0.36;
              const swirlForce = force * 0.38;
              const swirlX = Math.cos(swirlAngle) * swirlForce;
              const swirlY = Math.sin(swirlAngle) * swirlForce;

              p.vx += (pushX + swirlX) * dt * 4;
              p.vy += (pushY + swirlY) * dt * 4;
            }
          }

          // Restitution spring force towards drifting origin
          p.vx += (p.originX - p.x) * springK * dt;
          p.vy += (p.originY - p.y) * springK * dt;

          // Damping
          p.vx *= damping;
          p.vy *= damping;

          // Step position
          p.x += p.vx;
          p.y += p.vy;
        }

        // Apply smooth scroll parallax
        const parallaxOffsetY = currentScrollY * p.depth * 0.065;
        let renderY = (p.y - parallaxOffsetY) % height;
        if (renderY < 0) renderY += height;
        let renderX = p.x % width;
        if (renderX < 0) renderX += width;

        // Twinkle factor
        const twinkle = reduced
          ? 1
          : 0.75 + Math.sin(time * p.twinkleSpeed + p.twinklePhase) * 0.25;
        const alpha = Math.min(1, Math.max(0.05, p.baseAlpha * twinkle));

        ctx.fillStyle = p.color;
        ctx.globalAlpha = alpha;

        // Draw particle
        ctx.beginPath();
        ctx.arc(renderX, renderY, p.radius, 0, tau);
        ctx.fill();

        // Layer 2 Energy particles get an ethereal soft aura
        if (p.layer === 2 && !reduced && alpha > 0.4) {
          ctx.beginPath();
          ctx.arc(renderX, renderY, p.radius * 2.8, 0, tau);
          ctx.fillStyle = 'rgba(187, 168, 241, ' + (alpha * 0.28) + ')';
          ctx.fill();
        }
      }

      ctx.globalAlpha = 1;

      // --- 2. MULTIPLE OCCASIONAL SHOOTING COSMIC BEAMS ---
      if (!reduced) {
        nextBeamTimer -= dt;
        if (nextBeamTimer <= 0) {
          triggerShootingBeam();
          // Reset interval for next beam: between 5.0 and 11.5 seconds (random, natural timing)
          nextBeamTimer = 5.0 + Math.random() * 6.5;

          // 30% chance to schedule a complementary second beam shortly after (1.2 to 2.4s)
          if (Math.random() < 0.3) {
            secondaryBeamTimer = 1.2 + Math.random() * 1.2;
          }
        }

        if (secondaryBeamTimer > 0) {
          secondaryBeamTimer -= dt;
          if (secondaryBeamTimer <= 0) {
            triggerShootingBeam();
          }
        }

        // Update and render active beams
        for (let b = 0; b < beamPool.length; b++) {
          const beam = beamPool[b];
          if (!beam.active) continue;

          beam.progress += dt / beam.duration;
          if (beam.progress >= 1) {
            beam.active = false;
            continue;
          }

          // Move beam head
          beam.x += beam.vx * dt;
          beam.y += beam.vy * dt;

          // Tail coordinates with smooth growth and decay
          const tailFactor = Math.min(1, Math.min(beam.progress * 3.8, (1 - beam.progress) * 3.8 + 0.15));
          const tailLen = beam.length * Math.max(0.12, tailFactor);
          const tailX = beam.x - Math.cos(beam.angle) * tailLen;
          const tailY = beam.y - Math.sin(beam.angle) * tailLen;

          // Smooth sinusoidal opacity envelope (eases in and out)
          const envelope = Math.sin(beam.progress * Math.PI);

          ctx.save();
          ctx.globalCompositeOperation = 'lighter';

          // Outer glowing atmospheric streak
          const grad = ctx.createLinearGradient(tailX, tailY, beam.x, beam.y);
          grad.addColorStop(0, 'rgba(0, 0, 0, 0)');
          grad.addColorStop(0.3, beam.colorTail.replace('0.4', String(0.32 * envelope)).replace('0.45', String(0.35 * envelope)));
          grad.addColorStop(0.72, beam.colorMid.replace('0.75', String(0.75 * envelope)).replace('0.82', String(0.8 * envelope)));
          grad.addColorStop(1, 'rgba(255, 255, 255, ' + (0.95 * envelope) + ')');

          ctx.beginPath();
          ctx.moveTo(tailX, tailY);
          ctx.lineTo(beam.x, beam.y);
          ctx.strokeStyle = grad;
          ctx.lineWidth = beam.glowWidth;
          ctx.lineCap = 'round';
          ctx.stroke();

          // Sharp luminous inner electric core
          ctx.beginPath();
          ctx.moveTo(tailX, tailY);
          ctx.lineTo(beam.x, beam.y);
          ctx.strokeStyle = 'rgba(255, 255, 255, ' + (0.92 * envelope) + ')';
          ctx.lineWidth = beam.coreWidth;
          ctx.stroke();

          // Glowing head flare
          const headGlow = ctx.createRadialGradient(beam.x, beam.y, 0, beam.x, beam.y, beam.headGlowSize);
          headGlow.addColorStop(0, 'rgba(255, 255, 255, ' + (0.95 * envelope) + ')');
          headGlow.addColorStop(0.35, beam.colorHeadGlow.replace('0.6', String(0.6 * envelope)).replace('0.65', String(0.65 * envelope)).replace('0.75', String(0.75 * envelope)));
          headGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
          ctx.fillStyle = headGlow;
          ctx.beginPath();
          ctx.arc(beam.x, beam.y, beam.headGlowSize, 0, tau);
          ctx.fill();

          // Emit trailing stardust sparks (bounded to 10 max per beam)
          if (Math.random() < 0.45 && beam.sparks.length < 10) {
            const spread = (Math.random() - 0.5) * 6;
            beam.sparks.push({
              x: beam.x + Math.sin(beam.angle) * spread,
              y: beam.y - Math.cos(beam.angle) * spread,
              vx: -Math.cos(beam.angle) * (90 + Math.random() * 70),
              vy: -Math.sin(beam.angle) * (90 + Math.random() * 70),
              alpha: 0.8 * envelope,
              maxLife: 0.4,
              life: 0.4,
              size: 1.0 + Math.random() * 0.8,
              color: beam.colorSpark,
            });
          }

          ctx.restore();
        }

        // Update and render trailing beam sparks
        for (let b = 0; b < beamPool.length; b++) {
          const beam = beamPool[b];
          if (beam.sparks.length === 0) continue;

          ctx.save();
          ctx.globalCompositeOperation = 'lighter';
          for (let s = beam.sparks.length - 1; s >= 0; s--) {
            const sp = beam.sparks[s];
            sp.life -= dt;
            if (sp.life <= 0) {
              beam.sparks.splice(s, 1);
              continue;
            }
            sp.x += sp.vx * dt;
            sp.y += sp.vy * dt;
            const sparkAlpha = (sp.life / sp.maxLife) * sp.alpha;

            ctx.fillStyle = sp.color + sparkAlpha + ')';
            ctx.beginPath();
            ctx.arc(sp.x, sp.y, sp.size, 0, tau);
            ctx.fill();
          }
          ctx.restore();
        }
      }
    };

    // Frame loop
    const loop = createFrameLoop(draw, {
      request: (cb) => window.requestAnimationFrame(cb),
      cancel: (id) => window.cancelAnimationFrame(id),
    });

    const updateRunning = () => {
      if (document.hidden || !visible || reduced) {
        loop.stop();
        if (reduced) draw(0);
      } else {
        loop.start();
      }
    };

    const observer = new ResizeObserver(resize);
    observer.observe(canvas);

    const intersection = new IntersectionObserver(
      (entries) => {
        visible = entries[0].isIntersecting;
        updateRunning();
      },
      { threshold: 0 }
    );
    intersection.observe(canvas);

    resize();
    updateRunning();

    window.addEventListener('pointermove', onPointerMove, { passive: true });
    window.addEventListener('pointerleave', onPointerLeave, { passive: true });
    window.addEventListener('scroll', onScroll, { passive: true });
    document.addEventListener('visibilitychange', updateRunning);

    return () => {
      loop.dispose();
      observer.disconnect();
      intersection.disconnect();
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerleave', onPointerLeave);
      window.removeEventListener('scroll', onScroll);
      document.removeEventListener('visibilitychange', updateRunning);
      canvas.width = 0;
      canvas.height = 0;
    };
  }, [mode, reduced]);

  return (
    <div
      aria-hidden="true"
      className="cosmic-background fixed inset-0 z-0 overflow-hidden pointer-events-none select-none bg-[#020203]"
      style={{ contain: 'strict' }}
    >
      <div className="cosmic-nebula" />
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full block pointer-events-none"
      />
      <div className="cosmic-vignette" />
    </div>
  );
};
