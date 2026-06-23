import express from 'express';
import cors from 'cors';
import { calculate } from './controller';
import { calculateButterfly } from './butterfly';
import { clearCache } from './dataManager';
import { DISPLAY_MONTHS, REGULAR_MONTH_SETS, COMMON_BUTTERFLIES, YEAR_MIN } from './utility';
import { getGaps, fetchSuggestions, applyEdits } from './dataEditor';
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

app.get('/api/data/gaps', (req, res) => {
  const dataFile = req.query.dataFile as string | undefined;
  try {
    if (dataFile) clearCache();
    const result = getGaps(dataFile);
    res.json(result);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error('Gap scan error:', message);
    res.status(500).json({ error: message });
  }
});

app.post('/api/data/suggestions', async (req, res) => {
  const { gaps, apiKey } = req.body as { gaps: { series: string; date: string }[]; apiKey: string };
  if (!Array.isArray(gaps) || !apiKey) {
    res.status(400).json({ error: 'gaps (array) and apiKey (string) are required' });
    return;
  }
  try {
    const results = await fetchSuggestions(gaps, apiKey);
    res.json(results);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error('Suggestions error:', message);
    res.status(500).json({ error: message });
  }
});

app.post('/api/data/apply', (req, res) => {
  const { edits, dataFile } = req.body as { edits: { series: string; date: string; value: number }[]; dataFile?: string };
  if (!Array.isArray(edits)) {
    res.status(400).json({ error: 'edits (array) is required' });
    return;
  }
  try {
    applyEdits(edits, dataFile);
    clearCache();
    res.json({ saved: edits.length });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error('Apply edits error:', message);
    res.status(500).json({ error: message });
  }
});

const PORT = 3001;
app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
