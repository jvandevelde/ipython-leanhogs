// react-plotly.js is CJS; Vite may wrap it so the component lands at .default or .default.default
import PlotlyReact from 'react-plotly.js';

const Plot: typeof PlotlyReact =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ((PlotlyReact as any).default ?? PlotlyReact) as typeof PlotlyReact;

export default Plot;
