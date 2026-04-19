import React, { useState, useEffect } from 'react';
import fallbackZips from '../data/fallback-zips.json';

export default function ZipSearch() {
  const [zip, setZip] = useState('');
  const [error, setError] = useState('');
  const [invalidMsg, setInvalidMsg] = useState(false);
  const [zipMap, setZipMap] = useState(null);

  // Błyskawiczny Fetching asynchroniczny mapowania 4544 kodów pocztowych
  useEffect(() => {
    fetch('/api/zip-map.json')
      .then(res => res.json())
      .then(data => setZipMap(data))
      .catch(err => {
          console.error("[Foundation Pricing] Failed to load local ZIP routing map:", err);
          setError("Warning: System offline. Could not load local route dictionary.");
      });
  }, []);

  const handleZipChange = (e) => {
    setZip(e.target.value);
    if (error) setError('');
    if (invalidMsg) setInvalidMsg(false);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setError('');
    setInvalidMsg(false);
    
    const cleanZip = zip.trim();
    if (cleanZip.length !== 5 || !/^\d+$/.test(cleanZip)) {
      setError('Please enter a valid 5-digit US ZIP Code.');
      return;
    }

    if (!zipMap) {
      setError('System is synchronizing territorial maps. Please try again in a moment...');
      return;
    }

    // Walidacja główna O(1) oparta o zaciągnięty, dynamiczny Pythonowy the Master JSON z backendu
    const primaryRoute = zipMap[cleanZip];
    if (primaryRoute) {
      window.location.href = primaryRoute;
      return;
    }
    
    // Walidacja the Fallback: Weryfikujemy listę zapasowych kodów
    const fallbackStateCode = fallbackZips[cleanZip];
    if (fallbackStateCode) {
      const stateAbbrCode = fallbackStateCode.toLowerCase();
      window.location.href = `/${stateAbbrCode}`;
      return;
    }

    // Ostateczność: kod ZIP nie istenieje publicznym wykazie
    setInvalidMsg(true);
  };

  return (
    <div className="w-full max-w-2xl bg-white rounded-2xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.4)] border border-indigo-100 p-2 sm:p-2.5 relative z-20 mx-auto transition-transform duration-300 hover:scale-[1.02] group">
        
      {/* Outer Glow Effect */}
      <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000 group-hover:duration-200 z-[-1]"></div>

      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row relative bg-white rounded-xl">
        <div className="flex-1 relative flex items-center">
            <div className="absolute left-6 flex items-center pointer-events-none">
                <svg className="h-6 w-6 text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                </svg>
            </div>
            <input 
              type="text" 
              placeholder="Enter local ZIP Code (e.g. 77494)" 
              value={zip}
              onChange={handleZipChange}
              maxLength={5}
              className="w-full pl-16 pr-6 py-5 sm:py-6 text-gray-800 placeholder-gray-400 bg-transparent outline-none focus:ring-0 text-lg sm:text-xl font-semibold tracking-wide border-b border-gray-100 sm:border-b-0"
            />
        </div>
        
        <button 
          type="submit" 
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-5 sm:py-0 px-10 sm:rounded-xl rounded-b-xl shadow-md hover:shadow-lg transition-all active:scale-[0.98] text-lg sm:ml-1 mt-1 sm:mt-0 flex items-center justify-center gap-2 w-full sm:w-auto overflow-hidden relative"
        >
          <span className="relative z-10 whitespace-nowrap">Analyze Data</span>
          <svg className="w-5 h-5 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
        </button>
      </form>

      {/* Cybernetic Error Toast */}
      {error && (
        <div className="absolute top-full mt-4 left-4 right-4 sm:left-auto sm:right-0 sm:w-96 p-4 bg-white/95 backdrop-blur-md border-l-4 border-red-500 rounded-lg shadow-[0_10px_40px_-10px_rgba(220,38,38,0.3)] animate-in fade-in slide-in-from-top-4 flex items-start gap-3">
          <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <div className="text-gray-800 text-sm font-medium leading-snug">{error}</div>
        </div>
      )}
      
      {/* Target Not Found Toast - Clean without external affiliation number */}
      {invalidMsg && (
        <div className="absolute top-full mt-4 left-4 right-4 sm:left-auto sm:right-0 sm:w-96 p-4 bg-white/95 backdrop-blur-md border-l-4 border-amber-500 rounded-lg shadow-[0_10px_40px_-10px_rgba(245,158,11,0.2)] animate-in fade-in slide-in-from-top-4 flex items-start gap-3">
          <svg className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <div className="text-gray-800 text-sm font-medium leading-snug">
            <strong>Routing Notice:</strong> The ZCTA <span className="font-bold text-amber-600">{zip}</span> does not map to any known structural data zones.
            <div className="mt-2 text-xs text-gray-500">
              Please verify your 5-digit ZIP Code or try a neighboring region.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
