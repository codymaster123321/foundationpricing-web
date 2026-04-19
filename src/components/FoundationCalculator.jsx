import React, { useState } from 'react';

const ENGINEERING_FEE = 750;
const PERMIT_FEE = 400;
const FIXED_OVERHEAD = ENGINEERING_FEE + PERMIT_FEE;

export default function FoundationCalculator({ laborIndex = 1.0, city = "Your Area", state = "US", zipCode = "00000" }) {
  const [foundationType, setFoundationType] = useState('Slab-on-Grade');
  const [linearFeet, setLinearFeet] = useState(40);
  const [estimate, setEstimate] = useState(null);

  const problemOptions = {
    'Slab-on-Grade': 'Sinking / Settling',
    'Full Basement': 'Bowing Walls / Inward Pressure',
    'Crawlspace (Pier & Beam)': 'Sagging Floors / Wood Rot'
  };

  const handleCalculate = (e) => {
    e.preventDefault();
    let totalEstimate = 0;

    if (foundationType === 'Slab-on-Grade') {
      const pierCount = Math.floor(linearFeet / 5) + 1;
      const baseCost = pierCount * 2500;
      const plumbingTestFee = 800;
      totalEstimate = (baseCost + plumbingTestFee + FIXED_OVERHEAD) * laborIndex;
    } else if (foundationType === 'Full Basement') {
      const anchorCount = Math.floor(linearFeet / 5) + 1;
      const baseCost = anchorCount * 1200;
      totalEstimate = (baseCost + FIXED_OVERHEAD) * laborIndex;
    } else if (foundationType === 'Crawlspace (Pier & Beam)') {
      const supportCount = Math.floor(linearFeet / 8) + 1;
      const baseCost = supportCount * 1500;
      totalEstimate = (baseCost + FIXED_OVERHEAD) * laborIndex;
    }

    setEstimate({
      min: totalEstimate * 0.9,
      max: totalEstimate * 1.1
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="w-full bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden font-sans flex flex-col h-full">
      {/* Header section */}
      <div className="p-6 sm:p-8 bg-blue-50 border-b border-blue-100 flex justify-between items-start gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Repair Cost Estimator</h2>
          <p className="text-gray-600 text-sm">
            Select your issue and size to see historical pricing ranges in your area.
          </p>
        </div>
        <div className="hidden sm:block text-right">
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-100/70 rounded-lg border border-blue-200 text-blue-800 font-semibold text-xs shadow-sm shadow-blue-100/50">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {city}, {state}
          </div>
        </div>
      </div>

      <div className="p-6 sm:p-8 flex-1 flex flex-col">
        <form onSubmit={handleCalculate} className="space-y-6 flex-1 flex flex-col justify-between">
          {/* 1. Foundation Type */}
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-3">
              1. Foundation Type
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {Object.keys(problemOptions).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => {
                    setFoundationType(type);
                    setEstimate(null); // Clear previous estimate when changing type
                  }}
                  className={`px-4 py-3 rounded-lg border text-sm font-medium transition-colors
                    ${foundationType === type 
                      ? 'bg-blue-100/70 border-blue-300 text-blue-800 shadow-sm shadow-blue-100/50' 
                      : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'}`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* 2. Problem Type (Dynamic/Read-only representation) */}
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2">
              2. Typical Problem Profile
            </label>
            <div className="p-3.5 bg-gray-50 rounded-lg border border-gray-200 text-gray-700 text-sm font-medium shadow-inner">
              {problemOptions[foundationType]}
            </div>
          </div>

          {/* 3. Size of Damage */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="block text-sm font-semibold text-gray-800">
                3. Size of Damage
              </label>
              <span className="text-blue-700 font-bold bg-blue-50 px-3 py-1 rounded-full text-sm">
                {linearFeet} Linear Feet
              </span>
            </div>
            <input
              type="range"
              min="10"
              max="150"
              value={linearFeet}
              onChange={(e) => {
                setLinearFeet(Number(e.target.value));
                setEstimate(null);
              }}
              className="w-full h-2.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-2 font-medium">
              <span>10 ft</span>
              <span>150 ft</span>
            </div>
          </div>

          {/* 4. Zip Code & CTA */}
          <div className="pt-2 mt-auto">
            <label className="block text-sm font-semibold text-gray-800 mb-3">
              4. Local Estimate Generation
            </label>
            <div className="flex flex-col sm:flex-row gap-4 items-stretch">
              <div className="w-full sm:w-1/3 p-3 bg-gray-50 border border-gray-200 rounded-lg flex flex-col justify-center items-center shadow-inner relative overflow-hidden">
                <div className="absolute top-0 right-0 w-8 h-8 bg-blue-100 rounded-bl-full opacity-50"></div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">Active Region</span>
                <span className="text-xl font-black text-gray-800 tracking-widest">{zipCode}</span>
              </div>
              <button
                type="submit"
                className="w-full sm:flex-1 py-4 bg-gray-900 hover:bg-blue-900 text-white font-bold text-lg rounded-lg shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 active:shadow-md transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-900/50 flex justify-center items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 opacity-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                Calculate Local Estimate
              </button>
            </div>
          </div>
        </form>

        {/* Results UI */}
        {estimate && (
          <div className="mt-8 p-6 sm:p-7 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100 shadow-sm transition-all duration-500 ease-in-out">
            <h3 className="text-center text-sm font-bold text-blue-800 uppercase tracking-wider mb-2">
              Estimated Price Range
            </h3>
            <div className="text-center text-3xl sm:text-4xl font-extrabold text-gray-900 mb-5 tracking-tight">
              {formatCurrency(estimate.min)} <span className="text-gray-400 font-medium mx-1">-</span> {formatCurrency(estimate.max)}
            </div>
            <p className="text-[11px] sm:text-xs text-gray-500 leading-relaxed text-justify px-2 mb-6">
              <strong>Disclaimer:</strong> This is a market-based estimate aggregated from historical data. It does not constitute a formal engineering quote. Exact pricing requires an on-site inspection by a licensed structural engineer or certified contractor. Slab estimates exclude hidden sub-slab plumbing repairs.
            </p>
            
            <div className="pt-5 border-t border-blue-100/60 mt-2">
                <div className="w-full bg-gradient-to-r from-gray-400 to-gray-500 text-white font-bold py-3.5 px-4 rounded-lg shadow-md flex items-center justify-center gap-2 opacity-75">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  Quote Available Soon
                </div>
                <p className="text-[10px] text-gray-500 font-medium text-center mt-3">
                  We earn a commission if you initiate a call via this routing number.
                </p>
                <p className="text-[11px] leading-relaxed text-gray-400 mt-3 pt-3 border-t border-blue-100/40 text-center px-1 font-medium">
                  By calling this number, you will be connected to a third-party home services network that will match you with a licensed foundation repair specialist in your local area.
                </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
