import * as XLSX from 'xlsx';
import * as path from 'path';
import * as fs from 'fs';
import { loadData, toDateStr } from './dataManager';
import { MONTHS } from './utility';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface GapEntry {
  series: string;
  date: string;
}

export interface ActiveSeriesInfo {
  name: string;
  lastDate: string;
  expiry: string;
  gapCount: number;
}

export interface GapScanResult {
  activeSeries: ActiveSeriesInfo[];
  gaps: GapEntry[];
  dataLastDate: string;
}

export interface SuggestionResult {
  series: string;
  date: string;
  value: number | null;
  error?: string;
}

export interface EditEntry {
  series: string;
  date: string;
  value: number;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function getNthBusinessDay(year: number, month: number, n: number): Date {
  let count = 0;
  const d = new Date(year, month - 1, 1);
  while (count < n) {
    const dow = d.getDay();
    if (dow !== 0 && dow !== 6) count++;
    if (count < n) d.setDate(d.getDate() + 1);
  }
  return d;
}

function getContractExpiryDate(letter: string, year: number): Date {
  return getNthBusinessDay(year, MONTHS[letter], 10);
}

function businessDaysAfter(startStr: string, endStr: string): string[] {
  const result: string[] = [];
  const d = new Date(startStr + 'T00:00:00');
  const end = new Date(endStr + 'T00:00:00');
  d.setDate(d.getDate() + 1);
  while (d <= end) {
    const dow = d.getDay();
    if (dow !== 0 && dow !== 6) result.push(toDateStr(d));
    d.setDate(d.getDate() + 1);
  }
  return result;
}

function toBarchartSymbol(series: string): string {
  const match = series.match(/^LN([GJKMNQVZ])(\d{4})$/);
  if (!match) return '';
  return `HE${match[1]}${match[2].slice(2)}`;
}

// ── Gap Scanner ───────────────────────────────────────────────────────────────

export function getGaps(dataFile?: string): GapScanResult {
  const data = loadData(dataFile);

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const todayStr = toDateStr(today);

  let dataLastDate = '1900-01-01';
  for (const series of data.values()) {
    for (const date of series.keys()) {
      if (date > dataLastDate) dataLastDate = date;
    }
  }

  const CONTRACT_RE = /^LN([GJKMNQVZ])(\d{4})$/;
  const cutoff = new Date(today);
  cutoff.setDate(cutoff.getDate() - 60);

  const activeSeries: ActiveSeriesInfo[] = [];
  const gaps: GapEntry[] = [];

  for (const [name, series] of data.entries()) {
    const match = name.match(CONTRACT_RE);
    if (!match) continue;

    const year = parseInt(match[2]);
    const expiry = getContractExpiryDate(match[1], year);
    if (expiry < cutoff) continue;

    let lastDate = '1900-01-01';
    for (const date of series.keys()) {
      if (date > lastDate) lastDate = date;
    }

    const ceiling = expiry < today ? toDateStr(expiry) : todayStr;
    const missing = businessDaysAfter(lastDate, ceiling);

    activeSeries.push({ name, lastDate, expiry: toDateStr(expiry), gapCount: missing.length });
    for (const date of missing) gaps.push({ series: name, date });
  }

  activeSeries.sort((a, b) => a.expiry.localeCompare(b.expiry) || a.name.localeCompare(b.name));
  gaps.sort((a, b) => a.date.localeCompare(b.date) || a.series.localeCompare(b.series));

  return { activeSeries, gaps, dataLastDate };
}

// ── Barchart Suggestions ──────────────────────────────────────────────────────

interface BarchartRow { tradingDay: string; close: number }
interface BarchartResponse { status: { code: number; message: string }; results?: BarchartRow[] }

export async function fetchSuggestions(gaps: GapEntry[], apiKey: string): Promise<SuggestionResult[]> {
  const bySeries = new Map<string, { sym: string; dates: Set<string> }>();
  for (const gap of gaps) {
    const sym = toBarchartSymbol(gap.series);
    if (!sym) continue;
    if (!bySeries.has(gap.series)) bySeries.set(gap.series, { sym, dates: new Set() });
    bySeries.get(gap.series)!.dates.add(gap.date);
  }

  const results: SuggestionResult[] = [];

  for (const [series, { sym, dates }] of bySeries.entries()) {
    const sorted = [...dates].sort();
    const start = sorted[0].replace(/-/g, '');
    const end = sorted[sorted.length - 1].replace(/-/g, '');

    try {
      const url =
        `https://ondemand.websol.barchart.com/getHistory.json` +
        `?apikey=${encodeURIComponent(apiKey)}&symbol=${sym}&type=daily&startDate=${start}&endDate=${end}`;

      const resp = await fetch(url);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const json = await resp.json() as BarchartResponse;
      if (json.status.code !== 200) throw new Error(json.status.message);

      const priceByDate = new Map<string, number>();
      for (const row of json.results ?? []) priceByDate.set(row.tradingDay, row.close);

      for (const date of dates) {
        results.push({ series, date, value: priceByDate.get(date) ?? null });
      }
    } catch (e) {
      const err = e instanceof Error ? e.message : String(e);
      for (const date of dates) results.push({ series, date, value: null, error: err });
    }
  }

  return results;
}

// ── Apply Edits ───────────────────────────────────────────────────────────────

export function applyEdits(edits: EditEntry[], dataFile?: string): void {
  const filePath = dataFile
    ? path.resolve(dataFile)
    : path.resolve(__dirname, '..', '..', '..', 'hog_settlements.xlsx');

  if (!fs.existsSync(filePath)) throw new Error(`Data file not found: ${filePath}`);

  const workbook = XLSX.readFile(filePath, { cellDates: true });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];

  const rows: (string | number | null)[][] = XLSX.utils.sheet_to_json(sheet, {
    header: 1, raw: false, dateNF: 'yyyy-mm-dd',
  });

  if (rows.length === 0) throw new Error('Empty sheet');

  const header = rows[0] as string[];

  const dateToRow = new Map<string, number>();
  for (let r = 1; r < rows.length; r++) {
    const raw = rows[r][0];
    if (!raw) continue;
    const s = String(raw).trim();
    const dateStr = /^\d{4}-\d{2}-\d{2}/.test(s) ? s.slice(0, 10) : null;
    if (dateStr) dateToRow.set(dateStr, r);
  }

  const seriesToCol = new Map<string, number>();
  for (let c = 1; c < header.length; c++) {
    const h = String(header[c]).trim();
    if (h) seriesToCol.set(h, c);
  }

  for (const edit of edits) {
    let col = seriesToCol.get(edit.series);
    if (col === undefined) {
      col = header.length;
      header.push(edit.series);
      seriesToCol.set(edit.series, col);
    }

    let row = dateToRow.get(edit.date);
    if (row === undefined) {
      row = rows.length;
      const newRow: (string | number | null)[] = new Array(header.length).fill(null);
      newRow[0] = edit.date;
      rows.push(newRow);
      dateToRow.set(edit.date, row);
    }

    while (rows[row].length <= col) rows[row].push(null);
    rows[row][col] = edit.value;
  }

  const dataRows = rows.slice(1).filter(r => r[0] != null);
  dataRows.sort((a, b) => String(a[0]).localeCompare(String(b[0])));

  const newSheet = XLSX.utils.aoa_to_sheet([rows[0], ...dataRows]);
  workbook.Sheets[sheetName] = newSheet;
  XLSX.writeFile(workbook, filePath);
}
