import type { SpreadResult } from '../../types';
import { getCurrentYear, filterFarContracts } from '../../lib/chartHelpers';
import ChartWrapper from '../ChartWrapper';

interface Props {
  results: SpreadResult[];
  near: string;
  selectedFar: string[];
}

export default function IndividualChart({ results, near, selectedFar }: Props) {
  const filtered = filterFarContracts(results, selectedFar);
  if (filtered.length === 0) return <div className="flex items-center justify-center h-40 text-gray-400">No data.</div>;

  return (
    <div className="flex flex-col gap-8">
      {filtered.map(spread => {
        const currYear = getCurrentYear(spread.shifted);
        const allYears = Object.keys(spread.shifted).sort();
        const histYears = allYears.filter(y => y !== currYear);

        if (histYears.length === 0) return (
          <p key={spread.farContract} className="text-gray-400 text-sm">No historical years selected.</p>
        );

        const curr = spread.shifted[currYear];

        return (
          <div key={spread.farContract}>
            <h2 className="text-base font-semibold text-gray-800 tracking-tight mb-3">
              {near} − {spread.farContract} · magenta = year shown, black = {currYear}
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {histYears.map(year => {
                const hist = spread.shifted[year];
                const traces: Plotly.Data[] = [];

                if (hist) {
                  traces.push({
                    x: hist.dates, y: hist.values,
                    name: year, type: 'scatter', mode: 'lines',
                    line: { color: '#e879f9', width: 1.5 },
                  });
                }
                if (curr) {
                  traces.push({
                    x: curr.dates, y: curr.values,
                    name: currYear, type: 'scatter', mode: 'lines',
                    line: { color: 'black', width: 1.8 },
                  });
                }

                return (
                  <div key={year} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
                    <ChartWrapper
                      data={traces}
                      layout={{
                        height: 220,
                        margin: { t: 10, b: 40, l: 50, r: 20 },
                        paper_bgcolor: '#ffffff',
                        plot_bgcolor: '#fafafa',
                        showlegend: false,
                        hovermode: 'x unified',
                        xaxis: { showgrid: true, gridcolor: '#e5e7eb', type: 'date', tickformat: '%b %d' },
                        yaxis: { showgrid: true, gridcolor: '#e5e7eb', zeroline: true, zerolinecolor: '#9ca3af' },
                      }}
                      config={{ scrollZoom: true, displayModeBar: true, responsive: true }}
                      label={year}
                      title={`${near} − ${spread.farContract} · ${year}`}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
