export interface SeriesData {
  dates: string[];
  values: (number | null)[];
}

export interface SpreadResult {
  farContract: string;
  shifted: Record<string, SeriesData>;
  original: Record<string, SeriesData>;
}

export type ChartType = 'historical' | 'continuous' | 'monthly' | 'weekly' | 'individual';

export interface ButterflyResult {
  label: string;
  legs: [string, string, string];
  shifted: Record<string, SeriesData>;
  original: Record<string, SeriesData>;
}

export interface AppConfig {
  displayMonths: Record<string, string>;
  regularMonthSets: Record<string, string[]>;
  commonButterflies: Record<string, [string, string, string]>;
  yearRange: { min: number; max: number };
}
