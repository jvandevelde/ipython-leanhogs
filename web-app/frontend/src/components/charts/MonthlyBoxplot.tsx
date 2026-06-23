import type { SpreadResult } from '../../types';
import { getCurrentYear, computeMean, filterFarContracts } from '../../lib/chartHelpers';
import ChartWrapper from '../ChartWrapper';

interface Props {
  results: SpreadResult[];
  near: string;
  selectedFar: string[];
  chartHeight: number;
}

const MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

export default function MonthlyBoxplot({ results, near, selectedFar, chartHeight }: Props) {
  const filtered = filterFarContracts(results, selectedFar);
  if (filtered.length === 0) return <div className="flex items-center justify-center h-40 text-gray-400">No data.</div>;

  const today = new Date();
  const todayMonth = today.getMonth() + 1; // 1-12

  return (
    <div className="flex flex-col gap-6">
      {filtered.map(spread => {
        const currYear = getCurrentYear(spread.original);
        const allYears = Object.keys(spread.original);

        // Collect (month, value) pairs from all years' original data
        const months: number[] = [];
        const vals: number[] = [];
        for (const [, s] of Object.entries(spread.original)) {
          s.dates.forEach((d, i) => {
            const v = s.values[i];
            if (v !== null) {
              months.push(new Date(d + 'T00:00:00').getMonth() + 1);
              vals.push(v);
            }
          });
        }

        // Current year time series
        const currSeries = spread.original[currYear];
        const meanMap = computeMean(spread.original, currYear);
        const currDates = currSeries?.dates ?? [];
        const currVals = currSeries?.values ?? [];
        const meanDates = Array.from(meanMap.keys()).sort();

        // Highlight box for current month range
        const rangeShapes: Partial<Plotly.Shape>[] = [{
          type: 'rect',
          xref: 'x',
          yref: 'paper',
          x0: todayMonth - 0.5,
          x1: todayMonth + 0.5,
          y0: 0, y1: 1,
          fillcolor: 'rgba(199,210,254,0.35)',
          line: { width: 0 },
          layer: 'below',
        }];

        const topTraces: Plotly.Data[] = [
          {
            type: 'box',
            x: months.map(m => MONTH_NAMES[m - 1]),
            y: vals,
            name: 'Spread',
            boxpoints: 'all',
            jitter: 0.4,
            pointpos: 0,
            marker: { color: 'rgba(99,102,241,0.25)', size: 4 },
            line: { color: '#6366f1' },
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

        // current-month vrect for bottom chart — use date shapes
        const bottomShapes: Partial<Plotly.Shape>[] = [];
        if (currDates.length > 0) {
          const refYear = new Date(currDates[0] + 'T00:00:00').getFullYear();
          const m0 = new Date(refYear, todayMonth - 1, 1).toISOString().slice(0, 10);
          const daysInMonth = new Date(refYear, todayMonth, 0).getDate();
          const m1 = new Date(refYear, todayMonth - 1, daysInMonth - 1).toISOString().slice(0, 10);
          bottomShapes.push({
            type: 'rect', xref: 'x', yref: 'paper',
            x0: m0, x1: m1, y0: 0, y1: 1,
            fillcolor: 'rgba(199,210,254,0.35)',
            line: { width: 0 }, layer: 'below',
          });
        }

        const totalYears = allYears.length;
        const subtitle = `${near} − ${spread.farContract} · ${totalYears} years`;

        return (
          <div key={spread.farContract} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <h3 className="text-base font-semibold text-gray-800 tracking-tight mb-3">{subtitle}</h3>
            <ChartWrapper
              data={topTraces}
              layout={{
                height: chartHeight,
                margin: { t: 10, b: 40, l: 55, r: 10 },
                shapes: rangeShapes,
                xaxis: { categoryorder: 'array', categoryarray: MONTH_NAMES, showgrid: false },
                yaxis: { showgrid: true, gridcolor: '#e5e7eb', zeroline: true, zerolinecolor: '#9ca3af' },
                paper_bgcolor: '#ffffff', plot_bgcolor: '#fafafa',
                hovermode: 'closest',
              }}
              config={{ scrollZoom: true, displayModeBar: false, responsive: true }}
              label="Boxplot"
              title={`${subtitle} — Monthly Boxplot`}
            />
            <ChartWrapper
              data={bottomTraces}
              layout={{
                height: Math.round(chartHeight * 0.77),
                margin: { t: 10, b: 40, l: 55, r: 10 },
                shapes: bottomShapes,
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
