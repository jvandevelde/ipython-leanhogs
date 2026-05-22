import type { SpreadResult } from '../../types';
import { getCurrentYear, computeMean, getISOWeek, filterFarContracts } from '../../lib/chartHelpers';
import ChartWrapper from '../ChartWrapper';

interface Props {
  results: SpreadResult[];
  near: string;
  selectedFar: string[];
}

function getCurrentISOWeek(): number {
  const now = new Date();
  const jan4 = new Date(now.getFullYear(), 0, 4);
  const startOfWeek1 = new Date(jan4);
  startOfWeek1.setDate(jan4.getDate() - ((jan4.getDay() + 6) % 7));
  return Math.floor((now.getTime() - startOfWeek1.getTime()) / (7 * 86400000)) + 1;
}

export default function WeeklyBoxplot({ results, near, selectedFar }: Props) {
  const filtered = filterFarContracts(results, selectedFar);
  if (filtered.length === 0) return <div className="flex items-center justify-center h-40 text-gray-400">No data.</div>;

  const currentWeek = getCurrentISOWeek();

  return (
    <div className="flex flex-col gap-6">
      {filtered.map(spread => {
        const currYear = getCurrentYear(spread.original);
        const allYears = Object.keys(spread.original);

        // (week, value) pairs across all years
        const weeks: number[] = [];
        const vals: number[] = [];
        for (const [, s] of Object.entries(spread.original)) {
          s.dates.forEach((d, i) => {
            const v = s.values[i];
            if (v !== null) {
              weeks.push(getISOWeek(d));
              vals.push(v);
            }
          });
        }

        const currSeries = spread.original[currYear];
        const meanMap = computeMean(spread.original, currYear);
        const currDates = currSeries?.dates ?? [];
        const currVals = currSeries?.values ?? [];
        const meanDates = Array.from(meanMap.keys()).sort();

        const topTraces: Plotly.Data[] = [
          {
            type: 'box',
            x: weeks,
            y: vals,
            name: 'Spread',
            boxpoints: 'all',
            jitter: 0.3,
            pointpos: 0,
            marker: { color: 'rgba(16,185,129,0.25)', size: 3 },
            line: { color: '#10b981' },
            fillcolor: 'white',
            showlegend: false,
          },
        ];

        const bottomTraces: Plotly.Data[] = [
          {
            x: currDates,
            y: currVals,
            name: `${currYear} (curr)`,
            type: 'scatter',
            mode: 'lines',
            line: { color: 'black', width: 2 },
          },
          {
            x: meanDates,
            y: meanDates.map(d => meanMap.get(d) ?? null),
            name: 'AVG',
            type: 'scatter',
            mode: 'lines',
            line: { color: 'red', width: 1.5, dash: 'dash' },
          },
        ];

        const topShapes: Partial<Plotly.Shape>[] = [{
          type: 'rect', xref: 'x', yref: 'paper',
          x0: currentWeek - 0.5, x1: currentWeek + 0.5,
          y0: 0, y1: 1,
          fillcolor: 'rgba(167,243,208,0.4)',
          line: { width: 0 }, layer: 'below',
        }];

        const subtitle = `${near} − ${spread.farContract} · ${allYears.length} years`;

        return (
          <div key={spread.farContract} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <h3 className="text-base font-semibold text-gray-800 tracking-tight mb-3">{subtitle}</h3>
            <ChartWrapper
              data={topTraces}
              layout={{
                height: 260,
                margin: { t: 10, b: 40, l: 55, r: 10 },
                shapes: topShapes,
                xaxis: { showgrid: false, title: { text: 'ISO Week' } },
                yaxis: { showgrid: true, gridcolor: '#e5e7eb', zeroline: true, zerolinecolor: '#9ca3af' },
                paper_bgcolor: '#ffffff', plot_bgcolor: '#fafafa',
                hovermode: 'closest',
              }}
              config={{ scrollZoom: true, displayModeBar: false, responsive: true }}
              label="Boxplot"
              title={`${subtitle} — Weekly Boxplot`}
            />
            <ChartWrapper
              data={bottomTraces}
              layout={{
                height: 200,
                margin: { t: 10, b: 40, l: 55, r: 10 },
                xaxis: { showgrid: true, gridcolor: '#e5e7eb', type: 'date' },
                yaxis: { showgrid: true, gridcolor: '#e5e7eb', zeroline: true, zerolinecolor: '#9ca3af' },
                paper_bgcolor: '#ffffff', plot_bgcolor: '#fafafa',
                hovermode: 'x unified',
                legend: { orientation: 'h', y: -0.2 },
              }}
              config={{ scrollZoom: true, displayModeBar: false, responsive: true }}
              label="Seasonal"
              title={`${subtitle} — Seasonal Series`}
            />
          </div>
        );
      })}
    </div>
  );
}
