import { loadData, toDateStr, RawData } from './dataManager';
import { MONTHS } from './utility';
import type { ButterflyResult, SeriesData } from './types';

// ── Helpers (mirrors controller.ts) ─────────────────────────────────────────

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
  const allDates = dateRange(
    new Date(sortedDates[0] + 'T00:00:00'),
    new Date(sortedDates[sortedDates.length - 1] + 'T00:00:00'),
  );
  const rawValues: (number | null)[] = allDates.map(d => series.get(d) ?? null);
  const filled = forwardFill(rawValues);
  const byDate = new Map<string, number | null>();
  allDates.forEach((d, i) => byDate.set(d, filled[i]));
  return { dates: allDates, values: filled, byDate };
}

// ── Year-rollover for butterfly legs ─────────────────────────────────────────
// Same logic as Python's create_contract_to_expiry_map.

function getExpiryYears(letters: [string, string, string], forYear: number): [number, number, number] {
  const m1 = MONTHS[letters[0]];
  const m2 = MONTHS[letters[1]];
  const m3 = MONTHS[letters[2]];
  let y1 = forYear, y2 = forYear, y3 = forYear;

  if (m3 < m1) y3 = forYear + 1;

  if (m2 < m1) {
    if (!(m3 > m1 || m3 < m2)) {
      throw new Error(`Invalid butterfly: 3rd leg must be later than the 2nd when 2nd wraps to next year.`);
    }
    y2 = forYear + 1;
  }

  return [y1, y2, y3];
}

// ── Main export ───────────────────────────────────────────────────────────────

export function calculateButterfly(
  combos: [string, string, string][],
  requestedYears: number[],
  dataFile?: string,
): ButterflyResult[] {
  const raw = loadData(dataFile);
  const today = new Date();
  const currentYear = today.getFullYear();
  const allYears = Array.from(new Set([...requestedYears, currentYear, currentYear + 1])).sort();

  const results: ButterflyResult[] = [];

  for (const letters of combos) {
    const label = letters.join('');
    const legs: [string, string, string] = [`LN${letters[0]}`, `LN${letters[1]}`, `LN${letters[2]}`];

    // Align all years to the first leg's contract start window for the current year
    const graphStart = getContractStartDate(letters[0], currentYear);

    const shiftedByYear: Record<string, SeriesData> = {};
    const originalByYear: Record<string, SeriesData> = {};

    for (const year of allYears) {
      let expiryYears: [number, number, number];
      try {
        expiryYears = getExpiryYears(letters, year);
      } catch {
        continue;
      }

      const xData = getContractData(raw, legs[0], expiryYears[0]);
      const yData = getContractData(raw, legs[1], expiryYears[1]);
      const zData = getContractData(raw, legs[2], expiryYears[2]);
      if (!xData || !yData || !zData) continue;

      // x - 2y + z on dates where all three have values
      const bfByDate = new Map<string, number>();
      for (const d of xData.dates) {
        const xv = xData.byDate.get(d);
        const yv = yData.byDate.get(d);
        const zv = zData.byDate.get(d);
        if (xv != null && yv != null && zv != null) {
          bfByDate.set(d, xv - 2 * yv + zv);
        }
      }
      if (bfByDate.size === 0) continue;

      const bfDates = Array.from(bfByDate.keys()).sort();
      const bfStart = new Date(bfDates[0] + 'T00:00:00');
      const bfEnd = new Date(bfDates[bfDates.length - 1] + 'T00:00:00');

      const contractStart = getContractStartDate(letters[0], year);
      const contractEnd = getContractExpiryDate(letters[0], year);
      const rangeStart = contractStart > bfStart ? contractStart : bfStart;
      const rangeEnd = contractEnd < bfEnd ? contractEnd : bfEnd;
      if (rangeStart > rangeEnd) continue;

      const fullRange = dateRange(rangeStart, rangeEnd);
      const reindexed = fullRange.map(d => bfByDate.get(d) ?? null);
      if (reindexed.every(v => v === null)) continue;

      // Store original (non-null points only)
      const origDates: string[] = [];
      const origValues: (number | null)[] = [];
      fullRange.forEach((d, i) => {
        if (reindexed[i] !== null) { origDates.push(d); origValues.push(reindexed[i]); }
      });
      originalByYear[String(year)] = { dates: origDates, values: origValues };

      // Shift dates so all years overlay on same x-axis window
      const anchor = new Date(year, graphStart.getMonth(), graphStart.getDate());
      const shiftAmount = -daysBetween(anchor, graphStart);
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
      results.push({ label, legs, shifted: shiftedByYear, original: originalByYear });
    }
  }

  return results;
}
