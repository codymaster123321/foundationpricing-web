import React, { useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import topoJson from '../data/states-10m.json';
import metrics from '../data/state-metrics.json';

const STATE_NAMES_TO_ABBR = {
  "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
  "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
  "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
  "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
  "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
  "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
  "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
  "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
  "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
  "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
  "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
  "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
  "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
};

const getColorByRisk = (index) => {
  if (index >= 25.0) return '#b91c1c'; // Tailwind red-700 (Severe Shrink-Swell)
  if (index >= 18.0) return '#ea580c'; // Tailwind orange-600 (High Risk)
  if (index >= 10.0) return '#d97706'; // Tailwind amber-600 (Moderate Risk)
  if (index > 0.0) return '#eab308';   // Tailwind yellow-500 (Low Clay Risk / Alternative Hazards)
  return '#94a3b8';                    // Tailwind slate-400 (Processing/No Data)
};

export default function UsaRiskMap() {
  const [tooltip, setTooltip] = useState({ show: false, html: null, x: 0, y: 0 });

  const handleMouseEnter = (geo, evt) => {
    const stateName = geo.properties.name;
    const abbr = STATE_NAMES_TO_ABBR[stateName];
    const data = metrics[abbr];

    let htmlContent;
    
    if (data) {
      // THE ACTIVE STATE TOOLTIP
      htmlContent = (
        <div className="flex flex-col gap-1">
          <div className="font-bold text-gray-900 border-b border-gray-200 pb-1 mb-1 text-base">{stateName}</div>
          <div className="flex justify-between items-center text-sm gap-4">
            <span className="text-gray-500 font-medium">Local Reports:</span>
            <span className="font-bold text-blue-700">{data.reportCount}</span>
          </div>
          <div className="flex justify-between items-center text-sm gap-4">
            <span className="text-gray-500 font-medium whitespace-nowrap">Avg USDA Index:</span>
            <span className="font-bold text-red-600">{data.avg_usda_index > 0 ? data.avg_usda_index : 'N/A'}</span>
          </div>
        </div>
      );
    } else {
      // THE INACTIVE STATE TOOLTIP
      htmlContent = (
        <div className="flex flex-col gap-1">
          <div className="font-bold text-gray-700 border-b border-gray-200 pb-1 mb-1">{stateName}</div>
          <div className="text-xs font-semibold text-emerald-600 uppercase tracking-widest mt-1">Coverage: Active</div>
          <div className="text-xs text-gray-500 mt-0.5">Geotechnical Data: <span className="text-blue-500 animate-pulse font-medium">Computing...</span></div>
        </div>
      );
    }

    setTooltip({
      show: true,
      html: htmlContent,
      x: evt.clientX,
      y: evt.clientY
    });
  };

  const handleMouseMove = (evt) => {
    setTooltip(prev => ({
      ...prev,
      x: evt.clientX,
      y: evt.clientY
    }));
  };

  const handleMouseLeave = () => {
    setTooltip({ show: false, html: null, x: 0, y: 0 });
  };

  const handleClick = (geo) => {
    const stateName = geo.properties.name;
    const abbr = STATE_NAMES_TO_ABBR[stateName];
    // Dynamiczny routing Astro SSG posiłkuje się "The State Abbr" a nie Full slugami
    if (abbr) {
        window.location.href = `/${abbr.toLowerCase()}/`;
    }
  };

  return (
    <div className="relative w-full overflow-hidden bg-slate-900 border border-slate-700/50 rounded-[20px] shadow-inner">
      <div className="absolute top-4 left-4 z-10 bg-slate-800/80 backdrop-blur-md px-4 py-3 rounded-xl shadow-lg border border-slate-600/50 pointer-events-none ring-1 ring-white/5">
        <h4 className="text-xs font-bold text-slate-200 uppercase tracking-widest mb-3 border-b border-slate-700/50 pb-2">Risk Heatmap Legend</h4>
        <div className="flex items-center gap-3 text-xs text-slate-300 font-medium mb-1.5">
            <span className="w-3 h-3 rounded-full bg-[#ef4444] shadow-[0_0_8px_rgba(239,68,68,0.6)]"></span> Severe (&gt;25)
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-300 font-medium mb-1.5">
            <span className="w-3 h-3 rounded-full bg-[#f97316] shadow-[0_0_8px_rgba(249,115,22,0.6)]"></span> High (&gt;18)
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-300 font-medium mb-1.5">
            <span className="w-3 h-3 rounded-full bg-[#f59e0b] shadow-[0_0_8px_rgba(245,158,11,0.6)]"></span> Moderate (&gt;10)
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-300 font-medium mb-1.5">
            <span className="w-3 h-3 rounded-full bg-[#eab308] shadow-[0_0_8px_rgba(234,179,8,0.5)]"></span> Low (&lt;10)
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-400 font-medium mt-3 pt-2 border-t border-slate-700/50">
            <span className="w-3 h-3 rounded-full bg-slate-700/80 border border-slate-600"></span> Processing Array...
        </div>
      </div>

      <div className="w-full max-w-5xl mx-auto cursor-crosshair">
        <ComposableMap projection="geoAlbersUsa" className="w-full h-full">
          <Geographies geography={topoJson}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const stateName = geo.properties.name;
                const abbr = STATE_NAMES_TO_ABBR[stateName];
                const isActive = metrics[abbr];
                
                // DATA-DRIVEN COLOR MATRIX
                const defaultFill = isActive ? getColorByRisk(isActive.avg_usda_index) : "#1e293b"; // slate-800 dla inactive (Dark mode map)
                const hoverFill = isActive ? defaultFill : "#334155"; // slate-700 dla hover inactive w dark mode
                const strokeColor = "#0f172a"; // slate-900 obrysy stanów


                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    onMouseEnter={(evt) => handleMouseEnter(geo, evt)}
                    onMouseMove={handleMouseMove}
                    onMouseLeave={handleMouseLeave}
                    onClick={() => handleClick(geo)}
                    style={{
                      default: {
                        fill: defaultFill,
                        stroke: strokeColor,
                        strokeWidth: 0.75,
                        outline: "none",
                        transition: "all 300ms ease"
                      },
                      hover: {
                        fill: hoverFill,
                        opacity: isActive ? 0.8 : 1.0,
                        stroke: strokeColor,
                        strokeWidth: 1.5,
                        outline: "none",
                        cursor: "pointer",
                        transition: "all 300ms ease",
                        transformOrigin: "center"
                      },
                      pressed: {
                        fill: hoverFill,
                        opacity: 0.9,
                        stroke: strokeColor,
                        strokeWidth: 1.5,
                        outline: "none",
                      }
                    }}
                  />
                );
              })
            }
          </Geographies>
        </ComposableMap>
      </div>

      {/* RENDEROWANIE FIXED NATIVE TOOLTIP (THE FLOATING CARD) */}
      {tooltip.show && (
        <div 
          className="fixed z-50 pointer-events-none bg-white p-4 rounded-xl shadow-2xl border border-blue-100 transform -translate-x-1/2 -translate-y-[120%] transition-opacity duration-200"
          style={{ left: tooltip.x, top: tooltip.y }}
        >
          {/* Ozdobny triangle pointer u dołu */}
          <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-white border-b border-r border-blue-100 rotate-45"></div>
          
          <div className="relative z-10">
            {tooltip.html}
          </div>
        </div>
      )}
    </div>
  );
}
