import { useEffect, useRef } from 'react';
import { useEffects } from './EffectsProvider';
import { createFrameLoop } from '../lib/frameLoop';

interface Props {
  className?: string;
  speedMultiplier?: number;
  pulse?: number;
}

/**
 * Cosmic Sun & Stellar Energy Core Canvas.
 * Features an animated solar photosphere surface with living plasma convection cells,
 * flowing turbulent currents, molten active regions, hot energy veins, limb darkening,
 * undulating corona rim, 3D magnetosphere ribbons, and solar flare eruptions.
 *
 * Performance-optimized: pauses during active scroll and offscreen states for smooth 60 FPS.
 */
export function CelestialEnergyCanvas({ className = '', speedMultiplier = 1, pulse = 0 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pulseRef = useRef(0);
  const { reduced, mode } = useEffects();

  useEffect(() => {
    if (pulse > 0 && !reduced) pulseRef.current = 1;
  }, [pulse, reduced]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d', { alpha: true });
    if (!canvas || !ctx) return;

    let width = 0, height = 0, dpr = 1, time = 0, visible = true;
    let pointerX = 0, pointerY = 0, tiltX = 0, tiltY = 0;

    const compact = mode !== 'full' || window.matchMedia('(max-width: 640px)').matches;
    const filamentCount = compact ? 10 : 16;
    const steps = compact ? 54 : 84;
    const tau = Math.PI * 2;

    const draw = (dt: number) => {
      if (!width || !height) return;
      time += dt * speedMultiplier;

      const smoothing = 1 - Math.exp(-dt * 3);
      tiltX += (pointerX - tiltX) * smoothing;
      tiltY += (pointerY - tiltY) * smoothing;
      pulseRef.current = reduced ? 0 : Math.max(0, pulseRef.current - dt * 0.55);
      const interaction = pulseRef.current;

      const scale = Math.min(width, height) / 600;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      ctx.translate(width / 2, height / 2);
      ctx.scale(scale, scale);

      const breathing = 1 + Math.sin(time * 0.7) * 0.025;
      const rotation = time * 0.075 + tiltX;
      const sunRadius = 138 * breathing;

      const glow = (x: number, y: number, r: number, color: string, strength: number) => {
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, r);
        gradient.addColorStop(0, 'rgba(' + color + ',' + strength + ')');
        gradient.addColorStop(0.4, 'rgba(' + color + ',' + strength * 0.35 + ')');
        gradient.addColorStop(1, 'rgba(' + color + ',0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(x - r, y - r, r * 2, r * 2);
      };

      const project = (x: number, y: number, z: number) => {
        const rx = 0.28 + tiltY;
        const yy = y * Math.cos(rx) - z * Math.sin(rx);
        const zz = y * Math.sin(rx) + z * Math.cos(rx);
        const xx = x * Math.cos(rotation) + zz * Math.sin(rotation);
        const depth = -x * Math.sin(rotation) + zz * Math.cos(rotation);
        const perspective = 680 / (680 + depth);
        return { x: xx * perspective, y: yy * perspective, depth };
      };

      ctx.globalCompositeOperation = 'lighter';

      // 1. Atmospheric Stellar Corona Halos
      glow(0, 0, 280, '100,55,225', 0.24 + interaction * 0.08);
      glow(-45, 35, 185 * breathing, '122,54,236', 0.28);
      glow(52, -42, 140, '36,102,239', 0.29);

      // 2. Visible Sun-Like Photosphere Surface with Living Convection Detail
      ctx.save();
      ctx.beginPath();
      ctx.arc(0, 0, sunRadius, 0, tau);
      ctx.clip(); // Restrict surface texture strictly inside stellar disk

      // 2A. Base Photosphere with Realistic Stellar Limb Darkening
      const sunCenterOffsetX = tiltX * 42;
      const sunCenterOffsetY = tiltY * 32;
      const sunGrad = ctx.createRadialGradient(
        sunCenterOffsetX, sunCenterOffsetY, 0,
        0, 0, sunRadius
      );
      sunGrad.addColorStop(0, 'rgba(255,248,255,0.96)');   // Hot white-lavender core center
      sunGrad.addColorStop(0.18, 'rgba(235,200,255,0.90)'); // Soft pink/lavender heat
      sunGrad.addColorStop(0.42, 'rgba(172,110,255,0.84)'); // Electric violet mantle
      sunGrad.addColorStop(0.72, 'rgba(96,44,198,0.88)');   // Deep convective indigo
      sunGrad.addColorStop(0.92, 'rgba(42,16,105,0.94)');   // Dark violet limb
      sunGrad.addColorStop(1, 'rgba(18,6,50,0.98)');        // Photospheric rim
      ctx.fillStyle = sunGrad;
      ctx.fill();

      // 2B. Flowing Solar Plasma Currents (Differential Rotation Streams)
      const streamCount = compact ? 5 : 8;
      for (let s = 0; s < streamCount; s++) {
        const lat = (s - (streamCount - 1) / 2) / (streamCount / 2); // -1 to 1
        const yBase = lat * sunRadius * 0.88;
        const xHalf = Math.sqrt(Math.max(0, sunRadius * sunRadius - yBase * yBase));
        if (xHalf < 12) continue;

        const streamSpeed = (1.15 - Math.abs(lat) * 0.38) * (s % 2 === 0 ? 1 : 0.88);
        const streamPhase = s * 1.75 + time * streamSpeed * 0.45;

        ctx.beginPath();
        const segs = compact ? 18 : 28;
        for (let j = 0; j <= segs; j++) {
          const px = -xHalf + (j / segs) * (2 * xHalf);
          const wave = Math.sin(px * 0.045 + streamPhase) * 6
                     + Math.sin(px * 0.09 - time * 0.65 + s) * 3
                     + Math.sin(px * 0.02 + time * 0.22) * 3.5;
          const py = yBase + wave;
          if (j === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }

        const streamAlpha = (0.26 + Math.sin(time * 0.75 + s) * 0.12) * (1 - Math.abs(lat) * 0.35);
        const isHighlight = s % 3 === 0;
        ctx.strokeStyle = isHighlight
          ? `rgba(255,215,250,${streamAlpha * 0.85})` // Hot soft pink streak
          : s % 2 === 0
          ? `rgba(175,130,255,${streamAlpha})`        // Luminous violet plasma
          : `rgba(96,150,255,${streamAlpha * 0.8})`;   // Electric blue convective stream
        ctx.lineWidth = isHighlight ? 2.5 : 4.2;
        ctx.stroke();
      }

      // 2C. Solar Convection Granules (Cellular Boiling Mesh)
      const granuleCount = compact ? 30 : 52;
      for (let g = 0; g < granuleCount; g++) {
        const phi = Math.acos(1 - 2 * (g + 0.5) / granuleCount);
        const theta = g * 2.39996 + rotation * 0.75 + Math.sin(time * 0.18 + g) * 0.12;
        const gx = sunRadius * 0.94 * Math.sin(phi) * Math.cos(theta);
        const gy = sunRadius * 0.94 * Math.cos(phi);
        const gz = sunRadius * 0.94 * Math.sin(phi) * Math.sin(theta);

        if (gz > -12) {
          const p = project(gx, gy, gz);
          const granulePulse = Math.sin(time * 1.15 + g * 1.6) * 0.5 + 0.5;
          const grSize = (10 + (g % 5) * 3) * (0.8 + granulePulse * 0.4);

          const gGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, grSize);
          const isHot = g % 6 === 0;
          if (isHot) {
            gGrad.addColorStop(0, `rgba(255,245,252,${0.42 + granulePulse * 0.35})`);
            gGrad.addColorStop(0.4, `rgba(220,150,255,${0.24 + granulePulse * 0.2})`);
          } else {
            gGrad.addColorStop(0, `rgba(195,155,255,${0.22 + granulePulse * 0.18})`);
            gGrad.addColorStop(0.5, `rgba(112,62,215,${0.13 + granulePulse * 0.1})`);
          }
          gGrad.addColorStop(1, 'rgba(40,15,85,0)');

          ctx.fillStyle = gGrad;
          ctx.beginPath();
          ctx.arc(p.x, p.y, grSize, 0, tau);
          ctx.fill();
        }
      }

      // 2D. Hot Magnetic Energy Veins (Meandering Flux Tubes)
      for (let v = 0; v < 3; v++) {
        const vPhase = v * 2.1 + time * 0.18;
        const vPulse = Math.sin(time * 0.85 + v * 1.5) * 0.5 + 0.5;
        ctx.beginPath();
        let started = false;
        for (let step = 0; step <= 20; step++) {
          const t = step / 20;
          const vAng = vPhase + (t - 0.5) * 1.6;
          const vLat = (v - 1) * 0.42 + Math.sin(t * Math.PI * 2 + time * 0.5) * 0.18;
          const vx = sunRadius * 0.9 * Math.cos(vAng) * Math.cos(vLat);
          const vy = sunRadius * 0.9 * Math.sin(vLat);
          const vz = sunRadius * 0.9 * Math.sin(vAng) * Math.cos(vLat);
          if (vz > -10) {
            const p = project(vx, vy, vz);
            if (!started) { ctx.moveTo(p.x, p.y); started = true; }
            else ctx.lineTo(p.x, p.y);
          }
        }
        if (started) {
          ctx.strokeStyle = `rgba(255,230,250,${0.32 + vPulse * 0.28})`;
          ctx.lineWidth = 1.6;
          ctx.stroke();
          ctx.strokeStyle = `rgba(195,115,255,${0.16 + vPulse * 0.14})`;
          ctx.lineWidth = 4.2;
          ctx.stroke();
        }
      }

      // 2E. Internal Stellar Heat Highlight
      const heatX = tiltX * 52;
      const heatY = -12 + tiltY * 38;
      const coreHeatGrad = ctx.createRadialGradient(heatX, heatY, 0, heatX, heatY, sunRadius * 0.58);
      coreHeatGrad.addColorStop(0, 'rgba(255,255,255,0.45)');
      coreHeatGrad.addColorStop(0.3, 'rgba(235,195,255,0.26)');
      coreHeatGrad.addColorStop(0.7, 'rgba(162,98,245,0.11)');
      coreHeatGrad.addColorStop(1, 'rgba(60,20,130,0)');
      ctx.fillStyle = coreHeatGrad;
      ctx.beginPath();
      ctx.arc(heatX, heatY, sunRadius * 0.58, 0, tau);
      ctx.fill();

      ctx.restore(); // Restore from photosphere clipping path

      // 3. Undulating Turbulent Photosphere Boundary Rim & Spicules
      ctx.beginPath();
      const rimSteps = compact ? 42 : 72;
      for (let i = 0; i <= rimSteps; i++) {
        const a = (i / rimSteps) * tau;
        const undulation = Math.sin(a * 14 + time * 1.8) * 2.2
                         + Math.sin(a * 26 - time * 2.4) * 1.4
                         + Math.sin(a * 6 + time * 0.7) * 2.6;
        const r = sunRadius + undulation;
        const rx = r * Math.cos(a);
        const ry = r * Math.sin(a);
        if (i === 0) ctx.moveTo(rx, ry);
        else ctx.lineTo(rx, ry);
      }
      ctx.closePath();
      ctx.strokeStyle = 'rgba(220,190,255,0.44)';
      ctx.lineWidth = 2.2;
      ctx.stroke();
      ctx.strokeStyle = 'rgba(152,92,255,0.18)';
      ctx.lineWidth = 6.5;
      ctx.stroke();

      // 4. 3D Magnetosphere Filaments and Ribbons Orbiting the Stellar Core
      for (let ribbon = 0; ribbon < filamentCount; ribbon++) {
        const phase = ribbon * 2.39996;
        const inclination = ribbon * 0.39 + Math.sin(time * 0.12 + phase) * 0.14;
        const radius = (126 + (ribbon % 5) * 6) * breathing;
        ctx.beginPath();
        for (let i = 0; i <= steps; i++) {
          const a = (i / steps) * tau;
          const wave = Math.sin(a * 3 + time * 0.6 + phase) * 7 + Math.sin(a * 7 - time * 0.35 + phase) * 3;
          const r = radius + wave;
          const x = r * Math.cos(a), y = r * Math.sin(a) * Math.cos(inclination), z = r * Math.sin(a) * Math.sin(inclination);
          const p = project(x * Math.cos(phase) - y * Math.sin(phase), x * Math.sin(phase) + y * Math.cos(phase), z);
          if (i === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
        }
        ctx.closePath();
        const color = ribbon % 4 === 0 ? '96,169,255' : ribbon % 3 === 0 ? '213,153,255' : '149,87,245';
        const brightness = 0.22 + Math.pow((Math.sin(time * 0.65 + phase) + 1) / 2, 4) * 0.28;
        ctx.strokeStyle = 'rgba(' + color + ',' + brightness * 0.12 + ')';
        ctx.lineWidth = 8;
        ctx.stroke();
        ctx.strokeStyle = 'rgba(' + color + ',' + (brightness + interaction * 0.12) + ')';
        ctx.lineWidth = ribbon % 3 === 0 ? 1.3 : 0.7;
        ctx.stroke();
      }

      // 5. Traveling Magnetic Arc Flares
      for (let arc = 0; arc < 4; arc++) {
        const phase = arc * 1.7, a0 = time * (arc % 2 ? -0.18 : 0.22) + phase;
        ctx.beginPath();
        for (let j = 0; j <= 25; j++) {
          const a = a0 + j / 25 * 0.55, r = 149 + Math.sin(a * 17 + time * 1.1) * 2;
          const p = project(r * Math.cos(a), r * Math.sin(a) * Math.cos(phase), r * Math.sin(a) * Math.sin(phase));
          if (j === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
        }
        ctx.strokeStyle = 'rgba(185,188,255,' + (0.35 + 0.15 * Math.sin(time * 0.6 + phase)) + ')';
        ctx.lineWidth = 1.1;
        ctx.stroke();
      }

      // 6. Stellar Motes & Photosphere Dust
      const count = compact ? 50 : 85;
      for (let i = 0; i < count; i++) {
        const phi = Math.acos(1 - 2 * (i + 0.5) / count), theta = i * 2.39996 + time * 0.04;
        const r = 148 + Math.sin(time * 0.4 + i) * 7;
        const p = project(r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
        ctx.fillStyle = 'rgba(211,195,255,' + (0.25 + (155 - p.depth) / 310 * 0.45) + ')';
        ctx.beginPath();
        ctx.arc(p.x, p.y, i % 9 === 0 ? 1.6 : 0.75, 0, tau);
        ctx.fill();
      }

      // 7. Dynamic Solar Flare Eruptions & Prominence Loops
      if (!reduced) {
        const flareAge = time % (mode === 'full' ? 13 : 21);
        if (flareAge < 4) {
          const life = flareAge / 4, strength = Math.sin(life * Math.PI);
          const reach = 60 * strength;
          ctx.save();
          ctx.rotate(-0.65);
          glow(120, -50, 24, '126,139,255', strength * 0.25);
          ctx.beginPath();
          ctx.moveTo(120, -50);
          ctx.bezierCurveTo(170 + reach, -110 - reach, 195 + reach, 25, 142, 32);
          ctx.strokeStyle = 'rgba(149,137,255,' + strength * 0.12 + ')';
          ctx.lineWidth = 5;
          ctx.stroke();
          ctx.strokeStyle = 'rgba(184,175,255,' + strength * 0.5 + ')';
          ctx.lineWidth = 1;
          ctx.stroke();
          for (let i = 0; i < 4; i++) {
            const t = (life * 1.5 + i / 4) % 1, u = 1 - t;
            const x = u*u*u*120 + 3*u*u*t*(170+reach) + 3*u*t*t*(195+reach) + t*t*t*142;
            const y = u*u*u*(-50) + 3*u*u*t*(-110-reach) + 3*u*t*t*25 + t*t*t*32;
            ctx.fillStyle = 'rgba(202,196,255,' + strength * 0.6 + ')';
            ctx.beginPath();
            ctx.arc(x, y, 1, 0, tau);
            ctx.fill();
          }
          ctx.restore();
        }

        // Outward Solar Shockwave & Escaping Particles
        const age = interaction > 0 ? (1 - interaction) * 2.5 : (time + 2) % 9;
        if (age < 2.5) {
          const progress = age / 2.5, envelope = Math.sin(progress * Math.PI);
          ctx.strokeStyle = 'rgba(164,127,246,' + envelope * 0.19 + ')';
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.ellipse(0, 0, 160 + progress * 76, 147 + progress * 70, -0.3, 0, tau);
          ctx.stroke();
          for (let i = 0; i < 6; i++) {
            const angle = i * 1.047 + Math.floor(time / 9) * 0.6, radius = 154 + progress * (52 + i * 5);
            const x = Math.cos(angle) * radius, y = Math.sin(angle) * radius;
            glow(x, y, 8, i % 2 ? '164,117,255' : '110,179,255', envelope * 0.4);
            ctx.fillStyle = 'rgba(218,200,255,' + envelope * 0.7 + ')';
            ctx.beginPath();
            ctx.arc(x, y, 1.1, 0, tau);
            ctx.fill();
          }
        }
      }

      ctx.globalCompositeOperation = 'source-over';
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

    const pointer = (e: PointerEvent) => {
      if (reduced || !visible || e.pointerType === 'touch') return;
      const rect = canvas.getBoundingClientRect();
      pointerX = Math.max(-0.12, Math.min(0.12, ((e.clientX - rect.left - width / 2) / width) * 0.2));
      pointerY = Math.max(-0.09, Math.min(0.09, ((e.clientY - rect.top - height / 2) / height) * 0.16));
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

    window.addEventListener('pointermove', pointer, { passive: true });
    document.addEventListener('visibilitychange', updateRunning);

    return () => {
      loop.dispose();
      observer.disconnect();
      intersection.disconnect();
      window.removeEventListener('pointermove', pointer);
      document.removeEventListener('visibilitychange', updateRunning);
      canvas.width = 0;
      canvas.height = 0;
    };
  }, [reduced, speedMultiplier, mode]);

  return (
    <div aria-hidden="true" className={'energy-core ' + className}>
      <div className="energy-core-fallback" />
      <canvas ref={canvasRef} className="relative block w-full h-full" />
    </div>
  );
}
