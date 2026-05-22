import { useEffect, useState } from 'react';
import type { AppConfig, ChartType, SpreadResult, ButterflyResult } from './types';
import ControlPanel from './components/ControlPanel';
import ChartArea from './components/ChartArea';
import ButterflyChart from './components/charts/ButterflyChart';

const DEFAULT_FILE = '/data/hog_settlements.xlsx';

export type PageType = 'spread' | 'butterfly';

export default function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);

  // Shared
  const [activePage, setActivePage] = useState<PageType>('spread');
  const [selectedYears, setSelectedYears] = useState<number[]>(() => {
    const y = new Date().getFullYear();
    return [y - 4, y - 3, y - 2, y - 1, y];
  });
  const [dataFile, setDataFile] = useState(DEFAULT_FILE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Spread-specific
  const [near, setNear] = useState('G');
  const [selectedFar, setSelectedFar] = useState<string[]>(['J', 'K', 'M', 'N']);
  const [spreadResults, setSpreadResults] = useState<SpreadResult[] | null>(null);
  const [activeChart, setActiveChart] = useState<ChartType>('historical');

  // Butterfly-specific
  const [selectedCombos, setSelectedCombos] = useState<string[]>([]);
  const [customCombos, setCustomCombos] = useState<[string, string, string][]>([]);
  const [butterflyResults, setButterflyResults] = useState<ButterflyResult[] | null>(null);
  const [viewMode, setViewMode] = useState<'standard' | 'condensed'>('standard');
  const [upperPct, setUpperPct] = useState(75);
  const [lowerPct, setLowerPct] = useState(25);

  useEffect(() => {
    fetch('/api/config')
      .then(r => r.json())
      .then((cfg: AppConfig) => {
        setConfig(cfg);
        setSelectedFar(cfg.regularMonthSets['G'] ?? []);
      })
      .catch(e => setError(String(e)));
  }, []);

  async function handleCalculate() {
    setLoading(true);
    setError(null);
    try {
      if (activePage === 'spread') {
        const resp = await fetch('/api/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ near, years: selectedYears, dataFile }),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({}));
          throw new Error((body as { error?: string }).error ?? `HTTP ${resp.status}`);
        }
        setSpreadResults(await resp.json());
      } else {
        if (!config) return;
        const predefined = selectedCombos.map(key => config.commonButterflies[key]);
        const allCombos: [string, string, string][] = [...predefined, ...customCombos];
        if (allCombos.length === 0) {
          setError('Select at least one butterfly combo.');
          return;
        }
        const resp = await fetch('/api/butterfly', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ combos: allCombos, years: selectedYears, dataFile }),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({}));
          throw new Error((body as { error?: string }).error ?? `HTTP ${resp.status}`);
        }
        setButterflyResults(await resp.json());
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  if (!config) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50 text-gray-500">
        {error ? (
          <div className="text-center">
            <p className="text-red-600 font-medium">Failed to connect to backend.</p>
            <p className="text-sm mt-1">{error}</p>
            <p className="text-xs mt-2 text-gray-400">Is the backend running on port 3001?</p>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Loading…
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <ControlPanel
        config={config}
        activePage={activePage}
        setActivePage={setActivePage}
        near={near}
        setNear={(v) => { setNear(v); setSpreadResults(null); }}
        selectedFar={selectedFar}
        setSelectedFar={setSelectedFar}
        selectedCombos={selectedCombos}
        setSelectedCombos={setSelectedCombos}
        customCombos={customCombos}
        setCustomCombos={setCustomCombos}
        viewMode={viewMode}
        setViewMode={setViewMode}
        upperPct={upperPct}
        setUpperPct={setUpperPct}
        lowerPct={lowerPct}
        setLowerPct={setLowerPct}
        selectedYears={selectedYears}
        setSelectedYears={setSelectedYears}
        dataFile={dataFile}
        setDataFile={setDataFile}
        onCalculate={handleCalculate}
        loading={loading}
        error={error}
      />
      <div className="flex-1 overflow-y-auto">
        {activePage === 'spread' ? (
          <ChartArea
            results={spreadResults}
            near={near}
            selectedFar={selectedFar}
            activeChart={activeChart}
            setActiveChart={setActiveChart}
          />
        ) : (
          <div className="p-6">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-gray-800">Butterfly</h2>
              <p className="text-sm text-gray-500">x − 2y + z · historical comparison with {lowerPct}–{upperPct}th percentile band</p>
            </div>
            {butterflyResults ? (
              <ButterflyChart results={butterflyResults} viewMode={viewMode} upperPct={upperPct} lowerPct={lowerPct} />
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-gray-400 gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" className="w-12 h-12 text-gray-300">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5" />
                </svg>
                <p className="text-sm">Select butterfly combos and click Calculate</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
