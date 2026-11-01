import { useEffect, useRef } from 'react';
import { useEffects } from './EffectsProvider';
import { createFrameLoop } from '../lib/frameLoop';

interface RiftParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  life: number;
  maxLife: number;
  color: string;
}

interface DistantStar {
  x: number;
  y: number;
  size: number;
  baseAlpha: number;
  twinkleSpeed: number;
  phase: number;
}

interface Props {
  className?: string;
  speedMultiplier?: number;
}

/**
 * Distant Cosmic Slash / Dimensional Rift.
 * Renders an ethereal diagonal fissure in spacetime with glowing violet-blue energy,
 * subtle plasma flow along the rift seam, gentle atmospheric haze, and occasional
 * escaping dimensional particles.
 */
export function CosmicRiftCanvas({ className = '', speedMultiplier = 1 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { reduced, mode } = useEffects();

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d', { alpha: true });
    if (!canvas || !ctx) return;

    let width = 0;
    let height = 0;
    let dpr = 1;
    let time = 0;
    let visible = true;
    let isScrolling = false;
    let scrollTimer: number | null = null;

    const compact = mode !== 'full' || window.matchMedia('(max-width: 768px)').matches;

    // Distant background stars around the rift
    const starCount = compact ? 18 : 36;
    const distantStars: DistantStar[] = [];
    for (let i = 0; i < starCount; i++) {
      distantStars.push({
        x: Math.random(),
        y: Math.random(),
        size: Math.random() < 0.2 ? 1.4 : 0.8,
        baseAlpha: 0.15 + Math.random() * 0.45,
        twinkleSpeed: 0.6 + Math.random() * 1.8,
        phase: Math.random() * Math.PI * 2,
      });
    }

    // Escaping dimensional spark particles
    const maxParticles = compact ? 8 : 16;
    const particles: RiftParticle[] = [];
    const colors = [
      '220,185,255', // Lavender
      '147,197,253', // Electric cyan-blue
      '192,132,252', // Soft magenta
      '255,255,255', // Hot white spark
    ];

    const spawnParticle = () => {
      if (particles.length >= maxParticles) return;
      // Spawn along the diagonal rift line
      const t = 0.2 + Math.random() * 0.6; // Spawn mostly in active mid-section
      const startX = width * (0.35 + t * 0.45);
      const startY = height * (0.15 + t * 0.7);

      // Eject perpendicular to the slash with gentle drift
      const angle = -0.75 + (Math.random() - 0.5) * 0.8;
      const speed = 12 + Math.random() * 22;

      particles.push({
        x: startX,
        y: startY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 0.8 + Math.random() * 1.4,
        life: 0,
        maxLife: 2.2 + Math.random() * 1.8,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    };

    let spawnCooldown = 0;

    const draw = (dt: number) => {
      if (!width || !height || isScrolling) return;
      time += dt * speedMultiplier;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);

      // 1. Distant ambient stars
      for (const star of distantStars) {
        const sx = star.x * width;
        const sy = star.y * height;
        const twinkle = 0.6 + Math.sin(time * star.twinkleSpeed + star.phase) * 0.4;
        ctx.fillStyle = `rgba(216,201,255,${star.baseAlpha * twinkle})`;
        ctx.fillRect(sx, sy, star.size, star.size);
      }

      ctx.save();
      ctx.globalCompositeOperation = 'lighter';

      // Define the diagonal slash anchor coordinates
      // Diagonal angle from top-left-center to bottom-right (~ -38 degrees)
      const x1 = width * 0.32;
      const y1 = height * 0.12;
      const x2 = width * 0.82;
      const y2 = height * 0.88;
      const dx = x2 - x1;
      const dy = y2 - y1;
      const length = Math.sqrt(dx * dx + dy * dy);
      const angle = Math.atan2(dy, dx);

      ctx.translate(x1, y1);
      ctx.rotate(angle);

      // 2. Deep Atmospheric Nebular Glow behind the rift
      const glowGrad = ctx.createLinearGradient(0, -60, 0, 60);
      glowGrad.addColorStop(0, 'rgba(59,130,246,0)');
      glowGrad.addColorStop(0.25, 'rgba(124,58,237,0.06)');
      glowGrad.addColorStop(0.5, 'rgba(168,85,247,0.14)');
      glowGrad.addColorStop(0.75, 'rgba(79,70,229,0.06)');
      glowGrad.addColorStop(1, 'rgba(30,15,60,0)');

      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.ellipse(length * 0.5, 0, length * 0.52, 65, 0, 0, Math.PI * 2);
      ctx.fill();

      // Secondary soft cyan-violet aura
      const pulse = 1 + Math.sin(time * 0.8) * 0.08;
      const auraGrad = ctx.createRadialGradient(
        length * 0.5, 0, 0,
        length * 0.5, 0, length * 0.45 * pulse
      );
      auraGrad.addColorStop(0, 'rgba(192,132,252,0.18)');
      auraGrad.addColorStop(0.4, 'rgba(99,102,241,0.09)');
      auraGrad.addColorStop(1, 'rgba(15,10,40,0)');
      ctx.fillStyle = auraGrad;
      ctx.fillRect(0, -50, length, 100);

      // 3. Flowing Energy Ribbon along the Rift Fissure
      // Smooth sinusoidal energy waves undulating along the length
      const segments = compact ? 22 : 38;
      ctx.beginPath();
      for (let i = 0; i <= segments; i++) {
        const u = i / segments; // 0 to 1
        const posX = u * length;
        // Taper to 0 at ends so rift fades seamlessly without hard boundaries
        const taper = Math.sin(u * Math.PI);
        const wave = (Math.sin(u * 8 + time * 1.4) * 3.5 + Math.sin(u * 16 - time * 2.2) * 1.5) * taper;
        if (i === 0) ctx.moveTo(posX, wave);
        else ctx.lineTo(posX, wave);
      }

      // Outer violet energy casing
      ctx.strokeStyle = 'rgba(139,92,246,0.22)';
      ctx.lineWidth = 14;
      ctx.stroke();

      // Mid radiant lavender plasma
      ctx.strokeStyle = 'rgba(192,132,252,0.48)';
      ctx.lineWidth = 4.5;
      ctx.stroke();

      // Sharp razor-thin central dimensional light seam
      ctx.strokeStyle = 'rgba(255,255,255,0.85)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      // 4. Luminous nodes / energy surges traveling along the slash
      for (let n = 0; n < 3; n++) {
        const surgeProg = (time * (0.12 + n * 0.04) + n * 0.33) % 1;
        const surgeX = surgeProg * length;
        const surgeTaper = Math.sin(surgeProg * Math.PI);
        const surgeY = Math.sin(surgeProg * 8 + time * 1.4) * 3.5 * surgeTaper;

        const nodeGrad = ctx.createRadialGradient(surgeX, surgeY, 0, surgeX, surgeY, 18);
        nodeGrad.addColorStop(0, `rgba(255,255,255,${0.65 * surgeTaper})`);
        nodeGrad.addColorStop(0.3, `rgba(192,132,252,${0.35 * surgeTaper})`);
        nodeGrad.addColorStop(1, 'rgba(124,58,237,0)');
        ctx.fillStyle = nodeGrad;
        ctx.beginPath();
        ctx.arc(surgeX, surgeY, 18, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();

      // 5. Escaping Dimensional Spark Particles
      if (!reduced) {
        spawnCooldown -= dt;
        if (spawnCooldown <= 0) {
          spawnParticle();
          spawnCooldown = 0.35 + Math.random() * 0.45;
        }

        for (let i = particles.length - 1; i >= 0; i--) {
          const p = particles[i];
          p.life += dt;
          if (p.life >= p.maxLife) {
            particles.splice(i, 1);
            continue;
          }

          p.x += p.vx * dt;
          p.y += p.vy * dt;

          const progress = p.life / p.maxLife;
          const alpha = Math.sin(progress * Math.PI) * 0.65;

          ctx.fillStyle = `rgba(${p.color},${alpha})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size * (1 - progress * 0.3), 0, Math.PI * 2);
          ctx.fill();
        }
      }
    };

    const loop = createFrameLoop(draw, {
      request: (cb) => requestAnimationFrame(cb),
      cancel: (id) => cancelAnimationFrame(id),
    });

    const updateRunning = () => {
      if (!reduced && !document.hidden && visible) loop.start();
      else loop.stop();
    };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      dpr = Math.min(window.devicePixelRatio || 1, compact ? 1.0 : 1.25);
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      draw(0);
    };

    // Pause rendering loop during active scroll to ensure solid 60 FPS
    const onScroll = () => {
      isScrolling = true;
      if (scrollTimer !== null) window.clearTimeout(scrollTimer);
      scrollTimer = window.setTimeout(() => {
        isScrolling = false;
        scrollTimer = null;
        if (visible && !document.hidden && !reduced) draw(0);
      }, 100);
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

    window.addEventListener('scroll', onScroll, { passive: true });
    document.addEventListener('visibilitychange', updateRunning);

    return () => {
      loop.dispose();
      observer.disconnect();
      intersection.disconnect();
      window.removeEventListener('scroll', onScroll);
      document.removeEventListener('visibilitychange', updateRunning);
      if (scrollTimer !== null) window.clearTimeout(scrollTimer);
      canvas.width = 0;
      canvas.height = 0;
    };
  }, [reduced, speedMultiplier, mode]);

  return (
    <div aria-hidden="true" className={'cosmic-rift-wrapper ' + className}>
      <canvas ref={canvasRef} className="block w-full h-full" />
    </div>
  );
}

