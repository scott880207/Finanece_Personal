import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="min-h-screen p-6 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex flex-col md:flex-row justify-between items-end pb-6 border-b border-white/5">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-white mb-1">
              Nebula <span className="text-transparent bg-clip-text bg-gradient-to-r from-nebula-400 to-neon-blue">Finance</span>
            </h1>
            <p className="text-slate-400 font-medium text-lg tracking-wide">Command Center</p>
          </div>
          <div className="text-right hidden md:block">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-nebula-300">
              <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse"></div>
              SYSTEM ONLINE
            </div>
          </div>
        </header>
        <main className="animate-enter">
          <Dashboard />
        </main>
      </div>
    </div>
  );
}

export default App;
