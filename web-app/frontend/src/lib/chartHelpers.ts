import type { SpreadResult } from '../types';

export const YEAR_COLORS = [
  '#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b',
  '#e377c2', '#17becf', '#bcbd22', '#d62728', '#aec7e8',
  '#ffbb78', '#98df8a', '#c5b0d5', '#c49c94', '#f7b6d2',
];

export function getCurrentYear(shifted: Record<string, unknown>): string {
  const thisYear = new Date().getFullYear();
  if (String(thisYear + 1) in shifted) return String(thisYear + 1);
  return String(thisYear);
}

export function rollingMean(values: (number | null)[], window = 7): (number | null)[] {
  return values.map((_, i) => {
    const slice = values.slice(Math.max(0, i - window + 1), i + 1).filter((v): v is number => v !== null);
    if (slice.length < window) return null;
    return slice.reduce((a, b) => a + b, 0) / slice.length;
  });
}

export function computeMean(series: Record<string, { dates: string[]; values: (number | null)[] }>, excludeYear?: string): Map<string, number> {
  const byDate = new Map<string, number[]>();
  for (const [year, s] of Object.entries(series)) {
    if (year === excludeYear) continue;
    s.dates.forEach((d, i) => {
      const v = s.values[i];
      if (v !== null) {
        const arr = byDate.get(d) ?? [];
        arr.push(v);
        byDate.set(d, arr);
      }
    });
  }
  const result = new Map<string, number>();
  byDate.forEach((vals, d) => result.set(d, vals.reduce((a, b) => a + b, 0) / vals.length));
  return result;
}

export function computePercentile(series: Record<string, { dates: string[]; values: (number | null)[] }>, p: number, excludeYear?: string): Map<string, number> {
  const byDate = new Map<string, number[]>();
  for (const [year, s] of Object.entries(series)) {
    if (year === excludeYear) continue;
    s.dates.forEach((d, i) => {
      const v = s.values[i];
      if (v !== null) {
        const arr = byDate.get(d) ?? [];
        arr.push(v);
        byDate.set(d, arr);
      }
    });
  }
  const result = new Map<string, number>();
  byDate.forEach((vals, d) => {
    const sorted = [...vals].sort((a, b) => a - b);
    const idx = (p / 100) * (sorted.length - 1);
    const lo = Math.floor(idx);
    const hi = Math.ceil(idx);
    result.set(d, sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo));
  });
  return result;
}

export function getISOWeek(dateStr: string): number {
  const d = new Date(dateStr + 'T00:00:00');
  const jan4 = new Date(d.getFullYear(), 0, 4);
  const startOfWeek1 = new Date(jan4);
  startOfWeek1.setDate(jan4.getDate() - ((jan4.getDay() + 6) % 7));
  const diff = d.getTime() - startOfWeek1.getTime();
  return Math.floor(diff / (7 * 86400000)) + 1;
}

export function filterFarContracts(results: SpreadResult[], selected: string[]): SpreadResult[] {
  return results.filter(r => selected.includes(r.farContract[2]));
}

export const CHART_TABS = [
  { id: 'historical' as const, label: 'Historical' },
  { id: 'continuous' as const, label: 'Continuous' },
  { id: 'monthly' as const, label: 'Monthly Boxplot' },
  { id: 'weekly' as const, label: 'Weekly Boxplot' },
  { id: 'individual' as const, label: 'Individual' },
];
