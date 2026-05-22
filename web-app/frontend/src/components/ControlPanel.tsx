import { useRef, useEffect, useState } from 'react';
import type { AppConfig } from '../types';
import type { PageType } from '../App';

interface Props {
  config: AppConfig;
  activePage: PageType;
  setActivePage: (v: PageType) => void;
  near: string;
  setNear: (v: string) => void;
  selectedFar: string[];
  setSelectedFar: (v: string[]) => void;
  selectedCombos: string[];
  setSelectedCombos: (v: string[]) => void;
  customCombos: [string, string, string][];
  setCustomCombos: (v: [string, string, string][]) => void;
  viewMode: 'standard' | 'condensed';
  setViewMode: (v: 'standard' | 'condensed') => void;
  upperPct: number;
  setUpperPct: (v: number) => void;
  lowerPct: number;
  setLowerPct: (v: number) => void;
  selectedYears: number[];
  setSelectedYears: (v: number[]) => void;
  dataFile: string;
  setDataFile: (v: string) => void;
  onCalculate: () => void;
  loading: boolean;
  error: string | null;
}

const CONTRACT_LETTERS = ['G', 'J', 'K', 'M', 'N', 'Q', 'V', 'Z'];

export default function ControlPanel({
  config, activePage, setActivePage,
  near, setNear, selectedFar, setSelectedFar,
  selectedCombos, setSelectedCombos, customCombos, setCustomCombos,
  viewMode, setViewMode, upperPct, setUpperPct, lowerPct, setLowerPct,
  selectedYears, setSelectedYears,
  dataFile, setDataFile,
  onCalculate, loading, error,
}: Props) {
  const farRef = useRef<HTMLSelectElement>(null);
  const yearRef = useRef<HTMLSelectElement>(null);
  const [customLegs, setCustomLegs] = useState<[string, string, string]>(['G', 'J', 'K']);
  const [toast, setToast] = useState<string | null>(null);

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(null), 2500);
  }

  useEffect(() => {
    if (!farRef.current) return;
    Array.from(farRef.current.options).forEach(o => { o.selected = selectedFar.includes(o.value); });
  }, [selectedFar]);

  useEffect(() => {
    if (!yearRef.current) return;
    Array.from(yearRef.current.options).forEach(o => { o.selected = selectedYears.includes(Number(o.value)); });
  }, [selectedYears]);

  function handleNearChange(v: string) {
    setNear(v);
    setSelectedFar(config.regularMonthSets[v] ?? []);
  }

  function handleFarChange() {
    if (!farRef.current) return;
    setSelectedFar(Array.from(farRef.current.selectedOptions).map(o => o.value));
  }

  function handleYearChange() {
    if (!yearRef.current) return;
    setSelectedYears(Array.from(yearRef.current.selectedOptions).map(o => Number(o.value)));
  }

  function selectYears(n: number) {
    const max = config.yearRange.max;
    setSelectedYears(Array.from({ length: n }, (_, i) => max - i).reverse());
  }

  function toggleCombo(key: string) {
    setSelectedCombos(
      selectedCombos.includes(key)
        ? selectedCombos.filter(k => k !== key)
        : [...selectedCombos, key],
    );
  }

  function addCustomCombo() {
    const key = customLegs.join('');
    const isPredefined = key in config.commonButterflies;

    if (isPredefined) {
      if (selectedCombos.includes(key)) {
        showToast(`${key} is already selected`);
      } else {
        setSelectedCombos([...selectedCombos, key]);
      }
      return;
    }

    if (customCombos.some(c => c.join('') === key)) {
      showToast(`${key} is already added`);
      return;
    }

    setCustomCombos([...customCombos, [...customLegs] as [string, string, string]]);
  }

  function removeCustomCombo(key: string) {
    setCustomCombos(customCombos.filter(c => c.join('') !== key));
  }

  const allYears: number[] = [];
  for (let y = config.yearRange.max; y >= config.yearRange.min; y--) allYears.push(y);

  return (
    <aside className="w-72 shrink-0 flex flex-col h-screen bg-gray-50 border-r border-gray-200">
      {/* Sticky top: title + file + page toggle */}
      <div className="flex flex-col gap-3 p-4 border-b border-gray-200">
        <div>
          <h1 className="text-base font-semibold text-gray-800 leading-tight mb-2">Lean Hogs</h1>
          <input
            type="text"
            value={dataFile}
            onChange={e => setDataFile(e.target.value)}
            className="w-full text-xs border border-gray-300 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400 font-mono"
          />
        </div>
        <div className="flex rounded-lg border border-gray-200 overflow-hidden text-sm font-medium">
          <button
            onClick={() => setActivePage('spread')}
            className={`flex-1 py-1.5 transition-colors ${activePage === 'spread' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
          >
            Spreads
          </button>
          <button
            onClick={() => setActivePage('butterfly')}
            className={`flex-1 py-1.5 transition-colors ${activePage === 'butterfly' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
          >
            Butterfly
          </button>
        </div>
      </div>

      {/* Scrollable middle */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-4 p-4">

      {/* ── Spread-specific controls ── */}
      {activePage === 'spread' && (
        <>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">Near Contract</label>
            <select
              value={near}
              onChange={e => handleNearChange(e.target.value)}
              className="text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {Object.entries(config.displayMonths).map(([letter, label]) => (
                <option key={letter} value={letter}>{label}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              Far Contracts <span className="text-gray-400 normal-case">(ctrl+click)</span>
            </label>
            <select
              ref={farRef}
              multiple
              onChange={handleFarChange}
              size={5}
              className="text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {(config.regularMonthSets[near] ?? []).map(letter => (
                <option key={letter} value={letter}>{config.displayMonths[letter] ?? letter}</option>
              ))}
            </select>
          </div>
        </>
      )}

      {/* ── Butterfly-specific controls ── */}
      {activePage === 'butterfly' && (
        <div className="flex flex-col gap-3">
          {/* Predefined combos */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">Combos</label>
              <div className="flex gap-1">
                <button onClick={() => setSelectedCombos(Object.keys(config.commonButterflies))}
                  className="text-xs text-indigo-500 hover:text-indigo-700">All</button>
                <span className="text-gray-300 text-xs">·</span>
                <button onClick={() => setSelectedCombos([])}
                  className="text-xs text-indigo-500 hover:text-indigo-700">None</button>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-1">
              {Object.keys(config.commonButterflies).map(key => (
                <button
                  key={key}
                  onClick={() => toggleCombo(key)}
                  className={`text-xs py-1 rounded border transition-colors font-mono ${
                    selectedCombos.includes(key)
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-indigo-400'
                  }`}
                >
                  {key}
                </button>
              ))}
            </div>
          </div>

          {/* Custom combo */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">Custom</label>
            <div className="flex gap-1 items-center">
              {([0, 1, 2] as const).map(i => (
                <select
                  key={i}
                  value={customLegs[i]}
                  onChange={e => {
                    const next: [string, string, string] = [...customLegs] as [string, string, string];
                    next[i] = e.target.value;
                    setCustomLegs(next);
                  }}
                  className="flex-1 text-xs border border-gray-300 rounded px-1 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-indigo-400 font-mono"
                >
                  {CONTRACT_LETTERS.map(l => <option key={l} value={l}>{l}</option>)}
                </select>
              ))}
              <button
                onClick={addCustomCombo}
                className="text-xs px-2 py-1 rounded bg-indigo-50 border border-indigo-300 text-indigo-600 hover:bg-indigo-100 transition-colors"
              >
                Add
              </button>
            </div>
            {customCombos.length > 0 && (
              <div className="flex flex-col gap-0.5 mt-1">
                {customCombos.map(c => {
                  const key = c.join('');
                  return (
                    <div key={key} className="flex items-center justify-between px-2 py-0.5 rounded bg-indigo-50 border border-indigo-200">
                      <span className="text-xs font-mono text-indigo-700">{key}</span>
                      <button onClick={() => removeCustomCombo(key)} className="text-indigo-400 hover:text-red-500 transition-colors text-xs">✕</button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Toast */}
          {toast && (
            <div className="text-xs text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md px-3 py-1.5 text-center">
              {toast}
            </div>
          )}

          {/* View mode */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">View</label>
            <div className="flex rounded-lg border border-gray-200 overflow-hidden text-xs font-medium">
              <button
                onClick={() => setViewMode('standard')}
                className={`flex-1 py-1.5 transition-colors ${viewMode === 'standard' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
              >
                Standard
              </button>
              <button
                onClick={() => setViewMode('condensed')}
                className={`flex-1 py-1.5 transition-colors ${viewMode === 'condensed' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
              >
                Condensed
              </button>
            </div>
          </div>

          {/* Percentile band */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">Percentile Band</label>
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-12">Upper</span>
                <input
                  type="range" min={51} max={99} value={upperPct}
                  onChange={e => setUpperPct(Number(e.target.value))}
                  className="flex-1 accent-indigo-600"
                />
                <span className="text-xs font-mono text-gray-700 w-8 text-right">{upperPct}%</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-12">Lower</span>
                <input
                  type="range" min={1} max={49} value={lowerPct}
                  onChange={e => setLowerPct(Number(e.target.value))}
                  className="flex-1 accent-indigo-600"
                />
                <span className="text-xs font-mono text-gray-700 w-8 text-right">{lowerPct}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Years — shared */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">Years</label>
        <div className="flex gap-1 mb-1">
          {([5, 9, 15] as const).map(n => (
            <button key={n} onClick={() => selectYears(n)}
              className="flex-1 text-xs py-1 rounded border border-gray-300 hover:border-indigo-400 hover:text-indigo-600 bg-white transition-colors">
              {n} Yrs
            </button>
          ))}
        </div>
        <select
          ref={yearRef}
          multiple
          onChange={handleYearChange}
          size={10}
          className="text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          {allYears.map(y => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      </div>{/* end scrollable middle */}

      {/* Pinned bottom: calculate + error */}
      <div className="flex flex-col gap-2 p-4 border-t border-gray-200">
        <button
          onClick={onCalculate}
          disabled={loading}
          className="w-full py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
        >
          {loading ? 'Calculating…' : 'Calculate'}
        </button>
        {error && (
          <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-md p-2 break-all">{error}</p>
        )}
      </div>
    </aside>
  );
}
