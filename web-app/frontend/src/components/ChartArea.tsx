import type { SpreadResult, ChartType } from '../types';
import HistoricalChart from './charts/HistoricalChart';
import ContinuousChart from './charts/ContinuousChart';
import MonthlyBoxplot from './charts/MonthlyBoxplot';
import WeeklyBoxplot from './charts/WeeklyBoxplot';
import IndividualChart from './charts/IndividualChart';
import { CHART_TABS } from '../lib/chartHelpers';

interface Props {
  results: SpreadResult[] | null;
  near: string;
  selectedFar: string[];
  activeChart: ChartType;
  setActiveChart: (c: ChartType) => void;
  chartHeight: number;
}

export default function ChartArea({ results, near, selectedFar, activeChart, setActiveChart, chartHeight }: Props) {
  return (
    <main className="flex-1 flex flex-col min-w-0 p-6 gap-4">
      {/* Chart type tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        {CHART_TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveChart(tab.id)}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors font-medium ${
              activeChart === tab.id
                ? 'bg-white text-indigo-700 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Chart display */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 min-h-[400px]">
        {!results ? (
          <div className="flex flex-col items-center justify-center h-80 text-gray-400 gap-2">
            <svg className="w-12 h-12 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            <p className="text-sm">Select options and click <strong>Calculate</strong> to load charts.</p>
          </div>
        ) : (
          <ChartSwitch
            results={results}
            near={`LN${near}`}
            selectedFar={selectedFar}
            activeChart={activeChart}
            chartHeight={chartHeight}
          />
        )}
      </div>
    </main>
  );
}

function ChartSwitch({ results, near, selectedFar, activeChart, chartHeight }: {
  results: SpreadResult[];
  near: string;
  selectedFar: string[];
  activeChart: ChartType;
  chartHeight: number;
}) {
  switch (activeChart) {
    case 'historical': return <HistoricalChart results={results} near={near} selectedFar={selectedFar} chartHeight={chartHeight} />;
    case 'continuous': return <ContinuousChart results={results} near={near} selectedFar={selectedFar} chartHeight={chartHeight} />;
    case 'monthly':    return <MonthlyBoxplot  results={results} near={near} selectedFar={selectedFar} chartHeight={chartHeight} />;
    case 'weekly':     return <WeeklyBoxplot   results={results} near={near} selectedFar={selectedFar} chartHeight={chartHeight} />;
    case 'individual': return <IndividualChart results={results} near={near} selectedFar={selectedFar} chartHeight={chartHeight} />;
  }
}
