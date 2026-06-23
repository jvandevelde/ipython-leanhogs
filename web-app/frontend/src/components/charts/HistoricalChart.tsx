import type { SpreadResult } from '../../types';
import { getCurrentYear, computeMean, computePercentile, YEAR_COLORS, filterFarContracts } from '../../lib/chartHelpers';
import ChartWrapper from '../ChartWrapper';

interface Props {
  results: SpreadResult[];
  near: string;
  selectedFar: string[];
  chartHeight: number;
}

export default function HistoricalChart({ results, near, selectedFar, chartHeight }: Props) {
  const filtered = filterFarContracts(results, selectedFar);
  if (filtered.length === 0) return <Empty />;

  return (
    <div className="flex flex-col gap-6">
      {filtered.map(spread => {
        const currYear = getCurrentYear(spread.shifted);
        const allYears = Object.keys(spread.shifted).sort();
        const histYears = allYears.filter(y => y !== currYear);

        const mean75 = computePercentile(spread.shifted, 75, currYear);
        const mean25 = computePercentile(spread.shifted, 25, currYear);
        const meanLine = computeMean(spread.shifted, currYear);

        const traces: Plotly.Data[] = [];

        const bandDates = Array.from(mean75.keys()).sort();
        traces.push({
          x: [...bandDates, ...bandDates.slice().reverse()],
          y: [...bandDates.map(d => mean75.get(d) ?? null), ...bandDates.slice().reverse().map(d => mean25.get(d) ?? null)],
          fill: 'toself',
          fillcolor: 'rgba(200,210,220,0.4)',
          line: { width: 0 },
          showlegend: false,
          hoverinfo: 'skip',
          type: 'scatter',
        });

        histYears.forEach((year, yi) => {
          const s = spread.shifted[year];
          traces.push({
            x: s.dates, y: s.values,
            name: year, type: 'scatter', mode: 'lines',
            line: { color: YEAR_COLORS[yi % YEAR_COLORS.length], width: 1 },
          });
        });

        const meanDates = Array.from(meanLine.keys()).sort();
        traces.push({
          x: meanDates,
          y: meanDates.map(d => meanLine.get(d) ?? null),
          name: 'AVG', type: 'scatter', mode: 'lines',
          line: { color: 'red', width: 2, dash: 'dash' },
        });

        const curr = spread.shifted[currYear];
        if (curr) {
          const lastIdx = [...curr.values].reverse().findIndex(v => v !== null);
          const lastValidIdx = lastIdx >= 0 ? curr.values.length - 1 - lastIdx : -1;
          traces.push({
            x: curr.dates, y: curr.values,
            name: `${currYear} (curr)`, type: 'scatter', mode: 'lines',
            line: { color: 'black', width: 2.5 },
          });
          if (lastValidIdx >= 0) {
            traces.push({
              x: [curr.dates[lastValidIdx]],
              y: [curr.values[lastValidIdx]],
              mode: 'markers',
              marker: { color: '#4f46e5', size: 8 },
              showlegend: false,
              hoverinfo: 'skip',
              type: 'scatter',
            });
          }
        }

        const title = `${near} − ${spread.farContract}`;
        return (
          <div key={spread.farContract} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <ChartWrapper
              data={traces}
              layout={{
                height: chartHeight,
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

export function buildSubplotLayout(
  n: number,
  annotations: Partial<Plotly.Annotations>[],
  rowHeight: number,
): Partial<Plotly.Layout> {
  const layout: Partial<Plotly.Layout> & Record<string, unknown> = {
    height: n * rowHeight + 60,
    margin: { t: 40, b: 40, l: 60, r: 20 },
    hovermode: 'x unified',
    legend: { orientation: 'h', y: -0.08, x: 0 },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#fafafa',
    annotations,
  };

  for (let i = 0; i < n; i++) {
    const suffix = i === 0 ? '' : String(i + 1);
    const domainStart = 1 - (i + 1) / n;
    const domainEnd = 1 - i / n;
    const gap = 0.06;
    layout[`xaxis${suffix}`] = { domain: [0, 1], anchor: `y${suffix}`, showgrid: true, gridcolor: '#e5e7eb', type: 'date' };
    layout[`yaxis${suffix}`] = { domain: [domainStart + gap / 2, domainEnd - gap / 2], anchor: `x${suffix}`, showgrid: true, gridcolor: '#e5e7eb', zeroline: true, zerolinecolor: '#9ca3af' };
  }

  return layout as Partial<Plotly.Layout>;
}

function Empty() {
  return <div className="flex items-center justify-center h-40 text-gray-400">No data — select far contracts and calculate.</div>;
}
