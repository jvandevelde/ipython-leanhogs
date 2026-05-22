export function openChartInWindow(
  data: Plotly.Data[],
  layout: Partial<Plotly.Layout>,
  title = 'Chart',
) {
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>${title}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #fff; }
    #chart { width: 100vw; height: 100vh; }
  </style>
</head>
<body>
  <div id="chart"></div>
  <script>
    Plotly.newPlot(
      'chart',
      ${JSON.stringify(data)},
      ${JSON.stringify({ ...layout, autosize: true })},
      { scrollZoom: true, responsive: true, displayModeBar: true }
    );
  </script>
</body>
</html>`;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const win = window.open(url, '_blank', 'width=1280,height=750');
  // revoke after the window has had time to load
  if (win) setTimeout(() => URL.revokeObjectURL(url), 10000);
}
