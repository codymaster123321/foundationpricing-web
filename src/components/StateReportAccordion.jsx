import React, { useState } from 'react';

export default function StateReportAccordion({ children }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="relative w-full">
      <div 
        className={`relative overflow-hidden transition-all duration-1000 ease-in-out ${isExpanded ? 'max-h-[25000px]' : 'max-h-[600px]'}`}
      >
        {children}
        
        {/* Gradient Bottom Overlay when collapsed */}
        <div 
          className={`absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-white to-transparent pointer-events-none transition-opacity duration-500 ${isExpanded ? 'opacity-0' : 'opacity-100'}`}
        ></div>
      </div>

      <div className="mt-8 flex justify-center relataive z-10 bg-white pt-2">
        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="inline-flex items-center justify-center gap-2 bg-blue-50 border border-blue-200 hover:border-blue-300 text-blue-800 font-bold py-3 px-8 rounded-xl shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 hover:bg-blue-100"
        >
          {isExpanded ? 'Collapse Report' : 'Read Full Geotechnical Report'}
          <svg 
            className={`w-5 h-5 text-blue-500 transition-transform duration-500 ${isExpanded ? 'rotate-180' : ''}`} 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
