import { lazy, Suspense, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Plus, Sparkles } from 'lucide-react';
import { DimensionalHeading } from './DimensionalHeading';

const Core = lazy(() =>
  import('./CelestialEnergyCanvas').then((module) => ({
    default: module.CelestialEnergyCanvas,
  }))
);

const Rift = lazy(() =>
  import('./CosmicRiftCanvas').then((module) => ({
    default: module.CosmicRiftCanvas,
  }))
);

export function DashboardHero() {
  const [pulse, setPulse] = useState(0);
  const lastPulse = useRef(-Infinity);

  const energize = () => {
    if (performance.now() - lastPulse.current < 1800) return;
    lastPulse.current = performance.now();
    setPulse((value) => value + 1);
  };

  return (
    <section className="dashboard-hero relative overflow-hidden" aria-labelledby="dashboard-title">
      {/* Distant Cosmic Slash / Dimensional Rift in Far-Right Background */}
      <div className="hero-rift-anchor hidden md:block" aria-hidden="true">
        <Suspense fallback={null}>
          <Rift speedMultiplier={0.8} />
        </Suspense>
      </div>

      {/* Eyebrow Pill */}
      <div className="relative z-10 inline-flex items-center gap-2 px-3 py-1 rounded-full cosmic-glass-pill mb-3">
        <span className="w-1.5 h-1.5 rounded-full bg-[#cab0ff] shadow-[0_0_8px_#ae78fd]" />
        <span className="font-mono text-[9px] uppercase tracking-[0.16em] text-[#d6c3fc]">
          Intelligent Workspace · AI & RAG Engine
        </span>
      </div>

      {/* Hero Visual Stage with AOVIX-Style Watermark and Floating Translucent Glass Telemetry Cards */}
      <div className="hero-core-stage relative flex items-center justify-center">
        {/* Massive Ambient Typographic Watermark behind the sphere */}
        <div className="hero-watermark" aria-hidden="true">
          SMART INVOICE
        </div>

        {/* Floating Telemetry Glass Card: Top Left */}
        <div className="hero-floating-card hero-card-tl hidden md:flex">
          <div className="telemetry-badge">01 // EXTRACTION</div>
          <span className="telemetry-title">PyMuPDF OCR</span>
          <span className="telemetry-sub">Deterministic line parsing</span>
        </div>

        {/* Floating Telemetry Glass Card: Top Right */}
        <div className="hero-floating-card hero-card-tr hidden md:flex">
          <div className="telemetry-badge">02 // COGNITION</div>
          <span className="telemetry-title">Gemini RAG</span>
          <span className="telemetry-sub">ChromaDB vector reasoning</span>
        </div>

        {/* Central Cosmic Sun & Stellar Energy Core */}
        <Suspense fallback={<div className="energy-core-fallback" />}>
          <Core className="hero-core" pulse={pulse} speedMultiplier={0.8} />
        </Suspense>

        {/* Subtle Horizontal Telemetry Coordinate Axis */}
        <div className="hero-axis-line hidden lg:flex" aria-hidden="true">
          <span className="axis-dot-left" />
          <span className="axis-label-left">LAT // 48.8566</span>
          <div className="axis-rule" />
          <span className="axis-label-center">CORE-ENGINE // v2.0</span>
          <div className="axis-rule" />
          <span className="axis-label-right">ATMOSFER // 1-3</span>
          <span className="axis-dot-right" />
        </div>

        {/* Floating Telemetry Glass Card: Bottom Left */}
        <div className="hero-floating-card hero-card-bl hidden md:flex">
          <div className="telemetry-badge">03 // INTEGRITY</div>
          <span className="telemetry-title">Duplicate Shield</span>
          <span className="telemetry-sub">Zero double-payouts</span>
        </div>

        {/* Floating Telemetry Glass Card: Bottom Right */}
        <div className="hero-floating-card hero-card-br hidden md:flex">
          <div className="telemetry-badge">04 // TELEMETRY</div>
          <span className="telemetry-title">Multi-Currency</span>
          <span className="telemetry-sub">Automated valuation</span>
        </div>
      </div>

      {/* Atmospheric Lower Corner Notes (AOVIX Aesthetic) */}
      <div className="hero-subnotes relative z-10 hidden lg:flex justify-between items-center text-left px-4 max-w-6xl mx-auto -mt-6 mb-8 text-[11px] text-[#9c8fb3] font-sans">
        <p className="max-w-[280px] leading-relaxed">
          Smart Invoice Processor automates extraction, reconciles line items, and accelerates financial intelligence with AI.
        </p>
        <p className="max-w-[260px] text-right font-mono text-[10px] tracking-wider text-[#b8a7d1] uppercase">
          Advanced Infrastructure
          <span className="block text-[#84759d] lowercase tracking-normal font-sans">For Autonomous Accounting</span>
        </p>
      </div>

      {/* Hero Headline & Actions */}
      <div className="hero-copy relative z-10">
        <DimensionalHeading id="dashboard-title">
          Every invoice.
          <br />
          <span>One intelligent workspace.</span>
        </DimensionalHeading>

        <p>
          Bring your invoices into focus. Understand your spending,
          <br className="hidden sm:block" /> catch what needs attention, and move forward with clarity.
        </p>

        <div className="hero-actions">
          <Link
            to="/upload"
            className="aovix-gradient-btn hero-primary"
            onPointerEnter={energize}
            onFocus={energize}
          >
            <Plus size={16} /> Upload invoice <ArrowUpRight size={16} />
          </Link>
          <Link
            to="/chat"
            className="hero-secondary"
            onPointerEnter={energize}
            onFocus={energize}
          >
            <Sparkles size={15} /> Ask your invoices
          </Link>
        </div>
      </div>

      <div className="hero-footer relative z-10">
        <span>Less busywork. More perspective.</span>
        <a href="#financial-overview">
          Explore your workspace <span aria-hidden="true">↓</span>
        </a>
      </div>
    </section>
  );
}
