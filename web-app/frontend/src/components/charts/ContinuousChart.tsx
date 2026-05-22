import type { SpreadResult } from '../../types';
import { getCurrentYear, rollingMean, YEAR_COLORS, filterFarContracts } from '../../lib/chartHelpers';
import ChartWrapper from '../ChartWrapper';

interface Props {
  results: SpreadResult[];
  near: string;
  selectedFar: string[];
}

export default function ContinuousChart({ results, near, selectedFar }: Props) {
  const filtered = filterFarContracts(results, selectedFar);
  if (filtered.length === 0) return <div className="flex items-center justify-center h-40 text-gray-400">No data.</div>;

  return (
    <div className="flex flex-col gap-6">
      {filtered.map(spread => {
        const currYear = getCurrentYear(spread.original);
        const allYears = Object.keys(spread.original).sort();
        const histYears = allYears.filter(y => y !== currYear);

        const traces: Plotly.Data[] = [];

        histYears.forEach((year, yi) => {
          const s = spread.original[year];
          const smooth = rollingMean(s.values);
          traces.push({
            x: s.dates, y: smooth,
            name: year, type: 'scatter', mode: 'lines',
            line: { color: YEAR_COLORS[yi % YEAR_COLORS.length], width: 1 },
            legendgroup: year,
          });
        });

        const curr = spread.original[currYear];
        if (curr) {
          const smooth = rollingMean(curr.values);
          traces.push({
            x: curr.dates, y: smooth,
            name: `${currYear} (curr)`, type: 'scatter', mode: 'lines',
            line: { color: 'black', width: 2.5 },
            legendgroup: currYear,
          });
        }

        const title = `${near} − ${spread.farContract} (7-day avg)`;
        return (
          <div key={spread.farContract} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <ChartWrapper
              data={traces}
              layout={{
                height: 280,
                margin: { t: 10, b: 40, l: 60, r: 20 },
                hovermode: 'x unified',
                legend: { orientation: 'h', y: -0.15, x: 0 },
                paper_bgcolor: '#ffffff',
                plot_bgcolor: '#fafafa',
                xaxis: { showgrid: true, gridcolor: '#e5e7eb', type: 'date' },
                yaxis: { showgrid: true, gridcolor: '#e5e7eb', zeroline: true, zerolinecolor: '#9ca3af' },
              }}
              config={{ scrollZoom: true, displayModeBar: true, responsive: true }}
              title={title}
            />
          </div>
        );
      })}
    </div>
  );
}
