import express from 'express';
import cors from 'cors';
import { calculate } from './controller';
import { calculateButterfly } from './butterfly';
import { clearCache } from './dataManager';
import { DISPLAY_MONTHS, REGULAR_MONTH_SETS, COMMON_BUTTERFLIES, YEAR_MIN } from './utility';
import type { CalculateRequest, ButterflyRequest } from './types';

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/config', (_req, res) => {
  res.json({
    displayMonths: DISPLAY_MONTHS,
    regularMonthSets: REGULAR_MONTH_SETS,
    commonButterflies: COMMON_BUTTERFLIES,
    yearRange: { min: YEAR_MIN, max: new Date().getFullYear() },
  });
});

app.post('/api/calculate', (req, res) => {
  const { near, years, dataFile } = req.body as CalculateRequest;

  if (!near || !Array.isArray(years)) {
    res.status(400).json({ error: 'near (string) and years (number[]) are required' });
    return;
  }

  try {
    if (dataFile) clearCache();
    const results = calculate(`LN${near}`, years, dataFile);
    res.json(results);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error('Calculate error:', message);
    res.status(500).json({ error: message });
  }
});

app.post('/api/butterfly', (req, res) => {
  const { combos, years, dataFile } = req.body as ButterflyRequest;

  if (!Array.isArray(combos) || !Array.isArray(years)) {
    res.status(400).json({ error: 'combos (array) and years (number[]) are required' });
    return;
  }

  try {
    if (dataFile) clearCache();
    const results = calculateButterfly(combos, years, dataFile);
    res.json(results);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error('Butterfly error:', message);
    res.status(500).json({ error: message });
  }
});

const PORT = 3001;
app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
