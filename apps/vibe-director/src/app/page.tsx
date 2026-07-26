"use client";

import React, { useState } from "react";
import {
  Settings,
  Send,
  Play,
  Image as ImageIcon,
  Film,
  Video,
  Monitor,
  Camera,
  Layers,
  Wand2,
  ListVideo,
  Mic,
  MoreHorizontal
} from "lucide-react";

export default function VibeDirector() {
  const [activeVibe, setActiveVibe] = useState("Cinematic");
  const [intensity, setIntensity] = useState(50);
  const [aspectRatio, setAspectRatio] = useState("16:9");

  const vibes = [
    { name: "Cinematic", icon: Film },
    { name: "VHS", icon: Video },
    { name: "Anime", icon: Wand2 },
    { name: "Drone", icon: Camera },
  ];

  return (
    <div className="flex h-screen w-full bg-zinc-950 text-zinc-200 overflow-hidden font-sans">

      {/* LEFT SIDEBAR: Chat & Controls */}
      <div className="w-96 flex flex-col border-r border-zinc-800 bg-zinc-900/50 backdrop-blur-sm z-10">

        {/* Header */}
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/80">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-indigo-600 flex items-center justify-center">
              <Camera size={18} className="text-white" />
            </div>
            <h1 className="font-semibold text-lg tracking-tight text-white">Director's Console</h1>
          </div>
          <button className="p-2 text-zinc-400 hover:text-white transition-colors rounded hover:bg-zinc-800">
            <Settings size={18} />
          </button>
        </div>

        {/* Controls Panel */}
        <div className="p-5 border-b border-zinc-800 space-y-6 overflow-y-auto max-h-[40vh] scrollbar-thin scrollbar-thumb-zinc-700">

          {/* Motion Intensity */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="text-sm font-medium text-zinc-300">Motion Intensity</label>
              <span className="text-xs bg-zinc-800 px-2 py-1 rounded text-zinc-400">{intensity}%</span>
            </div>
            <input
              type="range"
              min="0" max="100"
              value={intensity}
              onChange={(e) => setIntensity(Number(e.target.value))}
              className="w-full accent-indigo-500 h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Aspect Ratio */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
              <Monitor size={14} /> Aspect Ratio
            </label>
            <select
              value={aspectRatio}
              onChange={(e) => setAspectRatio(e.target.value)}
              className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5 outline-none"
            >
              <option value="16:9">16:9 (Widescreen)</option>
              <option value="9:16">9:16 (Vertical)</option>
              <option value="1:1">1:1 (Square)</option>
              <option value="21:9">21:9 (Cinematic)</option>
            </select>
          </div>

          {/* Vibes Toggle */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
              <Layers size={14} /> Vibe Override
            </label>
            <div className="grid grid-cols-2 gap-2">
              {vibes.map((vibe) => (
                <button
                  key={vibe.name}
                  onClick={() => setActiveVibe(vibe.name)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-all duration-200 border ${
                    activeVibe === vibe.name
                      ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300'
                      : 'bg-zinc-800/50 border-zinc-700/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200'
                  }`}
                >
                  <vibe.icon size={14} />
                  {vibe.name}
                </button>
              ))}
            </div>
          </div>

        </div>

        {/* Chat Interface */}
        <div className="flex-1 flex flex-col overflow-hidden bg-zinc-950/50">

          {/* Chat Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center shrink-0">
                <span className="text-xs font-semibold">AI</span>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-zinc-300 bg-zinc-800/80 p-3 rounded-2xl rounded-tl-sm inline-block">
                  Ready to direct. Describe the scene you want to generate.
                </p>
                <p className="text-xs text-zinc-500 ml-1">10:42 AM</p>
              </div>
            </div>

            <div className="flex gap-3 flex-row-reverse">
              <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0">
                <span className="text-xs font-semibold">U</span>
              </div>
              <div className="space-y-1 flex flex-col items-end">
                <p className="text-sm text-white bg-indigo-600 p-3 rounded-2xl rounded-tr-sm inline-block shadow-sm">
                  A lone figure walking through a neon-lit cyberpunk street in the rain. Make it moody.
                </p>
                <p className="text-xs text-zinc-500 mr-1">10:43 AM</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center shrink-0">
                <span className="text-xs font-semibold">AI</span>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-zinc-300 bg-zinc-800/80 p-3 rounded-2xl rounded-tl-sm inline-block">
                  <p>Processing request...</p>
                  <div className="flex gap-1 mt-2">
                    <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce"></span>
                    <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce delay-75"></span>
                    <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce delay-150"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Input */}
          <div className="p-4 border-t border-zinc-800 bg-zinc-900/80">
            <div className="relative flex items-center">
              <button className="absolute left-3 p-1.5 text-zinc-400 hover:text-white transition-colors">
                <Mic size={18} />
              </button>
              <input
                type="text"
                placeholder="Direct the scene..."
                className="w-full bg-zinc-800/80 border border-zinc-700 rounded-full py-3 pl-10 pr-12 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all shadow-inner"
              />
              <button className="absolute right-2 p-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-500/20">
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT CANVAS: Preview & Timeline */}
      <div className="flex-1 flex flex-col bg-zinc-950 relative">

        {/* Main Canvas Area */}
        <div className="flex-1 flex items-center justify-center p-8 relative">

          {/* Canvas Toolbar overlay */}
          <div className="absolute top-6 right-6 flex items-center gap-2 bg-zinc-900/80 backdrop-blur-md p-1.5 rounded-lg border border-zinc-800 shadow-xl">
            <button className="p-2 text-zinc-400 hover:text-white transition-colors rounded hover:bg-zinc-800 tooltip" title="Export">
              <MoreHorizontal size={18} />
            </button>
          </div>

          {/* Generated Video/Image Placeholder */}
          <div className="w-full max-w-5xl aspect-video bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl flex flex-col items-center justify-center relative overflow-hidden group">

            {/* Background Grid Pattern for empty state feel */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay pointer-events-none"></div>

            <div className="absolute inset-0 bg-gradient-to-t from-zinc-950/80 via-transparent to-transparent z-10 pointer-events-none"></div>

            {/* Placeholder Image (Simulation of generated content) */}
            <div className="absolute inset-0 bg-zinc-800 animate-pulse opacity-20"></div>

            <div className="z-20 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-indigo-500/20 flex items-center justify-center mx-auto border border-indigo-500/30">
                <Play size={24} className="text-indigo-400 ml-1" />
              </div>
              <div>
                <p className="text-zinc-300 font-medium tracking-wide">Scene 04 Rendering...</p>
                <p className="text-zinc-500 text-sm mt-1">Applying {activeVibe} vibe</p>
              </div>
            </div>

            {/* Progress bar simulation */}
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-zinc-800 z-20">
              <div className="h-full bg-indigo-500 w-2/3 shadow-[0_0_10px_rgba(99,102,241,0.8)]"></div>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="h-48 border-t border-zinc-800 bg-zinc-900/30 backdrop-blur-sm p-4 flex flex-col">
          <div className="flex items-center justify-between mb-3 px-2">
            <h3 className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
              <ListVideo size={16} /> Storyboard
            </h3>
            <span className="text-xs text-zinc-500">4 Scenes • 00:12s</span>
          </div>

          <div className="flex-1 flex gap-3 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-zinc-700 items-end px-2">

            {/* Timeline Thumbnails */}
            {[1, 2, 3].map((scene) => (
              <div key={scene} className="min-w-[160px] h-24 bg-zinc-800 rounded-lg border border-zinc-700 relative group cursor-pointer hover:border-indigo-500/50 transition-colors shrink-0 overflow-hidden">
                <div className="absolute inset-0 bg-zinc-700/50 group-hover:bg-transparent transition-colors"></div>
                <div className="absolute bottom-2 left-2 text-[10px] font-medium bg-black/60 px-1.5 py-0.5 rounded text-zinc-300 backdrop-blur-md">
                  Sc {scene}
                </div>
              </div>
            ))}

            {/* Active/Generating Thumbnail */}
            <div className="min-w-[160px] h-24 bg-zinc-800/50 rounded-lg border-2 border-indigo-500 relative flex items-center justify-center shrink-0 overflow-hidden shadow-[0_0_15px_rgba(99,102,241,0.15)]">
               <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
               <div className="w-6 h-6 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin"></div>
               <div className="absolute bottom-2 left-2 text-[10px] font-medium bg-black/60 px-1.5 py-0.5 rounded text-indigo-300 backdrop-blur-md">
                  Sc 4 (Generating)
               </div>
            </div>

            {/* Add Scene Placeholder */}
            <div className="min-w-[160px] h-24 rounded-lg border border-dashed border-zinc-700 flex items-center justify-center text-zinc-600 hover:text-zinc-400 hover:border-zinc-500 hover:bg-zinc-800/30 transition-all cursor-pointer shrink-0 group">
              <span className="text-2xl group-hover:scale-110 transition-transform">+</span>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
