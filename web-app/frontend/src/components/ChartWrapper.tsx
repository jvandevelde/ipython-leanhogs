import Plot from '../lib/Plot';
import { openChartInWindow } from '../lib/openInWindow';

interface Props {
  data: Plotly.Data[];
  layout: Partial<Plotly.Layout>;
  config?: Partial<Plotly.Config>;
  style?: React.CSSProperties;
  title?: string;
  label?: string;
}

export default function ChartWrapper({ data, layout, config, style, title, label }: Props) {
  const displayText = label ?? title;
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-2">
        {displayText && (
          <span className="text-base font-semibold text-gray-800 tracking-tight">{displayText}</span>
        )}
        <button
          onClick={() => openChartInWindow(data, layout, title)}
          title="Open in new window"
          className="p-1 rounded text-indigo-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors flex-shrink-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
          </svg>
        </button>
      </div>
      <Plot data={data} layout={layout} config={config} style={style ?? { width: '100%' }} />
    </div>
  );
}
