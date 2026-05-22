import type { ButterflyResult } from '../../types';
import { getCurrentYear, computeMean, computePercentile, YEAR_COLORS } from '../../lib/chartHelpers';
import ChartWrapper from '../ChartWrapper';

interface Props {
  results: ButterflyResult[];
  viewMode: 'standard' | 'condensed';
  upperPct: number;
  lowerPct: number;
}

export default function ButterflyChart({ results, viewMode, upperPct, lowerPct }: Props) {
  if (results.length === 0) {
    return <div className="flex items-center justify-center h-40 text-gray-400">No data — select combos and calculate.</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      {results.map(spread => {
        const currYear = getCurrentYear(spread.shifted);
        const allYears = Object.keys(spread.shifted).sort();
        const histYears = allYears.filter(y => y !== currYear);

        const meanHigh = computePercentile(spread.shifted, upperPct, currYear);
        const meanLow  = computePercentile(spread.shifted, lowerPct, currYear);
        const meanLine = computeMean(spread.shifted, currYear);

        const traces: Plotly.Data[] = [];

        // Percentile band — yellow in condensed (prominent), gray in standard (subtle)
        const bandDates = Array.from(meanHigh.keys()).sort();
        traces.push({
          x: [...bandDates, ...bandDates.slice().reverse()],
          y: [
            ...bandDates.map(d => meanHigh.get(d) ?? null),
            ...bandDates.slice().reverse().map(d => meanLow.get(d) ?? null),
          ],
          fill: 'toself',
          fillcolor: viewMode === 'condensed' ? 'rgba(250,204,21,0.35)' : 'rgba(200,210,220,0.4)',
          line: { width: 0 },
          showlegend: false,
          hoverinfo: 'skip',
          type: 'scatter',
        });

        // Invisible bound traces for hover tooltip (both modes)
        {
          traces.push({
            x: bandDates,
            y: bandDates.map(d => meanHigh.get(d) ?? null),
            name: `P${upperPct}`,
            type: 'scatter',
            mode: 'lines',
            line: { width: 0, color: 'transparent' },
            showlegend: false,
            hovertemplate: `P${upperPct}: %{y:.3f}<extra></extra>`,
          });
          traces.push({
            x: bandDates,
            y: bandDates.map(d => meanLow.get(d) ?? null),
            name: `P${lowerPct}`,
            type: 'scatter',
            mode: 'lines',
            line: { width: 0, color: 'transparent' },
            showlegend: false,
            hovertemplate: `P${lowerPct}: %{y:.3f}<extra></extra>`,
          });
        }

        // Historical year lines — only in standard mode
        if (viewMode === 'standard') {
          histYears.forEach((year, yi) => {
            const s = spread.shifted[year];
            traces.push({
              x: s.dates, y: s.values,
              name: year, type: 'scatter', mode: 'lines',
              line: { color: YEAR_COLORS[yi % YEAR_COLORS.length], width: 1 },
            });
          });
        }

        // Mean line
        const meanDates = Array.from(meanLine.keys()).sort();
        traces.push({
          x: meanDates,
          y: meanDates.map(d => meanLine.get(d) ?? null),
          name: 'AVG', type: 'scatter', mode: 'lines',
          line: { color: 'red', width: 2, dash: 'dash' },
        });

        // Current year
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

        const [l1, l2, l3] = spread.legs;
        const title = `${spread.label} · ${l1} − 2×${l2} + ${l3}`;

        return (
          <div key={spread.label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <ChartWrapper
              data={traces}
              layout={{
                height: 440,
                margin: { t: 10, b: 40, l: 60, r: 20 },
                hovermode: 'x unified',
                legend: { orientation: 'h', y: -0.15, x: 0 },
                paper_bgcolor: '#ffffff',
                plot_bgcolor: '#fafafa',
                xaxis: { showgrid: true, gridcolor: '#e5e7eb', type: 'date', tickformat: '%b %d' },
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
