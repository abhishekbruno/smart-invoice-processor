import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { CosmicBackground } from './CosmicBackground';
import { EffectsProvider } from './EffectsProvider';
import { AnimatedPage } from './AnimatedPage';
import { CosmicTransitionSweep } from './CosmicTransitionSweep';
import { AppLoadingScreen } from './AppLoadingScreen';
import { NotificationProvider } from './NotificationProvider';
import { CommandPalette } from './CommandPalette';

export const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <EffectsProvider>
      <NotificationProvider>
        {/* Full-Screen Initial Cinematic Loading Experience */}
        <AppLoadingScreen />

        {/* Global Command Palette (Ctrl+K / Cmd+K) */}
        <CommandPalette />

        <div className="relative min-h-screen bg-[#020203] text-[#F1EDF8] flex selection:bg-[#4B37B2]/40 selection:text-[#BBA8F1]">
          {/* Persistent Shared Cosmic Atmosphere (Stays Mounted across navigation) */}
          <CosmicBackground />

          {/* Subtle Ambient Cosmic Glow Wash connecting sphere to glass panels */}
          <div className="cosmic-ambient-glow" aria-hidden="true" />

          {/* Ambient Cosmic Transition Energy Sweep across route changes */}
          <CosmicTransitionSweep />

          {/* Main App Layout */}
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

          <div className="relative z-10 flex-1 flex flex-col min-w-0 lg:pl-60">
            <Navbar onToggleSidebar={() => setSidebarOpen((prev) => !prev)} />
            <main id="main-content" className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto">
              <AnimatedPage />
            </main>
          </div>
        </div>
      </NotificationProvider>
    </EffectsProvider>
  );
};
