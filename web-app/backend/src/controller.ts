import { MONTHS, REGULAR_MONTH_SETS } from './utility';
import { loadData, toDateStr, RawData } from './dataManager';
import { SpreadResult, SeriesData } from './types';

// ── Date helpers ─────────────────────────────────────────────────────────────

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

function getContractStartDate(letter: string, year: number): Date {
  const expiry = getContractExpiryDate(letter, year);
  const start = new Date(expiry);
  start.setFullYear(start.getFullYear() - 1);
  return start;
}

function daysBetween(a: Date, b: Date): number {
  return Math.round((a.getTime() - b.getTime()) / 86400000);
}

function addDays(dateStr: string, days: number): string {
  const d = new Date(dateStr + 'T00:00:00');
  d.setDate(d.getDate() + days);
  return toDateStr(d);
}

function dateRange(start: Date, end: Date): string[] {
  const dates: string[] = [];
  const d = new Date(start);
  d.setHours(0, 0, 0, 0);
  const endMs = new Date(end).setHours(0, 0, 0, 0);
  while (d.getTime() <= endMs) {
    dates.push(toDateStr(d));
    d.setDate(d.getDate() + 1);
  }
  return dates;
}

// ── Contract data extraction ──────────────────────────────────────────────────

function forwardFill(values: (number | null)[], maxGap = 3): (number | null)[] {
  let last: number | null = null;
  let gap = 0;
  return values.map(v => {
    if (v !== null) { last = v; gap = 0; return v; }
    if (last !== null && gap < maxGap) { gap++; return last; }
    return null;
  });
}

interface ContractSeries {
  dates: string[];
  values: (number | null)[];
  byDate: Map<string, number | null>;
}

function getContractData(raw: RawData, contractName: string, year: number): ContractSeries | null {
  const colName = `${contractName}${year}`;
  const series = raw.get(colName);
  if (!series || series.size === 0) return null;

  const sortedDates = Array.from(series.keys()).sort();
  const firstDate = sortedDates[0];
  const lastDate = sortedDates[sortedDates.length - 1];

  const allDates = dateRange(new Date(firstDate + 'T00:00:00'), new Date(lastDate + 'T00:00:00'));
  const rawValues: (number | null)[] = allDates.map(d => series.get(d) ?? null);
  const filled = forwardFill(rawValues);

  const byDate = new Map<string, number | null>();
  allDates.forEach((d, i) => byDate.set(d, filled[i]));

  return { dates: allDates, values: filled, byDate };
}

// ── Main calculate ────────────────────────────────────────────────────────────

export function calculate(near: string, requestedYears: number[], dataFile?: string): SpreadResult[] {
  const raw = loadData(dataFile);
  const nearLetter = near[2]; // e.g. "LNG" -> "G"
  const today = new Date();
  const currentYear = today.getFullYear();

  // Auto-append current and next year (mirrors Python's get_active_years)
  const allYears = Array.from(new Set([...requestedYears, currentYear, currentYear + 1])).sort();

  const farLetters = REGULAR_MONTH_SETS[nearLetter];
  const graphStart = getContractStartDate(nearLetter, currentYear);

  const results: SpreadResult[] = [];

  for (const farLetter of farLetters) {
    const farContract = `LN${farLetter}`;
    const shiftedByYear: Record<string, SeriesData> = {};
    const originalByYear: Record<string, SeriesData> = {};

    for (const year of allYears) {
      const nearData = getContractData(raw, near, year);

      // Year-rollover correction: late-year near + early-year far → use year+1 for far
      const LATE_YEAR_NEAR = ['N', 'Q', 'V', 'Z'];
      const EARLY_YEAR_FAR = ['G', 'J', 'K', 'M'];
      const farYear = (LATE_YEAR_NEAR.includes(nearLetter) && EARLY_YEAR_FAR.includes(farLetter) && year <= currentYear)
        ? year + 1
        : year;

      const farData = getContractData(raw, farContract, farYear);

      if (!nearData || !farData) continue;

      // Compute spread on dates where both have values
      const diffByDate = new Map<string, number>();
      for (const d of nearData.dates) {
        const nv = nearData.byDate.get(d);
        const fv = farData.byDate.get(d);
        if (nv != null && fv != null) {
          diffByDate.set(d, nv - fv);
        }
      }

      if (diffByDate.size === 0) continue;

      const diffDates = Array.from(diffByDate.keys()).sort();
      const diffStart = new Date(diffDates[0] + 'T00:00:00');
      const diffEnd = new Date(diffDates[diffDates.length - 1] + 'T00:00:00');

      // Reindex to full range (contract start→end for this year)
      const contractStart = getContractStartDate(nearLetter, year);
      const contractEnd = getContractExpiryDate(nearLetter, year);
      const fullRange = dateRange(contractStart > diffStart ? contractStart : diffStart,
                                  contractEnd < diffEnd ? contractEnd : diffEnd);

      const reindexed = fullRange.map(d => diffByDate.get(d) ?? null);
      const allNull = reindexed.every(v => v === null);
      if (allNull) continue;

      // Store original dates
      const origDates: string[] = [];
      const origValues: (number | null)[] = [];
      fullRange.forEach((d, i) => {
        if (reindexed[i] !== null) { origDates.push(d); origValues.push(reindexed[i]); }
      });
      originalByYear[String(year)] = { dates: origDates, values: origValues };

      // Shift: datetime(year, graphStart.month, graphStart.day) → graphStart.
      // All years land in the same ~1-year window (≈ graphStart - 1yr to graphStart).
      const anchor = new Date(year, graphStart.getMonth(), graphStart.getDate());
      const daysToShift = daysBetween(anchor, graphStart);
      const shiftAmount = -daysToShift;

      const shiftedDates: string[] = [];
      const shiftedValues: number[] = [];
      fullRange.forEach((d, i) => {
        const v = reindexed[i];
        if (v === null) return;
        shiftedDates.push(addDays(d, shiftAmount));
        shiftedValues.push(v);
      });

      if (shiftedDates.length === 0) continue;
      shiftedByYear[String(year)] = { dates: shiftedDates, values: shiftedValues };
    }

    if (Object.keys(shiftedByYear).length > 0) {
      results.push({ farContract, shifted: shiftedByYear, original: originalByYear });
    }
  }

  return results;
}
